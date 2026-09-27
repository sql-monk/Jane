import { useEffect, useRef } from "react";
import { EditorView, basicSetup } from "codemirror";
import { EditorState, type Extension } from "@codemirror/state";
import { python } from "@codemirror/lang-python";
import { json } from "@codemirror/lang-json";

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
    const current = view.current;
    if (current && current.state.doc.toString() !== value) {
      current.dispatch({ changes: { from: 0, to: current.state.doc.length, insert: value } });
    }
  }, [value]);

  return <div className="code-editor" ref={host} data-testid={`editor-${label}`} />;
}
