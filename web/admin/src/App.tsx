import { useEffect, useRef, useState } from "react";
import { UnsavedChangesProvider, useUnsavedChanges } from "./components/UnsavedChanges";
import { NavLink, Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { Icon } from "./components/Icon";
import { ThemeControl } from "./components/ThemeControl";
import { NAV_GROUPS, navigationFor } from "./lib/navigation";
import { useAuth } from "./app/context";
import { LoginPage, OidcCallbackPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SourcesPage, SourcePage } from "./pages/SourcesPage";
import { TasksPage, TaskPage } from "./pages/TasksPage";
import { RunsPage, RunPage } from "./pages/RunsPage";
import { MaterialsPage, MaterialTracePage } from "./pages/MaterialsPage";
import { StoragesPage } from "./pages/StoragesPage";
import { ResultsPage } from "./pages/ResultsPage";
import { ProblemsPage } from "./pages/ProblemsPage";
import { PackagesPage, PackagePage } from "./pages/PackagesPage";
import { PackageEditorPage } from "./pages/PackageEditorPage";
import { RulesEditorPage } from "./pages/RulesEditorPage";
import { ConnectionsPage } from "./pages/ConnectionsPage";
import { LlmPage } from "./pages/LlmPage";
import { LimitsPage } from "./pages/LimitsPage";
import { AssistantPage } from "./pages/AssistantPage";
import { AuditPage } from "./pages/AuditPage";
import { ModulesPage, ModulePage } from "./pages/ModulesPage";
import { MonitoringPage } from "./pages/MonitoringPage";

function Layout() {
  const auth = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [search, setSearch] = useState("");
  const guard = useUnsavedChanges({ dirty: false });
  const menuButton = useRef<HTMLButtonElement>(null);
  const menuSearch = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!menuOpen) return;
    menuSearch.current?.focus();
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
        menuButton.current?.focus();
      }
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [menuOpen]);
  const active = navigationFor(location.pathname);
  return (
    <div className={menuOpen ? "layout menu-open" : "layout"}>
      <a className="skip-link" href="#main-content">
        До вмісту
      </a>
      <nav id="main-navigation" className="sidebar" aria-label="Розділи">
        <NavLink className="brand" to="/" onClick={() => setMenuOpen(false)}>
          <span className="brand-mark">j</span>
          <span>
            Jane<small>Платформа збору даних</small>
          </span>
        </NavLink>
        <label className="nav-search">
          <Icon name="search" />
          <input
            aria-label="Знайти розділ"
            ref={menuSearch}
            placeholder="Знайти розділ…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <div className="nav-groups">
          {NAV_GROUPS.map((group) => {
            const items = group.items.filter((item) =>
              `${group.label} ${item.label} ${item.description}`
                .toLocaleLowerCase("uk")
                .includes(search.toLocaleLowerCase("uk")),
            );
            return items.length ? (
              <div className="nav-group" key={group.label}>
                <div className="nav-group-label">{group.label}</div>
                {items.map(({ to, label, icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === "/"}
                    className={({ isActive }) => (isActive ? "nav nav-active" : "nav")}
                    onClick={() => setMenuOpen(false)}
                  >
                    <Icon name={icon} />
                    <span>{label}</span>
                  </NavLink>
                ))}
              </div>
            ) : null;
          })}
          {search &&
          !NAV_GROUPS.some((group) =>
            group.items.some((item) =>
              `${group.label} ${item.label} ${item.description}`
                .toLocaleLowerCase("uk")
                .includes(search.toLocaleLowerCase("uk")),
            ),
          ) ? (
            <p className="muted">Розділ не знайдено</p>
          ) : null}
        </div>
        <div className="sidebar-foot">
          <div className="workspace-label">
            <span className="workspace-avatar">J</span>
            <span>
              Робочий простір
              <small>{auth.principal ?? (auth.mode === "none" ? "Локальний режим" : "Адміністратор")}</small>
            </span>
          </div>
          {auth.mode !== "none" ? (
            <button type="button" className="btn btn-small" onClick={() => guard.confirmChange(auth.logout)}>
              Вийти
            </button>
          ) : null}
        </div>
      </nav>
      <div className="workspace">
        <header className="topbar">
          <div className="topbar-path">
            <button
              type="button"
              className="btn menu-toggle"
              ref={menuButton}
              aria-label={menuOpen ? "Закрити меню" : "Відкрити меню"}
              aria-expanded={menuOpen}
              aria-controls="main-navigation"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <Icon name={menuOpen ? "close" : "menu"} />
            </button>
            <span className="muted">Робочий простір</span>
            <span className="muted">/</span>
            <strong>{active?.label ?? "Jane"}</strong>
          </div>
          <div className="topbar-actions">
            <NavLink className="assistant-shortcut" to="/assistant">
              <Icon name="assistant" />
              Асистент
            </NavLink>
            <ThemeControl />
          </div>
        </header>
        <main
          className={`content${location.pathname.startsWith("/materials") || location.pathname === "/storages" ? " storage-workspace" : ""}`}
          id="main-content"
          tabIndex={-1}
        >
          {auth.expired ? (
            <div className="error-box" role="alert">
              Сесія недійсна або прострочена (401). <NavLink to="/login">Увійти знову</NavLink>
            </div>
          ) : null}
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function RequireAuth() {
  const auth = useAuth();
  const location = useLocation();
  if (!auth.authenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Layout />;
}

export function App() {
  return (
    <UnsavedChangesProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<OidcCallbackPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/monitoring" element={<MonitoringPage />} />
          <Route path="/modules" element={<ModulesPage />} />
          <Route path="/modules/:moduleId" element={<ModulePage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/sources/new" element={<SourcePage />} />
          <Route path="/sources/:sourceId" element={<SourcePage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/tasks/new" element={<TaskPage />} />
          <Route path="/tasks/:taskId" element={<TaskPage />} />
          <Route path="/runs" element={<RunsPage />} />
          <Route path="/runs/:runId" element={<RunPage />} />
          <Route path="/materials" element={<MaterialsPage />} />
          <Route path="/storages" element={<StoragesPage />} />
          <Route path="/materials/:materialId/trace" element={<MaterialTracePage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/problems" element={<ProblemsPage />} />
          <Route path="/packages" element={<PackagesPage />} />
          <Route path="/packages/:packageId" element={<PackagePage />} />
          <Route path="/packages/:packageId/versions/:version/edit" element={<PackageEditorPage />} />
          <Route path="/packages/:packageId/versions/:version/rules" element={<RulesEditorPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/llm" element={<LlmPage />} />
          <Route path="/limits" element={<LimitsPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="*" element={<p>Сторінку не знайдено</p>} />
        </Route>
      </Routes>
    </UnsavedChangesProvider>
  );
}
