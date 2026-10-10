import { useEffect, useRef } from "react";
import { EditorView, basicSetup } from "codemirror";
import { Compartment, EditorState, type Extension } from "@codemirror/state";
import { python } from "@codemirror/lang-python";
import { json } from "@codemirror/lang-json";
import { useTheme } from "../app/theme";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { tags } from "@lezer/highlight";

function editorTheme(dark: boolean): Extension {
  return [
    EditorView.theme(
      {
        "&": { color: "var(--text)", backgroundColor: "var(--panel)" },
        ".cm-content": { caretColor: "var(--accent)" },
        ".cm-cursor, .cm-dropCursor": { borderLeftColor: "var(--accent)" },
        ".cm-gutters": {
          backgroundColor: "var(--surface)",
          color: "var(--muted)",
          borderColor: "var(--border)",
        },
        ".cm-activeLine, .cm-activeLineGutter": {
          backgroundColor: "color-mix(in srgb, var(--accent) 8%, transparent)",
        },
        ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": {
          backgroundColor: "color-mix(in srgb, var(--accent) 22%, var(--panel))",
        },
        ".cm-panels, .cm-tooltip": {
          backgroundColor: "var(--surface)",
          color: "var(--text)",
          borderColor: "var(--border)",
        },
      },
      { dark },
    ),
    syntaxHighlighting(
      HighlightStyle.define([
        { tag: tags.keyword, color: dark ? "#ff7b72" : "#cf222e" },
        { tag: [tags.string, tags.special(tags.string)], color: dark ? "#a5d6ff" : "#0a3069" },
        { tag: [tags.number, tags.bool, tags.null], color: dark ? "#79c0ff" : "#0550ae" },
        { tag: tags.comment, color: "var(--muted)", fontStyle: "italic" },
        { tag: [tags.function(tags.variableName), tags.propertyName], color: dark ? "#d2a8ff" : "#8250df" },
        { tag: [tags.typeName, tags.className], color: dark ? "#ffa657" : "#953800" },
        { tag: tags.invalid, color: "var(--bad)" },
      ]),
    ),
  ];
}

export type EditorLanguage = "python" | "json" | "text";

function languageFor(lang: EditorLanguage): Extension[] {
  if (lang === "python") return [python()];
  if (lang === "json") return [json()];
  return [];
}

export function languageOfPath(path: string): EditorLanguage {
  if (path.endsWith(".py")) return "python";
  if (path.endsWith(".json")) return "json";
  return "text";
}

/**
 * CodeMirror 6 editor. Uncontrolled inside, synchronised from `value` when it changes from outside
 * (e.g. another file is opened). `label` becomes the accessible name of the editing surface.
 */
export function CodeEditor({
  value,
  onChange,
  language,
  label,
  readOnly = false,
  minHeight = "16rem",
}: {
  value: string;
  onChange?: (value: string) => void;
  language: EditorLanguage;
  label: string;
  readOnly?: boolean;
  minHeight?: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const themeCompartment = useRef(new Compartment());
  const { theme } = useTheme();
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (!host.current) return;
    const created = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: value,
        extensions: [
          basicSetup,
          themeCompartment.current.of(editorTheme(theme === "dark")),
          ...languageFor(language),
          EditorState.readOnly.of(readOnly),
          EditorView.editable.of(!readOnly),
          EditorView.contentAttributes.of({ "aria-label": label }),
          EditorView.theme({ "&": { minHeight }, ".cm-scroller": { minHeight } }),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) onChangeRef.current?.(update.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = created;
    return () => {
      created.destroy();
      view.current = null;
    };
    // Recreate only when the language / mode changes; content is synchronised below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, readOnly, label, minHeight]);

  useEffect(() => {
    view.current?.dispatch({ effects: themeCompartment.current.reconfigure(editorTheme(theme === "dark")) });
  }, [theme]);

  useEffect(() => {
    const current = view.current;
    if (current && current.state.doc.toString() !== value) {
      current.dispatch({ changes: { from: 0, to: current.state.doc.length, insert: value } });
    }
  }, [value]);

  return <div className="code-editor" ref={host} data-testid={`editor-${label}`} />;
}
