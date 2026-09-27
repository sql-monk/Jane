import { NavLink, Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./app/context";
import { LoginPage, OidcCallbackPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SourcesPage, SourcePage } from "./pages/SourcesPage";
import { TasksPage, TaskPage } from "./pages/TasksPage";
import { RunsPage, RunPage } from "./pages/RunsPage";
import { MaterialsPage, MaterialTracePage } from "./pages/MaterialsPage";
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

const NAV: Array<[string, string]> = [
  ["/", "Огляд"],
  ["/sources", "Джерела"],
  ["/tasks", "Завдання"],
  ["/runs", "Запуски"],
  ["/materials", "Матеріали"],
  ["/results", "Результати"],
  ["/problems", "Проблеми"],
  ["/packages", "Пакети"],
  ["/assistant", "Асистент"],
  ["/connections", "Підключення"],
  ["/llm", "LLM"],
  ["/limits", "Ліміти"],
  ["/audit", "Аудит"],
];

function Layout() {
  const auth = useAuth();
  return (
    <div className="layout">
      <nav className="sidebar" aria-label="Розділи">
        <div className="brand">Jane</div>
        {NAV.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => (isActive ? "nav nav-active" : "nav")}
          >
            {label}
          </NavLink>
        ))}
        <div className="sidebar-foot">
          <span className="muted">{auth.principal ?? ""}</span>
          {auth.mode !== "none" ? (
            <button type="button" className="btn btn-small" onClick={auth.logout}>
              Вийти
            </button>
          ) : null}
        </div>
      </nav>
      <main className="content">
        {auth.expired ? (
          <div className="error-box" role="alert">
            Сесія недійсна або прострочена (401). <NavLink to="/login">Увійти знову</NavLink>
          </div>
        ) : null}
        <Outlet />
      </main>
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
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<OidcCallbackPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route path="/sources/new" element={<SourcePage />} />
        <Route path="/sources/:sourceId" element={<SourcePage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/tasks/new" element={<TaskPage />} />
        <Route path="/tasks/:taskId" element={<TaskPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/runs/:runId" element={<RunPage />} />
        <Route path="/materials" element={<MaterialsPage />} />
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
  );
}
