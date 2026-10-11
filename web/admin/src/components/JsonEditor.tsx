import { useMemo, useState } from "react";
import { CodeEditor } from "./CodeEditor";
import { schemaIssueLabel, validateAgainst, type SchemaIssue, type SchemaRef } from "../lib/schema";

export interface JsonCheck {
  value: unknown;
  parseError: string | null;
  issues: SchemaIssue[];
  ok: boolean;
}

export function checkJson(text: string, schema?: SchemaRef): JsonCheck {
  let value: unknown;
  try {
    value = text.trim() ? JSON.parse(text) : undefined;
  } catch {
    return {
      value: undefined,
      parseError: "Некоректний JSON: перевірте лапки, коми та парні дужки",
      issues: [],
      ok: false,
    };
  }
  const issues = schema && value !== undefined ? validateAgainst(schema, value) : [];
  return { value, parseError: null, issues, ok: issues.length === 0 };
}

/** JSON editor validated against a contract JSON Schema (early feedback; the service validates again). */
export function JsonEditor({
  text,
  onChange,
  schema,
  label,
  minHeight,
  readOnly = false,
}: {
  text: string;
  onChange: (text: string) => void;
  schema?: SchemaRef;
  label: string;
  minHeight?: string;
  readOnly?: boolean;
}) {
  const check = useMemo(() => checkJson(text, schema), [text, schema]);
  const [touched, setTouched] = useState(false);
  return (
    <div className="json-editor">
      <CodeEditor
        value={text}
        onChange={(next) => {
          setTouched(true);
          onChange(next);
        }}
        language="json"
        label={label}
        readOnly={readOnly}
        {...(minHeight ? { minHeight } : {})}
      />
      {touched && check.parseError ? (
        <p className="error-inline" role="alert">
          JSON: {check.parseError}
        </p>
      ) : null}
      {touched && check.issues.length ? (
        <ul className="error-inline" role="alert" aria-label={`Помилки схеми: ${label}`}>
          {check.issues.map((issue, i) => (
            <li key={i}>
              {schemaIssueLabel(issue)}
              <details>
                <summary>Технічні подробиці</summary>
                <code>{issue.technical ?? issue.pointer}</code>
              </details>
            </li>
          ))}
        </ul>
      ) : null}
      {schema && !check.parseError && !check.issues.length && text.trim() ? (
        <p className="ok-inline">Відповідає схемі контракту</p>
      ) : null}
    </div>
  );
}

export function toJsonText(value: unknown): string {
  return value === undefined ? "" : JSON.stringify(value, null, 2);
}
