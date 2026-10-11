import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { UNSAFE_NavigationContext, useLocation } from "react-router-dom";
import { ActionDialog, ErrorBox } from "./ui";

export interface UnsavedChangesOptions {
  dirty: boolean;
  label?: string;
  onSave?: () => Promise<boolean>;
  onDiscard?: () => void;
}

type Registration = UnsavedChangesOptions;
type Guard = {
  register: (id: string, entry: Registration) => void;
  unregister: (id: string) => void;
  markSaved: (id: string) => void;
  confirmChange: (action: () => void) => void;
};
const GuardContext = createContext<Guard | null>(null);

/** BrowserRouter-compatible protection for route changes, history and local editor contexts. */
export function UnsavedChangesProvider({ children }: { children: ReactNode }) {
  const { navigator } = useContext(UNSAFE_NavigationContext);
  const location = useLocation();
  const registrations = useRef(new Map<string, Registration>());
  const [pending, setPending] = useState<{ action: () => void; entries: Registration[] } | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [invalid, setInvalid] = useState(false);
  const bypass = useRef(false);
  const historyIndex = useRef<number | undefined>(window.history.state?.idx as number | undefined);
  const dirtyEntries = useCallback(
    () => [...registrations.current.values()].filter((entry) => entry.dirty),
    [],
  );
  const proceed = useCallback((action: () => void) => {
    bypass.current = true;
    try {
      action();
    } finally {
      bypass.current = false;
    }
  }, []);
  const confirmChange = useCallback(
    (action: () => void) => {
      const entries = dirtyEntries();
      if (bypass.current || !entries.length) {
        proceed(action);
        return;
      }
      setError(null);
      setInvalid(false);
      setPending({ action, entries });
    },
    [dirtyEntries, proceed],
  );
  const guard = useRef<Guard>(null);
  if (!guard.current)
    guard.current = {
      register: (id, entry) => {
        registrations.current.set(id, entry);
      },
      unregister: (id) => {
        registrations.current.delete(id);
      },
      markSaved: (id) => {
        const entry = registrations.current.get(id);
        if (entry) entry.dirty = false;
      },
      confirmChange,
    };

  useEffect(() => {
    const push = navigator.push.bind(navigator);
    const replace = navigator.replace.bind(navigator);
    const go = navigator.go.bind(navigator);
    navigator.push = (...args) => confirmChange(() => push(...args));
    navigator.replace = (...args) => confirmChange(() => replace(...args));
    navigator.go = (...args) => confirmChange(() => go(...args));
    // Native Back/Forward bypass navigator.go. Restore the previous history entry before
    // asking, so choosing Stay leaves both the URL and editor draft intact.
    let restoring = false;
    let allowPop = false;
    const pop = (event: PopStateEvent) => {
      const nextIndex = event.state?.idx as number | undefined;
      if (restoring) {
        restoring = false;
        event.stopImmediatePropagation();
        return;
      }
      if (allowPop || bypass.current || !dirtyEntries().length) {
        allowPop = false;
        historyIndex.current = nextIndex;
        return;
      }
      if (
        typeof historyIndex.current !== "number" ||
        typeof nextIndex !== "number" ||
        historyIndex.current === nextIndex
      )
        return;
      event.stopImmediatePropagation();
      const delta = nextIndex - historyIndex.current;
      restoring = true;
      go(-delta);
      confirmChange(() => {
        allowPop = true;
        go(delta);
      });
    };
    const unload = (event: BeforeUnloadEvent) => {
      if (!dirtyEntries().length) return;
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("popstate", pop, true);
    window.addEventListener("beforeunload", unload);
    const updateIndex = () => {
      historyIndex.current = window.history.state?.idx as number | undefined;
    };
    // Push/replace also update the entry index used by the native history guard.
    navigator.push = (...args) =>
      confirmChange(() => {
        push(...args);
        updateIndex();
      });
    navigator.replace = (...args) =>
      confirmChange(() => {
        replace(...args);
        updateIndex();
      });
    return () => {
      navigator.push = push;
      navigator.replace = replace;
      navigator.go = go;
      window.removeEventListener("popstate", pop, true);
      window.removeEventListener("beforeunload", unload);
    };
  }, [navigator, confirmChange, dirtyEntries]);

  useEffect(() => {
    historyIndex.current = window.history.state?.idx as number | undefined;
    setPending(null);
  }, [location.key]);
  const leave = () => {
    if (!pending) return;
    pending.entries.forEach((entry) => {
      entry.onDiscard?.();
      entry.dirty = false;
    });
    const action = pending.action;
    setPending(null);
    proceed(action);
  };
  const saveAndLeave = async () => {
    if (!pending) return;
    setSaving(true);
    setError(null);
    setInvalid(false);
    try {
      for (const entry of pending.entries) {
        if (!entry.onSave || !(await entry.onSave())) {
          setInvalid(true);
          return;
        }
        entry.dirty = false;
      }
      const action = pending.action;
      setPending(null);
      proceed(action);
    } catch (cause) {
      setError(cause);
    } finally {
      setSaving(false);
    }
  };
  return (
    <GuardContext.Provider value={guard.current}>
      {children}
      {pending ? (
        <ActionDialog
          title="Незбережені зміни"
          onClose={() => {
            if (!saving) setPending(null);
          }}
        >
          <p>
            Є незбережені зміни
            {pending.entries.length === 1 && pending.entries[0]?.label ? `: ${pending.entries[0].label}` : ""}
            . Збережіть їх або відкиньте перед переходом.
          </p>
          <ErrorBox error={error} title="Зміни не збережено" />
          {invalid ? (
            <p role="alert">
              Форма містить незаповнені або некоректні поля. Залиштеся на сторінці та виправте їх перед
              збереженням.
            </p>
          ) : null}
          <div className="button-row">
            <button
              type="button"
              className="btn"
              disabled={saving}
              autoFocus
              onClick={() => setPending(null)}
            >
              Залишитися
            </button>
            <button type="button" className="btn btn-danger" disabled={saving} onClick={leave}>
              Відкинути й перейти
            </button>
            {pending.entries.every((entry) => entry.onSave) ? (
              <button
                type="button"
                className="btn btn-primary"
                disabled={saving}
                onClick={() => void saveAndLeave()}
              >
                {saving ? "Збереження…" : "Зберегти й перейти"}
              </button>
            ) : null}
          </div>
        </ActionDialog>
      ) : null}
    </GuardContext.Provider>
  );
}

export function useUnsavedChanges(options: UnsavedChangesOptions) {
  const guard = useContext(GuardContext);
  const id = useId();
  useEffect(() => {
    guard?.register(id, { ...options });
  }, [guard, id, options]);
  useEffect(
    () => () => {
      guard?.unregister(id);
    },
    [guard, id],
  );
  return {
    confirmChange: (action: () => void) => {
      if (guard) guard.confirmChange(action);
      else action();
    },
    markSaved: () => guard?.markSaved(id),
  };
}

/** Protect a parent tab/context which unmounts a dirty child form. */
export function useConfirmUnsavedChange() {
  const guard = useContext(GuardContext);
  return (action: () => void) => {
    if (guard) guard.confirmChange(action);
    else action();
  };
}
