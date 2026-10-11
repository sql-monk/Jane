import { useCallback, useEffect, useState } from "react";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { Source, Stage } from "../api/types";
import { Link } from "react-router-dom";
import { removeStage, renameStage, type JsonValue } from "../lib/property";
import { checkJson, JsonEditor, toJsonText } from "./JsonEditor";
import { DagView } from "./DagView";
import { PropertyGrid, PropertyIssuesContext, PropertyDraftsBlockedContext } from "./PropertyGrid";
import { ErrorBox, Field, JsonView, LoadMore } from "./ui";
import { ConnectionPicker } from "./ConnectionPicker";
import { conditionPropertyChoices, stagePropertyChoices } from "../lib/property-help";
import { useStagePropertyHelp } from "./useStagePropertyHelp";
import "../chain-editor.css";

export function ChainEditor({
  text,
  onChange,
  requireCollect = true,
  onValidityChange,
  source,
  readOnly = false,
}: {
  text: string;
  onChange: (text: string) => void;
  requireCollect?: boolean;
  onValidityChange?: (valid: boolean) => void;
  source?: Source | undefined;
  readOnly?: boolean;
}) {
  const parsed = checkJson(text);
  const valid =
    Array.isArray(parsed.value) &&
    parsed.value.every(
      (s) =>
        s &&
        typeof s === "object" &&
        typeof s.stage_id === "string" &&
        ["collect", "handler"].includes(s.kind) &&
        (s.inputs === undefined ||
          (Array.isArray(s.inputs) &&
            s.inputs.every(
              (i: unknown) => i && typeof i === "object" && "from" in i && typeof i.from === "string",
            ))),
    );
  const stages = valid ? (parsed.value as Stage[]) : [];
  const [selected, setSelected] = useState<string | null>(null);
  const [raw, setRaw] = useState(false);
  const [error, setError] = useState("");
  const [propertyIssues, setPropertyIssues] = useState<Record<string, string>>({});
  const [editReset, setEditReset] = useState(0);
  const hasDraftIssues = Boolean(error) || Object.keys(propertyIssues).length > 0;
  const blocked = hasDraftIssues || readOnly;
  const reportIssue = useCallback(
    (key: string, issue: string) =>
      setPropertyIssues((previous) => {
        if ((previous[key] ?? "") === issue) return previous;
        const next = { ...previous };
        if (issue) next[key] = issue;
        else delete next[key];
        return next;
      }),
    [],
  );
  useEffect(
    () => onValidityChange?.(!error && Object.keys(propertyIssues).length === 0),
    [error, propertyIssues, onValidityChange],
  );
  const stage = stages.find((s) => s.stage_id === selected) ?? stages[0];
  const update = (next: Stage[]) => {
    const nextText = toJsonText(next);
    if (nextText !== text) onChange(nextText);
  };
  const patch = (next: Stage) => update(stages.map((s) => (s.stage_id === stage?.stage_id ? next : s)));
  return (
    <PropertyIssuesContext.Provider value={reportIssue}>
      <PropertyDraftsBlockedContext.Provider value={blocked}>
        <div className="chain-editor">
          <div className="button-row">
            <button type="button" className="btn" disabled={blocked} onClick={() => setRaw(!raw)}>
              {raw ? "Візуальний редактор" : "Редагувати JSON"}
            </button>
            <button
              type="button"
              className="btn"
              disabled={!valid || blocked}
              onClick={() => {
                let id = `stage-${stages.length + 1}`;
                while (stages.some((s) => s.stage_id === id)) id += "-new";
                update([
                  ...stages,
                  {
                    stage_id: id,
                    kind: "handler",
                    handler: { package_id: "", version: "" },
                    params: {},
                    inputs: stage ? [{ from: stage.stage_id }] : [],
                  },
                ]);
                setSelected(id);
              }}
            >
              Додати етап-обробник
            </button>
            <button
              type="button"
              className="btn"
              disabled={!valid || blocked || stages.some((s) => s.kind === "collect")}
              onClick={() => {
                let id = "collect";
                while (stages.some((s) => s.stage_id === id)) id += "-new";
                update([{ stage_id: id, kind: "collect", collector: { collector: "web" } }, ...stages]);
                setSelected(id);
              }}
            >
              Додати збір
            </button>
          </div>
          {raw ? (
            <JsonEditor
              text={text}
              onChange={onChange}
              label="Етапи завдання"
              minHeight="20rem"
              readOnly={readOnly}
            />
          ) : valid ? (
            <>
              <DagView
                stages={stages}
                selected={stage?.stage_id ?? ""}
                onSelect={(id) => {
                  if (!blocked) setSelected(id);
                }}
                requireCollect={requireCollect}
              />
              <div className="chain-layout">
                <nav aria-label="Етапи">
                  {stages.map((s) => (
                    <button
                      className="btn"
                      type="button"
                      key={s.stage_id}
                      aria-pressed={s === stage}
                      disabled={blocked}
                      onClick={() => {
                        if (!blocked) setSelected(s.stage_id);
                      }}
                    >
                      {s.stage_id}
                    </button>
                  ))}
                </nav>
                {stage ? (
                  <section aria-label="Вибраний етап">
                    <h3>{stage.stage_id}</h3>
                    <div className="chain-stage-identity">
                      <Field
                        label="Ідентифікатор етапу"
                        hint="Унікальна назва етапу. При перейменуванні зв’язки оновлюються автоматично."
                      >
                        <input
                          key={`identity-${stage.stage_id}-${editReset}`}
                          defaultValue={stage.stage_id}
                          disabled={Object.keys(propertyIssues).length > 0}
                          onBlur={(e) => {
                            try {
                              update(renameStage(stages, stage.stage_id, e.target.value));
                              setSelected(e.target.value);
                              setError("");
                            } catch (err) {
                              setError((err as Error).message);
                              e.target.value = stage.stage_id;
                            }
                          }}
                        />
                      </Field>
                      <button
                        type="button"
                        className="btn btn-danger"
                        disabled={blocked}
                        onClick={() => {
                          update(removeStage(stages, stage.stage_id));
                          setSelected(null);
                        }}
                      >
                        Видалити етап і його зв’язки
                      </button>
                    </div>
                    <fieldset className="chain-package-fields" disabled={blocked}>
                      <ChainPackagePicker
                        key={stage.stage_id}
                        stage={stage}
                        source={source}
                        onChange={patch}
                      />
                    </fieldset>
                    {stage.kind === "handler" ? (
                      <ChainLinks
                        key={`links-${stage.stage_id}-${editReset}`}
                        stage={stage}
                        stages={stages}
                        onChange={patch}
                        blocked={blocked}
                      />
                    ) : null}
                    <h4>Властивості етапу</h4>
                    <p className="muted">Типи JSON зберігаються. Помилки схеми показано перед збереженням.</p>
                    <StagePropertyGrid
                      key={`properties-${stage.stage_id}-${editReset}`}
                      stage={stage}
                      onChange={patch}
                    />
                  </section>
                ) : (
                  <p>Додайте етап.</p>
                )}
              </div>
            </>
          ) : (
            <p role="alert">
              JSON етапів некоректний. Відкрийте JSON-режим для виправлення; текст збережено.
            </p>
          )}
          {error ? <p role="alert">{error}</p> : null}
          {hasDraftIssues ? (
            <div role="alert">
              <p>Є незавершені поля. Виправте їх перед зміною етапу, режиму чи збереженням.</p>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  setEditReset((v) => v + 1);
                  setPropertyIssues({});
                  setError("");
                }}
              >
                Відкинути незбережені поля
              </button>
            </div>
          ) : null}
        </div>
      </PropertyDraftsBlockedContext.Provider>
    </PropertyIssuesContext.Provider>
  );
}

function StagePropertyGrid({ stage, onChange }: { stage: Stage; onChange: (stage: Stage) => void }) {
  const help = useStagePropertyHelp(stage);
  return (
    <>
      {help.loading ? (
        <p className="muted" role="status">
          Завантажуємо описи параметрів…
        </p>
      ) : null}
      {help.error ? <p className="muted">Описи параметрів пакета наразі недоступні.</p> : null}
      <PropertyGrid
        objectRoot
        describe={help.describe}
        choices={(_path, keys) => stagePropertyChoices(stage, keys, help.schema)}
        renderValue={(path, keys, value, setValue) =>
          keys[0] === "connections" && keys.length === 2 && typeof value === "string" ? (
            <ConnectionPicker label={`Значення ${path}`} value={value} onChange={setValue} />
          ) : null
        }
        value={
          Object.fromEntries(
            Object.entries(stage)
              .filter(([k]) => !["stage_id", "kind", "inputs", "handler"].includes(k))
              .map(([key, value]) => [
                key,
                key === "collector" && value
                  ? Object.fromEntries(Object.entries(value).filter(([name]) => name !== "rules"))
                  : value,
              ]),
          ) as JsonValue
        }
        onChange={(v) => {
          if (v && typeof v === "object" && !Array.isArray(v))
            onChange({
              ...v,
              stage_id: stage.stage_id,
              kind: stage.kind,
              ...(stage.handler ? { handler: stage.handler } : {}),
              ...(stage.collector?.rules &&
              v["collector"] &&
              typeof v["collector"] === "object" &&
              !Array.isArray(v["collector"])
                ? { collector: { ...v["collector"], rules: stage.collector.rules } }
                : {}),
              ...(stage.inputs ? { inputs: stage.inputs } : {}),
            } as Stage);
        }}
      />
      <details className="form-advanced">
        <summary>Технічні властивості пакета (лише перегляд)</summary>
        <p className="muted">
          Пакет і версію змінюйте у полях над властивостями. Дайджест фіксує конкретний вміст пакета.
        </p>
        <JsonView value={stage.kind === "handler" ? stage.handler : stage.collector?.rules} compact />
      </details>
    </>
  );
}

export function ChainPackagePicker({
  stage,
  source,
  inherit = true,
  onChange,
}: {
  stage: Stage;
  source?: Source | undefined;
  inherit?: boolean;
  onChange: (stage: Stage) => void;
}) {
  const api = useApi();
  const ref = stage.kind === "handler" ? stage.handler : stage.collector?.rules;
  const packages = useCursorList(["chain-packages", stage.kind], (cursor, limit) =>
    unwrap(
      api.registry.GET("/v1/packages", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(stage.kind === "collect" ? { kind: "collector-rules" as const } : {}),
          },
        },
      }),
    ),
  );
  const packageId = ref?.package_id ?? "";
  const versions = useCursorList(["chain-versions", packageId], (cursor, limit) =>
    packageId
      ? unwrap(
          api.registry.GET("/v1/packages/{package_id}/versions", {
            params: { path: { package_id: packageId }, query: { limit, ...(cursor ? { cursor } : {}) } },
          }),
        )
      : Promise.resolve({ items: [], next_cursor: null }),
  );
  const setRef = (next: { package_id: string; version: string }) => {
    if (!next.package_id && stage.kind === "collect") {
      const collector = { ...stage.collector! };
      delete collector.rules;
      onChange({ ...stage, collector });
      return;
    }
    onChange(
      stage.kind === "handler"
        ? { ...stage, handler: next }
        : { ...stage, collector: { ...stage.collector!, rules: next } },
    );
  };
  return (
    <div className="grid-2">
      <Field
        label={stage.kind === "collect" ? "Пакет правил" : "Пакет обробника"}
        hint={
          stage.kind === "collect"
            ? inherit
              ? "Правила збору. Можна використати правила джерела або задати пакет етапу."
              : "Пакет правил, за яким колектор обходить це джерело."
            : "Пакет, який обробляє вхідні матеріали або зберігає результат."
        }
      >
        <select value={packageId} onChange={(e) => setRef({ package_id: e.target.value, version: "" })}>
          <option value="">
            {stage.kind === "collect" && inherit ? "Правила джерела" : "Виберіть пакет"}
          </option>
          {packageId && !packages.items.some((p) => p.package_id === packageId) ? (
            <option>{packageId}</option>
          ) : null}
          {packages.items
            .filter((p) => stage.kind === "collect" || p.kind !== "collector-rules")
            .map((p) => (
              <option key={p.package_id} value={p.package_id}>
                {p.title} ({p.package_id})
              </option>
            ))}
        </select>
        <LoadMore hasMore={packages.hasMore} loading={packages.loadingMore} onClick={packages.loadMore} />
      </Field>
      <Field label="Версія пакета" hint="Точна версія вибраного пакета для цього етапу.">
        <select
          disabled={!packageId}
          value={ref?.version ?? ""}
          onChange={(e) => setRef({ package_id: packageId, version: e.target.value })}
        >
          <option value="">
            {stage.kind === "collect" && inherit && !packageId && source?.collector_rules
              ? `Із джерела: ${source.collector_rules.version}`
              : "Виберіть версію"}
          </option>
          {ref?.version && !versions.items.some((v) => v.version === ref.version) ? (
            <option>{ref.version}</option>
          ) : null}
          {versions.items.map((v) => (
            <option key={v.version}>{v.version}</option>
          ))}
        </select>
        <LoadMore hasMore={versions.hasMore} loading={versions.loadingMore} onClick={versions.loadMore} />
      </Field>
      <ErrorBox error={packages.error ?? versions.error} />
      {stage.kind === "collect" && inherit && !packageId ? (
        <p className="muted">
          {source?.collector_rules ? (
            <>
              Правила з джерела{" "}
              <Link to={`/sources/${encodeURIComponent(source.source_id)}`}>{source.title}</Link>:{" "}
              <strong>
                {source.collector_rules.package_id}@{source.collector_rules.version}
              </strong>
              .
            </>
          ) : (
            "Успадковані правила ще не вибрані. Виберіть джерело з правилами або задайте пакет для цього етапу."
          )}
        </p>
      ) : null}
    </div>
  );
}

function ChainLinks({
  stage,
  stages,
  onChange,
  blocked = false,
}: {
  stage: Stage;
  stages: Stage[];
  onChange: (stage: Stage) => void;
  blocked?: boolean;
}) {
  const [from, setFrom] = useState("");
  const inputs = stage.inputs ?? [];
  return (
    <section aria-label="Вхідні зв’язки">
      <h4>Вхідні зв’язки</h4>
      {inputs.map((input, i) => (
        <div key={`${i}-${input.from}`} className="chain-link">
          <strong>
            {input.from} → {stage.stage_id}
          </strong>
          <Field label={`Вихід зв’язку ${i + 1}`}>
            <select
              disabled={blocked}
              value={input.select ?? "output"}
              onChange={(e) =>
                onChange({
                  ...stage,
                  inputs: inputs.map((v, j) =>
                    j === i ? { ...v, select: e.target.value as NonNullable<typeof input.select> } : v,
                  ),
                })
              }
            >
              {!(
                stages.find((s) => s.stage_id === input.from)?.kind === "collect"
                  ? ["output", "unmatched_materials"]
                  : ["output", "input_material", "problems"]
              ).includes(input.select ?? "output") ? (
                <option value={input.select}>Недопустимий: {input.select}</option>
              ) : null}
              {(stages.find((s) => s.stage_id === input.from)?.kind === "collect"
                ? ["output", "unmatched_materials"]
                : ["output", "input_material", "problems"]
              ).map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </Field>
          <button
            disabled={blocked}
            type="button"
            className="btn"
            onClick={() => onChange({ ...stage, inputs: inputs.filter((_, j) => j !== i) })}
          >
            Видалити зв’язок {i + 1}
          </button>
          {input.when ? (
            <>
              <PropertyGrid
                label={`Умова зв’язку ${i + 1}`}
                choices={(_path, keys) => conditionPropertyChoices(keys)}
                value={input.when as JsonValue}
                onChange={(v) =>
                  onChange({
                    ...stage,
                    inputs: inputs.map((item, j) =>
                      j === i ? { ...item, when: v as NonNullable<typeof input.when> } : item,
                    ),
                  })
                }
              />
              <button
                disabled={blocked}
                type="button"
                className="btn"
                onClick={() =>
                  onChange({
                    ...stage,
                    inputs: inputs.map((item, j) => {
                      if (i !== j) return item;
                      const next = { ...item };
                      delete next.when;
                      return next;
                    }),
                  })
                }
              >
                Прибрати умову {i + 1}
              </button>
            </>
          ) : (
            <button
              disabled={blocked}
              type="button"
              className="btn"
              onClick={() =>
                onChange({
                  ...stage,
                  inputs: inputs.map((item, j) =>
                    j === i
                      ? { ...item, when: { field: "result.status", op: "eq", value: "success" } }
                      : item,
                  ),
                })
              }
            >
              Додати умову {i + 1}
            </button>
          )}
        </div>
      ))}
      <Field label="З’єднати з етапом">
        <select disabled={blocked} value={from} onChange={(e) => setFrom(e.target.value)}>
          <option value="">—</option>
          {stages
            .filter((s) => s.stage_id !== stage.stage_id)
            .map((s) => (
              <option key={s.stage_id}>{s.stage_id}</option>
            ))}
        </select>
      </Field>
      <button
        type="button"
        className="btn"
        disabled={blocked || !stages.some((s) => s.stage_id === from) || from === stage.stage_id}
        onClick={() => {
          onChange({ ...stage, inputs: [...inputs, { from }] });
          setFrom("");
        }}
      >
        Додати зв’язок
      </button>
    </section>
  );
}
