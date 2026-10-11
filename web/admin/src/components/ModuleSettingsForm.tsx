import { useEffect, useState } from "react";
import { useBeforeUnload } from "react-router-dom";
import { fieldGroup, fieldLabel, type ModuleConfiguration, type ModuleField } from "../lib/modules";
import { ErrorBox, Notice } from "./ui";

function FieldControl({
  field,
  value,
  onChange,
}: {
  field: ModuleField;
  value: string | number | boolean;
  onChange: (value: string | number | boolean) => void;
}) {
  const label = fieldLabel(field.path);
  if (field.choices)
    return (
      <select
        aria-label={label}
        value={String(value)}
        onChange={(event) =>
          onChange(
            field.choices?.find((choice) => String(choice) === event.target.value) ?? event.target.value,
          )
        }
      >
        {field.choices.map((choice) => (
          <option key={String(choice)} value={String(choice)}>
            {String(choice)}
          </option>
        ))}
      </select>
    );
  if (field.type === "boolean")
    return (
      <input
        aria-label={label}
        type="checkbox"
        checked={Boolean(value)}
        onChange={(event) => onChange(event.target.checked)}
      />
    );
  return (
    <input
      aria-label={label}
      type={field.type === "number" ? "number" : "text"}
      value={String(value)}
      required
      min={
        field.minimum ??
        (field.exclusive_minimum !== undefined
          ? field.exclusive_minimum + (field.integer ? 1 : 0.000001)
          : undefined)
      }
      max={field.maximum}
      step={field.integer ? 1 : "any"}
      onChange={(event) =>
        onChange(
          field.type === "number"
            ? event.target.value === ""
              ? ""
              : Number(event.target.value)
            : event.target.value,
        )
      }
    />
  );
}

export function ModuleSettingsForm({
  configuration,
  save,
  pending,
  error,
}: {
  configuration: ModuleConfiguration;
  save: (values: ModuleConfiguration["overrides"]) => void;
  pending: boolean;
  error: unknown;
}) {
  const [values, setValues] = useState(configuration.overrides);
  const [search, setSearch] = useState("");
  const dirty = JSON.stringify(values) !== JSON.stringify(configuration.overrides);
  useBeforeUnload((event) => {
    if (dirty) event.preventDefault();
  });
  useEffect(() => {
    if (!dirty) return;
    const guard = (event: MouseEvent) => {
      const anchor = (event.target as HTMLElement).closest("a[href],button[role=tab]");
      if (
        anchor &&
        anchor.getAttribute("aria-selected") !== "true" &&
        !window.confirm("Є незбережені налаштування. Залишити сторінку?")
      ) {
        event.preventDefault();
        event.stopPropagation();
      }
    };
    document.addEventListener("click", guard, true);
    return () => document.removeEventListener("click", guard, true);
  }, [dirty]);
  const groups = new Map<string, ModuleField[]>();
  for (const field of configuration.fields) {
    if (
      search &&
      !`${fieldLabel(field.path)} ${field.description ?? ""}`
        .toLocaleLowerCase("uk")
        .includes(search.toLocaleLowerCase("uk"))
    )
      continue;
    const group = fieldGroup(field.path);
    groups.set(group, [...(groups.get(group) ?? []), field]);
  }
  return (
    <form
      className="module-settings"
      onSubmit={(event) => {
        event.preventDefault();
        save(values);
      }}
    >
      <Notice>
        Збережені зміни застосуються після перезапуску цього модуля. Поточні запуски продовжують
        використовувати активні значення.
      </Notice>
      {configuration.pending_restart ? (
        <Notice tone="warn">Є збережені зміни, що очікують перезапуску.</Notice>
      ) : null}
      <label className="module-filter">
        Знайти налаштування
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Паралельність, час очікування…"
        />
      </label>
      {[...groups].map(([group, fields], index) => (
        <details className="module-setting-group" key={group} open={Boolean(search) || index < 2}>
          <summary>
            {group}
            <span>{fields.length}</span>
          </summary>
          {fields.map((field) => (
            <div className="module-setting-row" key={field.path}>
              <div>
                <strong>{fieldLabel(field.path)}</strong>
                {field.description ? <p>{field.description}</p> : null}
                <small>
                  Активне: {String(field.value)} ·{" "}
                  {field.origin === "module" ? "Налаштовано для модуля" : "Початкова конфігурація"}
                  {field.maximum !== undefined ? ` · Максимум: ${field.maximum}` : ""}
                </small>
              </div>
              <div className="module-setting-control">
                <FieldControl
                  field={field}
                  value={values[field.path] ?? field.inherited_value ?? field.value}
                  onChange={(value) => setValues({ ...values, [field.path]: value })}
                />
                {Object.hasOwn(values, field.path) ? (
                  <button
                    type="button"
                    className="btn btn-small"
                    onClick={() => {
                      const next = { ...values };
                      delete next[field.path];
                      setValues(next);
                    }}
                  >
                    Успадкувати
                  </button>
                ) : null}
                {Object.hasOwn(values, field.path) && values[field.path] !== field.value ? (
                  <small className="muted">Після перезапуску</small>
                ) : null}
              </div>
            </div>
          ))}
        </details>
      ))}
      {!groups.size ? <p className="muted">Налаштувань за цим запитом немає.</p> : null}
      <div className="module-save">
        <button type="submit" className="btn btn-primary" disabled={!dirty || pending}>
          {pending ? "Збереження…" : "Зберегти налаштування"}
        </button>
        {dirty ? <span className="muted">Є незбережені зміни</span> : null}
      </div>
      <ErrorBox error={error} title="Налаштування не збережено" />
    </form>
  );
}
