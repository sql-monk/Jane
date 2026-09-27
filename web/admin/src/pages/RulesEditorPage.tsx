// Collector rules (package kind=collector-rules): crawl strategies of a source, combinable (ТЗ §6, §13.1.1).
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import {
  fetchAllFiles,
  fetchPackageFile,
  nextManifest,
  publishVersion,
  type PackageFile,
} from "../api/packages";
import type { PackageManifest, PackageRef } from "../api/types";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { ErrorBox, Field, JsonView, Loading, Notice, Page, Section, Table } from "../components/ui";
import { SCHEMAS, validateAgainst } from "../lib/schema";
import { SEMVER_PATTERN, bumpVersion } from "../lib/format";

type Json = Record<string, unknown>;

/** Templates for every strategy type of collector-rules.schema.json#/$defs/Strategy (required fields only). */
export const STRATEGY_TEMPLATES: Record<string, Json> = {
  seed_list: { type: "seed_list", urls: ["https://example.test/"] },
  recursive: { type: "recursive", seeds: ["https://example.test/"], follow: [{ value: "example.test/**" }] },
  sitemap: { type: "sitemap", use_robots_txt: true },
  feed: { type: "feed", autodiscover: true },
  listing: {
    type: "listing",
    start_urls: ["https://example.test/catalog"],
    next_page: { type: "rel", value: "next" },
  },
  url_template: {
    type: "url_template",
    template: "https://example.test/item/{id}",
    variables: { id: { range: { start: 1, end: 100 } } },
  },
  api_feed: {
    type: "api_feed",
    url: "https://example.test/api/items",
    items_path: "$.items",
    url_path: "$.url",
  },
  llm_explore: { type: "llm_explore", goal: "find product pages" },
};

export const STRATEGY_LABELS: Record<string, string> = {
  seed_list: "Явний перелік URL",
  recursive: "Рекурсивний обхід посилань",
  sitemap: "Sitemap / Sitemap Index",
  feed: "RSS / Atom",
  listing: "Категорії, пагінація, пошук",
  url_template: "Шаблон URL",
  api_feed: "API / JSON-канал",
  llm_explore: "Дослідження за допомогою LLM",
};

function rulesPath(manifest: PackageManifest | undefined): string | null {
  const entry = manifest?.entry as { rules?: string } | undefined;
  return entry?.rules ?? null;
}

function useRules(ref: PackageRef) {
  const api = useApi();
  return useQuery({
    queryKey: ["rules", ref.package_id, ref.version],
    queryFn: async () => {
      const version = await unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
          params: { path: { package_id: ref.package_id, version: ref.version } },
        }),
      );
      const path = rulesPath(version.manifest);
      if (!path) return { version, path: null, rules: null as Json | null, raw: "" };
      const file = await fetchPackageFile(api, ref.package_id, ref.version, path);
      let rules: Json | null;
      try {
        rules = JSON.parse(file.data) as Json;
      } catch {
        rules = null;
      }
      return { version, path, rules, raw: file.data };
    },
  });
}

/** Read-only summary of the strategies a source uses (source page). */
export function StrategiesSummary({ rules: ref }: { rules: PackageRef }) {
  const rules = useRules(ref);
  if (rules.isLoading) return <Loading />;
  if (rules.error) return <ErrorBox error={rules.error} />;
  const doc = rules.data?.rules;
  const strategies = Array.isArray(doc?.["strategies"]) ? (doc["strategies"] as Json[]) : [];
  return (
    <div>
      {doc ? (
        <Table
          label="Стратегії обходу"
          rows={strategies}
          rowKey={(s, i) => String(s["strategy_id"] ?? i)}
          empty="Правила без стратегій (наприклад Telegram)"
          columns={[
            { header: "Стратегія", cell: (s) => STRATEGY_LABELS[String(s["type"])] ?? String(s["type"]) },
            { header: "id", cell: (s) => String(s["strategy_id"] ?? "—") },
            { header: "Пріоритет", cell: (s) => String(s["priority"] ?? 0) },
          ]}
        />
      ) : (
        <p className="muted">Файл правил не є JSON або не вказаний у маніфесті.</p>
      )}
      <Link
        className="btn"
        to={`/packages/${encodeURIComponent(ref.package_id)}/versions/${encodeURIComponent(ref.version)}/rules`}
      >
        Редагувати стратегії
      </Link>
    </div>
  );
}

export function RulesEditorPage() {
  const { packageId = "", version = "" } = useParams();
  const api = useApi();
  const navigate = useNavigate();
  const rules = useRules({ package_id: packageId, version });
  const [strategyTexts, setStrategyTexts] = useState<string[]>([]);
  const [restText, setRestText] = useState("");
  const [newVersion, setNewVersion] = useState("");
  const [summary, setSummary] = useState("");
  const [addType, setAddType] = useState("sitemap");

  useEffect(() => {
    const doc = rules.data?.rules;
    if (!doc) return;
    const { strategies, ...rest } = doc;
    setStrategyTexts(Array.isArray(strategies) ? strategies.map((s) => toJsonText(s)) : []);
    setRestText(toJsonText(rest));
    setNewVersion(bumpVersion(version, "minor"));
  }, [rules.data, version]);

  const isWeb = rules.data?.rules?.["collector"] === "web";

  const assembled = useMemo(() => {
    const rest = checkJson(restText);
    const strategies = strategyTexts.map((t) => checkJson(t, SCHEMAS.strategy));
    if (rest.parseError || strategies.some((s) => s.parseError))
      return { doc: null, issues: ["JSON містить синтаксичні помилки"] };
    const doc: Json = { ...((rest.value as Json | undefined) ?? {}) };
    if (isWeb || strategies.length) doc["strategies"] = strategies.map((s) => s.value);
    const issues = validateAgainst(SCHEMAS.collectorRules, doc).map((i) => `${i.pointer} ${i.message}`);
    return { doc, issues };
  }, [restText, strategyTexts, isWeb]);

  const publish = useMutation({
    mutationFn: async () => {
      const current = rules.data;
      if (!current?.version.manifest || !current.path || !assembled.doc)
        throw new Error("rules are not loaded");
      const files: Record<string, PackageFile> = await fetchAllFiles(api, current.version);
      files[current.path] = { encoding: "utf-8", data: `${JSON.stringify(assembled.doc, null, 2)}\n` };
      return publishVersion(
        api,
        packageId,
        nextManifest(current.version.manifest, newVersion, summary),
        files,
      );
    },
    onSuccess: (published) =>
      navigate(`/packages/${encodeURIComponent(packageId)}?version=${encodeURIComponent(published.version)}`),
  });

  if (rules.isLoading) return <Loading />;

  const typeCounts = strategyTexts.map((t) =>
    String((checkJson(t).value as Json | undefined)?.["type"] ?? "?"),
  );

  return (
    <Page title={`Правила колектора ${packageId}@${version}`}>
      <ErrorBox error={rules.error} />
      {rules.data && !rules.data.rules ? (
        <Notice tone="warn">Файл правил відсутній або не є JSON.</Notice>
      ) : null}
      <Notice>
        Зміни зберігаються як нова незмінна версія пакета (статус draft). Її можна протестувати, погодити й
        активувати для джерела чи етапу збору; попередня версія лишається для відкату.
      </Notice>
      {isWeb ? (
        <Section
          title={`Стратегії обходу (${strategyTexts.length})`}
          actions={
            <span className="inline-form">
              <select
                aria-label="Тип нової стратегії"
                value={addType}
                onChange={(e) => setAddType(e.target.value)}
              >
                {Object.keys(STRATEGY_TEMPLATES).map((t) => (
                  <option key={t} value={t}>
                    {STRATEGY_LABELS[t]}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn"
                onClick={() =>
                  setStrategyTexts((list) => [
                    ...list,
                    toJsonText({
                      ...STRATEGY_TEMPLATES[addType],
                      strategy_id: `${addType.replace(/_/g, "-")}-${list.length + 1}`,
                    }),
                  ])
                }
              >
                Додати стратегію
              </button>
            </span>
          }
        >
          <p className="muted">
            Режими комбінуються: наприклад Sitemap дає початкові URL, а рекурсивний обхід знаходить пов'язані
            матеріали.
          </p>
          {strategyTexts.map((text, index) => (
            <div key={index} className="card" data-testid={`strategy-${index}`}>
              <div className="card-head">
                <strong>
                  {index + 1}. {STRATEGY_LABELS[typeCounts[index] ?? ""] ?? typeCounts[index]}
                </strong>
                <span>
                  <button
                    type="button"
                    className="btn btn-small"
                    disabled={index === 0}
                    onClick={() =>
                      setStrategyTexts((list) => {
                        const copy = [...list];
                        [copy[index - 1], copy[index]] = [copy[index] as string, copy[index - 1] as string];
                        return copy;
                      })
                    }
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    className="btn btn-small btn-danger"
                    onClick={() => setStrategyTexts((list) => list.filter((_, i) => i !== index))}
                  >
                    Видалити
                  </button>
                </span>
              </div>
              <JsonEditor
                text={text}
                onChange={(t) => setStrategyTexts((list) => list.map((old, i) => (i === index ? t : old)))}
                schema={SCHEMAS.strategy}
                label={`Стратегія ${index + 1}`}
                minHeight="6rem"
              />
            </div>
          ))}
        </Section>
      ) : null}
      <Section
        title={
          isWeb ? "Область обходу, robots.txt, нормалізація, дедуплікація, пріоритети, ліміти" : "Правила"
        }
      >
        <JsonEditor text={restText} onChange={setRestText} label="Інші правила" minHeight="12rem" />
      </Section>
      <Section title="Перевірка за схемою контракту">
        {assembled.issues.length ? (
          <ul className="error-inline" role="alert" aria-label="Помилки правил">
            {assembled.issues.map((i) => (
              <li key={i}>{i}</li>
            ))}
          </ul>
        ) : (
          <p className="ok-inline">Правила відповідають collector-rules.schema.json</p>
        )}
        {assembled.doc ? <JsonView value={assembled.doc} compact /> : null}
      </Section>
      <Section title="Опублікувати нову версію">
        <div className="grid-2">
          <Field label="Нова версія">
            <input value={newVersion} onChange={(e) => setNewVersion(e.target.value)} />
          </Field>
          <Field label="Опис змін">
            <input value={summary} onChange={(e) => setSummary(e.target.value)} maxLength={4000} />
          </Field>
        </div>
        <ErrorBox error={publish.error} title="Не вдалося опублікувати" />
        <button
          type="button"
          className="btn btn-primary"
          disabled={
            publish.isPending ||
            !assembled.doc ||
            assembled.issues.length > 0 ||
            !SEMVER_PATTERN.test(newVersion)
          }
          onClick={() => publish.mutate()}
        >
          Опублікувати версію правил
        </button>
      </Section>
    </Page>
  );
}
