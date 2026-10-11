import { createContext, Fragment, useContext, useEffect, useId, useState } from "react";
import { emptyValue, jsonType, moveItem, renameField, type JsonType, type JsonValue } from "../lib/property";

const TYPES: JsonType[] = ["string", "number", "boolean", "null", "object", "array"];
export const PropertyIssuesContext = createContext<(key: string, error: string) => void>(() => {});
export const PropertyDraftsBlockedContext = createContext(false);
export function PropertyGrid({
  value,
  onChange,
  label = "Властивості",
  objectRoot = false,
  describe,
}: {
  value: JsonValue;
  onChange: (value: JsonValue) => void;
  label?: string;
  objectRoot?: boolean;
  describe?: ((path: string, keys: readonly (string | number)[]) => string | undefined) | undefined;
}) {
  return (
    <div className="property-grid-wrap">
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
            keys={[]}
            prefix={label}
            value={value}
            onChange={onChange}
            depth={0}
            describe={describe}
            fixedType={objectRoot}
          />
        </tbody>
      </table>
    </div>
  );
}
function PropertyRow({
  name,
  path,
  keys,
  value,
  onChange,
  depth,
  onRename,
  onRemove,
  onMove,
  fixedType = false,
  prefix,
  visible = true,
  describe,
}: {
  name: string;
  path: string;
  keys: readonly (string | number)[];
  value: JsonValue;
  onChange: (value: JsonValue) => void;
  depth: number;
  onRename?: (name: string) => void;
  onRemove?: () => void;
  onMove?: (delta: number) => void;
  fixedType?: boolean;
  prefix: string;
  visible?: boolean;
  describe?: ((path: string, keys: readonly (string | number)[]) => string | undefined) | undefined;
}) {
  const [open, setOpen] = useState(true);
  const [error, setError] = useState("");
  const reportIssue = useContext(PropertyIssuesContext);
  const blocked = useContext(PropertyDraftsBlockedContext);
  const issueId = useId();
  useEffect(() => {
    reportIssue(issueId, error);
    return () => reportIssue(issueId, "");
  }, [reportIssue, issueId, error]);
  const description = describe?.(path, keys);
  const descriptionId = `${issueId}-description`;
  const type = jsonType(value);
  const container = type === "object" || type === "array";
  const object = type === "object" ? (value as Record<string, JsonValue>) : null;
  const array = type === "array" ? (value as JsonValue[]) : null;
  return (
    <Fragment>
      <tr hidden={!visible}>
        <td style={{ paddingLeft: `${Math.min(depth, 5) * 0.6 + 0.5}rem` }}>
          <div className="property-name-controls">
            {container ? (
              <button
                className="btn btn-small"
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
                aria-describedby={description ? descriptionId : undefined}
                aria-label={`Назва ${path}`}
                defaultValue={name}
                disabled={blocked && !error}
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
          </div>
          {description ? (
            <p id={descriptionId} className="property-description">
              {description}
            </p>
          ) : null}
        </td>
        <td>
          <select
            disabled={fixedType || blocked}
            aria-describedby={description ? descriptionId : undefined}
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
          <div className="property-value-controls">
            <div className="property-value">
              {type === "string" ? (
                <textarea
                  rows={1}
                  aria-describedby={description ? descriptionId : undefined}
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
                  aria-describedby={description ? descriptionId : undefined}
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
                  aria-describedby={description ? descriptionId : undefined}
                  aria-label={`Значення ${path}`}
                  checked={value as boolean}
                  onChange={(e) => onChange(e.target.checked)}
                />
              ) : null}
              {type === "null" ? <code>null</code> : null}
              {container ? (
                <span>{array ? `Елементи: ${array.length}` : `Поля: ${Object.keys(object!).length}`}</span>
              ) : null}
            </div>
            <div className="property-actions">
              {container ? (
                <button
                  className="btn btn-small"
                  type="button"
                  aria-label={`Додати ${path}`}
                  disabled={blocked}
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
              ) : null}
              {onMove ? (
                <>
                  <button
                    className="btn btn-small"
                    disabled={blocked}
                    type="button"
                    aria-label={`Вгору ${path}`}
                    onClick={() => onMove(-1)}
                  >
                    ↑
                  </button>
                  <button
                    className="btn btn-small"
                    disabled={blocked}
                    type="button"
                    aria-label={`Вниз ${path}`}
                    onClick={() => onMove(1)}
                  >
                    ↓
                  </button>
                </>
              ) : null}
              {onRemove ? (
                <button
                  className="btn btn-small"
                  disabled={blocked}
                  type="button"
                  aria-label={`Видалити ${path}`}
                  onClick={onRemove}
                >
                  ×
                </button>
              ) : null}
            </div>
          </div>
          {error ? <span role="alert">{error}</span> : null}
        </td>
      </tr>
      {object
        ? Object.entries(object).map(([key, item]) => (
            <PropertyRow
              prefix={prefix}
              describe={describe}
              visible={visible && open}
              key={key}
              name={key}
              path={`${path}.${key}`}
              keys={[...keys, key]}
              depth={depth + 1}
              value={item}
              onChange={(next) => onChange({ ...object, [key]: next })}
              onRename={(next) => onChange(renameField(object, key, next))}
              onRemove={() => onChange(Object.fromEntries(Object.entries(object).filter(([k]) => k !== key)))}
            />
          ))
        : null}
      {array
        ? array.map((item, index) => (
            <PropertyRow
              prefix={prefix}
              describe={describe}
              visible={visible && open}
              key={index}
              name={String(index)}
              path={`${path}[${index}]`}
              keys={[...keys, index]}
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
