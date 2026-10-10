import { createContext, Fragment, useContext, useEffect, useState } from "react";
import { emptyValue, jsonType, moveItem, renameField, type JsonType, type JsonValue } from "../lib/property";

const TYPES: JsonType[] = ["string", "number", "boolean", "null", "object", "array"];
export const PropertyIssuesContext = createContext<(key: string, error: string) => void>(() => {});
export function PropertyGrid({
  value,
  onChange,
  label = "Властивості",
  objectRoot = false,
}: {
  value: JsonValue;
  onChange: (value: JsonValue) => void;
  label?: string;
  objectRoot?: boolean;
}) {
  return (
    <table className="property-grid" aria-label={label}>
      <thead>
        <tr>
          <th>Назва</th>
          <th>Тип</th>
          <th>Значення</th>
        </tr>
      </thead>
      <tbody>
        <PropertyRow
          name="$"
          path="$"
          prefix={label}
          value={value}
          onChange={onChange}
          depth={0}
          fixedType={objectRoot}
        />
      </tbody>
    </table>
  );
}
function PropertyRow({
  name,
  path,
  value,
  onChange,
  depth,
  onRename,
  onRemove,
  onMove,
  fixedType = false,
  prefix,
}: {
  name: string;
  path: string;
  value: JsonValue;
  onChange: (value: JsonValue) => void;
  depth: number;
  onRename?: (name: string) => void;
  onRemove?: () => void;
  onMove?: (delta: number) => void;
  fixedType?: boolean;
  prefix: string;
}) {
  const [open, setOpen] = useState(true);
  const [error, setError] = useState("");
  const reportIssue = useContext(PropertyIssuesContext);
  useEffect(() => {
    reportIssue(`${prefix}:${path}`, error);
    return () => reportIssue(`${prefix}:${path}`, "");
  }, [reportIssue, prefix, path, error]);
  const type = jsonType(value);
  const container = type === "object" || type === "array";
  const object = type === "object" ? (value as Record<string, JsonValue>) : null;
  const array = type === "array" ? (value as JsonValue[]) : null;
  return (
    <Fragment>
      <tr>
        <td style={{ paddingLeft: `${depth + 0.5}rem` }}>
          {container ? (
            <button
              type="button"
              aria-label={`Розгорнути ${path}`}
              aria-expanded={open}
              onClick={() => setOpen(!open)}
            >
              {open ? "▾" : "▸"}
            </button>
          ) : null}
          {onRename ? (
            <input
              aria-label={`Назва ${path}`}
              defaultValue={name}
              onChange={() => setError("Завершіть редагування назви поля")}
              key={name}
              onBlur={(e) => {
                try {
                  onRename(e.target.value);
                  setError("");
                } catch (err) {
                  setError((err as Error).message);
                  e.target.value = name;
                }
              }}
            />
          ) : (
            <span>{name}</span>
          )}
        </td>
        <td>
          <select
            disabled={fixedType}
            aria-label={`Тип ${path}`}
            value={type}
            onChange={(e) => {
              setError("");
              onChange(emptyValue(e.target.value as JsonType));
            }}
          >
            {TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </td>
        <td>
          {type === "string" ? (
            <textarea
              rows={1}
              aria-label={`Значення ${path}`}
              value={value as string}
              onChange={(e) => onChange(e.target.value)}
            />
          ) : null}
          {type === "number" ? (
            <input
              type="number"
              onChange={(e) =>
                setError(
                  e.target.value !== "" && Number.isFinite(Number(e.target.value))
                    ? "Завершіть редагування числа"
                    : "Некоректне число; попереднє значення збережено",
                )
              }
              step="any"
              aria-label={`Значення ${path}`}
              defaultValue={value as number}
              key={`${path}-${value}`}
              onBlur={(e) => {
                if (e.target.value !== "" && Number.isFinite(Number(e.target.value))) {
                  onChange(Number(e.target.value));
                  setError("");
                } else setError("Некоректне число; попереднє значення збережено");
              }}
            />
          ) : null}
          {type === "boolean" ? (
            <input
              type="checkbox"
              aria-label={`Значення ${path}`}
              checked={value as boolean}
              onChange={(e) => onChange(e.target.checked)}
            />
          ) : null}
          {type === "null" ? <code>null</code> : null}
          {container ? (
            <>
              <span>{array ? `${array.length} елементів` : `${Object.keys(object!).length} полів`}</span>{" "}
              <button
                type="button"
                aria-label={`Додати ${path}`}
                onClick={() => {
                  if (array) onChange([...array, ""]);
                  else {
                    let key = "new_field";
                    let n = 1;
                    while (Object.hasOwn(object!, key)) key = `new_field_${n++}`;
                    onChange({ ...object, [key]: "" });
                  }
                }}
              >
                {array ? "+ Елемент" : "+ Поле"}
              </button>
            </>
          ) : null}
          {onMove ? (
            <>
              <button type="button" aria-label={`Вгору ${path}`} onClick={() => onMove(-1)}>
                ↑
              </button>
              <button type="button" aria-label={`Вниз ${path}`} onClick={() => onMove(1)}>
                ↓
              </button>
            </>
          ) : null}
          {onRemove ? (
            <button type="button" aria-label={`Видалити ${path}`} onClick={onRemove}>
              ×
            </button>
          ) : null}
          {error ? <span role="alert">{error}</span> : null}
        </td>
      </tr>
      {open && object
        ? Object.entries(object).map(([key, item]) => (
            <PropertyRow
              prefix={prefix}
              key={key}
              name={key}
              path={`${path}.${key}`}
              depth={depth + 1}
              value={item}
              onChange={(next) => onChange({ ...object, [key]: next })}
              onRename={(next) => onChange(renameField(object, key, next))}
              onRemove={() => onChange(Object.fromEntries(Object.entries(object).filter(([k]) => k !== key)))}
            />
          ))
        : null}
      {open && array
        ? array.map((item, index) => (
            <PropertyRow
              prefix={prefix}
              key={index}
              name={String(index)}
              path={`${path}[${index}]`}
              depth={depth + 1}
              value={item}
              onChange={(next) => onChange(array.map((v, i) => (i === index ? next : v)))}
              onRemove={() => onChange(array.filter((_, i) => i !== index))}
              onMove={(delta) => onChange(moveItem(array, index, delta))}
            />
          ))
        : null}
    </Fragment>
  );
}
