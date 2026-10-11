import { contractSchemas } from "../api/generated/schemas";
import { fieldLabel } from "../lib/modules";
import { describeSchemaPath } from "../lib/property-help";

type SchemaNode = {
  type?: string;
  minimum?: number;
  maximum?: number;
  exclusiveMinimum?: number;
  properties?: Record<string, SchemaNode>;
};
type LimitsDocument = {
  profile?: string;
  defaults?: Record<string, Record<string, number | boolean>>;
  hard_caps?: Record<string, Record<string, number | boolean>>;
};

export function PlatformLimitsForm({ text, onChange }: { text: string; onChange: (text: string) => void }) {
  let value: LimitsDocument;
  try {
    value = JSON.parse(text) as LimitsDocument;
  } catch {
    return (
      <p className="muted">Для форм потрібен коректний документ лімітів. Перевірте розширений редактор.</p>
    );
  }
  const schema = contractSchemas["common/limits.schema.json"] as unknown as SchemaNode;
  function change(
    section: "defaults" | "hard_caps",
    group: string,
    field: string,
    next: number | boolean | undefined,
  ) {
    const updated = structuredClone(value);
    updated[section] ??= {};
    updated[section][group] ??= {};
    if (next === undefined) delete updated[section][group][field];
    else updated[section][group][field] = next;
    if (!Object.keys(updated[section][group]).length) delete updated[section][group];
    onChange(JSON.stringify(updated, null, 2));
  }
  return (
    <div className="platform-limits-form">
      <label className="module-filter">
        Назва профілю
        <input
          aria-label="Назва профілю лімітів"
          value={value.profile ?? ""}
          onChange={(event) => {
            const updated = { ...value };
            if (event.target.value) updated.profile = event.target.value;
            else delete updated.profile;
            onChange(JSON.stringify(updated, null, 2));
          }}
        />
      </label>
      {(["defaults", "hard_caps"] as const).map((section) => (
        <details className="module-setting-group" key={section} open={section === "defaults"}>
          <summary>{fieldLabel(section)}</summary>
          {Object.entries(schema.properties ?? {}).map(([group, node]) => (
            <details className="module-setting-group" key={group}>
              <summary>{fieldLabel(group)}</summary>
              {Object.entries(node.properties ?? {})
                .filter(([, field]) => ["number", "integer", "boolean"].includes(field.type ?? ""))
                .map(([name, field]) => {
                  const current = value[section]?.[group]?.[name];
                  const label = `${fieldLabel(name)} · ${section === "defaults" ? "типове значення" : "жорстка межа"}`;
                  return (
                    <div className="module-setting-row" key={name}>
                      <div>
                        <strong>{fieldLabel(name)}</strong>
                        <p>
                          {describeSchemaPath(
                            contractSchemas["common/limits.schema.json"] ?? {},
                            `$.${group}.${name}`,
                          )}
                        </p>
                        <small>
                          {current === undefined
                            ? "Успадковується зі стандартної конфігурації"
                            : "Задано на рівні платформи"}
                        </small>
                      </div>
                      <div className="module-setting-control">
                        <label>
                          <input
                            type="checkbox"
                            aria-label={`Задати: ${label}`}
                            checked={current !== undefined}
                            onChange={(event) =>
                              change(
                                section,
                                group,
                                name,
                                event.target.checked
                                  ? field.type === "boolean"
                                    ? true
                                    : (field.minimum ?? 1)
                                  : undefined,
                              )
                            }
                          />{" "}
                          Задати
                        </label>
                        {current !== undefined ? (
                          field.type === "boolean" ? (
                            <label>
                              <input
                                type="checkbox"
                                aria-label={label}
                                checked={Boolean(current)}
                                onChange={(event) => change(section, group, name, event.target.checked)}
                              />{" "}
                              Увімкнено
                            </label>
                          ) : (
                            <input
                              aria-label={label}
                              type="number"
                              required
                              min={
                                field.minimum ??
                                (field.exclusiveMinimum !== undefined
                                  ? field.exclusiveMinimum + 0.000001
                                  : undefined)
                              }
                              max={field.maximum}
                              step={field.type === "integer" ? 1 : "any"}
                              value={Number(current)}
                              onChange={(event) => {
                                if (event.target.value !== "")
                                  change(section, group, name, Number(event.target.value));
                              }}
                            />
                          )
                        ) : null}
                      </div>
                    </div>
                  );
                })}
            </details>
          ))}
        </details>
      ))}
    </div>
  );
}
