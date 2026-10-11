import { useId, useState } from "react";
import { ErrorBox, Field, Loading } from "./ui";

export type EntityOption = { value: string; label: string; description?: string };
/** Searchable known entities; the identifier stays explicit and round-trips unchanged. */
export function EntityPicker({
  label,
  value,
  onChange,
  options,
  required = false,
  loading = false,
  error,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: EntityOption[];
  required?: boolean;
  loading?: boolean;
  error?: unknown;
}) {
  const id = useId();
  const [search, setSearch] = useState("");
  const filtered = options.filter((option) =>
    `${option.label} ${option.value} ${option.description ?? ""}`
      .toLocaleLowerCase("uk")
      .includes(search.toLocaleLowerCase("uk")),
  );
  const selected = options.find((option) => option.value === value);
  const searchLabel = `Пошук за назвою (${label.replace(/\s*\([^)]*\)/g, "").toLocaleLowerCase("uk")})`;
  return (
    <div className="entity-picker">
      <Field label={searchLabel}>
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Назва або ідентифікатор…"
        />
      </Field>
      <Field
        label={label}
        hint={
          selected
            ? `${selected.label}${selected.description ? ` — ${selected.description}` : ""}`
            : "Виберіть наявний об’єкт зі списку або введіть точний ідентифікатор."
        }
      >
        <input
          list={id}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required={required}
        />
        <datalist id={id}>
          {filtered.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
              {option.description ? ` — ${option.description}` : ""}
            </option>
          ))}
        </datalist>
      </Field>
      {search ? (
        <div className="entity-picker-options" role="group" aria-label={`Збіги: ${label}`}>
          {filtered.length ? (
            filtered.map((option) => (
              <button
                type="button"
                className="btn btn-small"
                key={option.value}
                onClick={() => {
                  onChange(option.value);
                  setSearch("");
                }}
              >
                {option.label} ({option.value})
              </button>
            ))
          ) : (
            <span className="muted">Збігів у завантажених об’єктах немає.</span>
          )}
        </div>
      ) : null}
      {loading ? <Loading /> : null}
      <ErrorBox error={error} />
    </div>
  );
}
