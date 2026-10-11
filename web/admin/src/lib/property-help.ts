import { contractSchemas } from "../api/generated/schemas";
import type { Stage } from "../api/types";

export type PropertySchema = Record<string, unknown>;
type SchemaDocuments = Record<string, PropertySchema>;
type Cursor = { node: PropertySchema; document: PropertySchema; documentPath: string };
type PathPart = string | number;

function record(value: unknown): PropertySchema | undefined {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as PropertySchema)
    : undefined;
}

function parts(path: string): PathPart[] | undefined {
  if (!path.startsWith("$")) return undefined;
  const result: PathPart[] = [];
  const pattern = /\.([^.[\]]+)|\[(\d+)\]/g;
  let position = 1;
  for (const match of path.slice(1).matchAll(pattern)) {
    if (match.index !== position - 1) return undefined;
    result.push(match[1] ?? Number(match[2]));
    position += match[0].length;
  }
  return position === path.length ? result : undefined;
}

function documentPath(base: string, reference: string): string {
  const result = base.split("/").slice(0, -1);
  for (const part of reference.split("/")) {
    if (part === "..") result.pop();
    else if (part && part !== ".") result.push(part);
  }
  return result.join("/");
}

function dereference(cursor: Cursor, documents: SchemaDocuments): Cursor | undefined {
  const seen = new Set<string>();
  let current = cursor;
  while (typeof current.node["$ref"] === "string") {
    const reference = current.node["$ref"];
    const marker = `${current.documentPath}:${reference}`;
    if (seen.has(marker)) return undefined;
    seen.add(marker);
    const [file = "", fragment = ""] = reference.split("#");
    const key = file ? documentPath(current.documentPath, file) : current.documentPath;
    const document = file ? documents[key] : current.document;
    if (!document || (fragment && !fragment.startsWith("/"))) return undefined;
    let target: unknown = document;
    for (const token of fragment.split("/").slice(1)) {
      const object = record(target);
      const name = token.replace(/~1/g, "/").replace(/~0/g, "~");
      target = object && Object.hasOwn(object, name) ? object[name] : undefined;
    }
    const node = record(target);
    if (!node) return undefined;
    const { $ref: _reference, ...siblings } = current.node;
    current = { node: { ...node, ...siblings }, document, documentPath: key };
  }
  return current;
}

function matchesDiscriminator(node: PropertySchema, value: unknown): boolean {
  const properties = record(node["properties"]);
  const object = record(value);
  if (!properties || !object) return true;
  return Object.entries(properties).every(([key, definition]) => {
    const field = record(definition);
    if (!field || !Object.hasOwn(object, key)) return true;
    if (Object.hasOwn(field, "const")) return field["const"] === object[key];
    return !Array.isArray(field["enum"]) || field["enum"].includes(object[key]);
  });
}

function candidates(
  cursor: Cursor,
  path: readonly PathPart[],
  value: unknown,
  documents: SchemaDocuments,
  seen = new Set<PropertySchema>(),
  discriminate = false,
): PropertySchema[] {
  if (seen.has(cursor.node)) return [];
  seen.add(cursor.node);
  const current = dereference(cursor, documents);
  if (!current || (discriminate && !matchesDiscriminator(current.node, value))) return [];
  if (!path.length) return [current.node];
  const [part, ...rest] = path;
  let child: PropertySchema | undefined;
  let childValue: unknown;
  if (typeof part === "number") {
    const tuple = current.node["prefixItems"];
    child = record(Array.isArray(tuple) ? tuple[part] : undefined) ?? record(current.node["items"]);
    childValue = Array.isArray(value) ? value[part] : undefined;
  } else if (part !== undefined) {
    const properties = record(current.node["properties"]);
    child = properties && Object.hasOwn(properties, part) ? record(properties[part]) : undefined;
    child ??= record(current.node["additionalProperties"]);
    const object = record(value);
    childValue = object && Object.hasOwn(object, part) ? object[part] : undefined;
  }
  const direct = child ? candidates({ ...current, node: child }, rest, childValue, documents) : [];
  if (direct.length) return direct;
  return ["allOf", "oneOf", "anyOf"].flatMap((keyword) => {
    const branches = current.node[keyword];
    return Array.isArray(branches)
      ? branches.flatMap((branch) => {
          const node = record(branch);
          return node
            ? candidates({ ...current, node }, path, value, documents, seen, keyword !== "allOf")
            : [];
        })
      : [];
  });
}

function metadata(
  node: PropertySchema,
  summary?: string,
  fallbackSummary?: string,
  note?: string,
): string | undefined {
  const description = summary ?? node["description"] ?? fallbackSummary ?? node["title"];
  const fragments = typeof description === "string" && description.trim() ? [description.trim()] : [];
  if (Array.isArray(node["enum"]))
    fragments.push(`Допустимі значення: ${node["enum"].map((value) => JSON.stringify(value)).join(", ")}.`);
  if (Object.hasOwn(node, "default")) fragments.push(`За замовчуванням: ${JSON.stringify(node["default"])}.`);
  if (note) fragments.push(note);
  return fragments.join(" ") || undefined;
}

/** Read metadata only: no validation or remote schema execution takes place here. */
export function describeSchemaPath(
  schema: PropertySchema,
  path: string,
  options: {
    root?: PropertySchema;
    documents?: SchemaDocuments;
    documentPath?: string;
    value?: unknown;
    summary?: string;
    fallbackSummary?: string;
    note?: string;
    keys?: readonly PathPart[];
  } = {},
): string | undefined {
  const tokens = options.keys ?? parts(path);
  if (!tokens) return undefined;
  const nodes = candidates(
    { node: schema, document: options.root ?? schema, documentPath: options.documentPath ?? "" },
    tokens,
    options.value,
    options.documents ?? {},
  );
  const descriptions = nodes.map((node) =>
    metadata(node, options.summary, options.fallbackSummary, options.note),
  );
  // Ambiguous alternatives must not claim the semantics of whichever branch happened to be first.
  return descriptions.length && descriptions.every((description) => description === descriptions[0])
    ? descriptions[0]
    : undefined;
}

const STAGE_SUMMARIES: Record<string, string> = {
  "$.stage_id": "Унікальне ім'я етапу, за яким інші етапи посилаються на його вихід.",
  "$.kind": "collect — збір матеріалів; handler — виконання пакета обробника.",
  "$.title": "Назва етапу для відображення.",
  "$.collector": "Налаштування етапу збору матеріалів.",
  "$.collector.collector": "Колектор, який виконує збір, наприклад web або telegram.",
  "$.collector.rules":
    "Зафіксована версія правил збору. Якщо поле відсутнє, використовуються правила джерела.",
  "$.collector.mode": "full — повний збір; incremental — продовжити від збереженого стану колектора.",
  "$.params": "Параметри вибраної версії пакета; їхню форму визначає схема пакета.",
  "$.connections": "Відповідність логічних імен підключень пакета ідентифікаторам підключень.",
  "$.inputs": "Зв'язки з попередніми етапами, які передають дані на цей етап.",
  "$.bindings":
    "Фільтри матеріалів для екстрактора. Достатньо збігу з однією прив'язкою; без прив'язок етап отримує весь вхід.",
  "$.limits": "Ліміти цього етапу перекривають успадковані значення в межах обмежень платформи.",
};

function stageSummary(path: string): string | undefined {
  const generic = path.replace(/\[\d+\]/g, "[]");
  const nested: Record<string, string> = {
    "$.inputs[].from": "Ідентифікатор попереднього етапу, з якого надходять дані.",
    "$.inputs[].select":
      "output — вихід; input_material — вхідний матеріал; problems — проблемні елементи; unmatched_materials — матеріали без прив'язки (за дозволеної передачі в LLM).",
    "$.inputs[].when": "Умова, за якої елемент переходить за цим зв'язком.",
    "$.bindings[].url_patterns": "Шаблони URL матеріалів, до яких застосовується цей етап.",
    "$.bindings[].url_patterns[].type": "Спосіб зіставлення URL: glob — шаблон; regex — регулярний вираз.",
    "$.bindings[].url_patterns[].value":
      "glob: * — у межах сегмента шляху, ** — вкладені шляхи; URL без схеми, наприклад shop.example.test/product/**. Для regex — регулярний вираз по всьому URL.",
    "$.bindings[].media_types": "Типи вмісту матеріалу для цієї прив'язки, наприклад text/html.",
    "$.bindings[].content_kinds": "Різновиди вмісту матеріалу для цієї прив'язки.",
  };
  return STAGE_SUMMARIES[path] ?? nested[generic];
}

// Built-in behavior is documented by storage/README.md and jane_storage/formats.py.
// This fallback applies only to the selected file-storage package and only to existing schema fields.
function fileStorageCopy(stage: Stage, keys: readonly PathPart[] | undefined) {
  if (stage.kind !== "handler" || stage.handler?.package_id !== "jane.storage-files" || !keys) return {};
  if (keys.length === 1 && keys[0] === "prefix")
    return { note: "Для перегляду цих матеріалів підключення сховища має використовувати той самий prefix." };
  if (keys.length === 1 && keys[0] === "format")
    return { fallbackSummary: "Формати збереження оригіналів і сутностей." };
  if (keys.length === 2 && keys[0] === "format" && keys[1] === "raw")
    return {
      fallbackSummary:
        "Формат оригіналу: original — байти як є; html — лише HTML; json — документ Material із вбудованим вмістом.",
    };
  if (keys.length === 2 && keys[0] === "format" && keys[1] === "entities")
    return { fallbackSummary: "Формат сутностей: json — JSON-документи; jsonl — історія як JSON Lines." };
  return {};
}
/** Params metadata comes from the selected schema; known built-ins may supply documented fallback copy. */
export function describeStageProperty(
  stage: Stage,
  path: string,
  paramsSchema?: PropertySchema,
  keys?: readonly PathPart[],
): string | undefined {
  if (
    keys
      ? keys[0] === "params" && keys.length > 1
      : path.startsWith("$.params.") || path.startsWith("$.params[")
  )
    return paramsSchema
      ? describeSchemaPath(paramsSchema, `$${path.slice("$.params".length)}`, {
          value: stage.params,
          ...fileStorageCopy(stage, keys ? keys.slice(1) : parts(path)?.slice(1)),
          ...(keys ? { keys: keys.slice(1) } : {}),
        })
      : undefined;
  const task = contractSchemas["task-config.schema.json"];
  if (!task) return undefined;
  const summary = stageSummary(path);
  return describeSchemaPath({ $ref: "#/$defs/Stage" }, path, {
    root: task,
    documents: contractSchemas,
    documentPath: "task-config.schema.json",
    value: stage,
    ...(summary ? { summary } : {}),
    ...(keys ? { keys } : {}),
  });
}
