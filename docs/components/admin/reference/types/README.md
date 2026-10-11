# Типи й члени: Admin UI

> Згенеровано `scripts/docs_reference.py` з [web/admin/src](../../../../../web/admin/src). Не редагуйте вручну.

Експортовані оголошення модулів `web/admin/src` (без тестів і згенерованих клієнтів `src/api/generated`, які відтворюють контракти — [довідник API](../../../../reference/api/README.md)). Сигнатури виведено компілятором TypeScript.

## Модулі

| Модуль | Експортів | Призначення |
|---|---|---|
| [`api.client`](api.client.md) | 7 |  |
| [`api.hooks`](api.hooks.md) | 4 |  |
| [`api.packages`](api.packages.md) | 7 |  |
| [`api.problem`](api.problem.md) | 5 |  |
| [`api.types`](api.types.md) | 63 |  |
| [`App`](App.md) | 1 |  |
| [`app.context`](app.context.md) | 5 |  |
| [`app.theme`](app.theme.md) | 5 |  |
| [`auth.oidc`](auth.oidc.md) | 1 |  |
| [`auth.session`](auth.session.md) | 3 |  |
| [`components.AttemptHistory`](components.AttemptHistory.md) | 1 |  |
| [`components.CodeEditor`](components.CodeEditor.md) | 3 |  |
| [`components.ConnectionPicker`](components.ConnectionPicker.md) | 1 |  |
| [`components.DagView`](components.DagView.md) | 1 |  |
| [`components.EffectiveLimitsView`](components.EffectiveLimitsView.md) | 2 |  |
| [`components.Icon`](components.Icon.md) | 2 |  |
| [`components.ImprovementResultView`](components.ImprovementResultView.md) | 2 |  |
| [`components.ImprovementRuns`](components.ImprovementRuns.md) | 2 |  |
| [`components.JobPanel`](components.JobPanel.md) | 2 |  |
| [`components.JsonEditor`](components.JsonEditor.md) | 4 |  |
| [`components.ReprocessForm`](components.ReprocessForm.md) | 2 |  |
| [`components.ScheduleEditor`](components.ScheduleEditor.md) | 1 |  |
| [`components.StageVersions`](components.StageVersions.md) | 1 |  |
| [`components.TaskQuickRun`](components.TaskQuickRun.md) | 1 |  |
| [`components.ThemeControl`](components.ThemeControl.md) | 1 |  |
| [`components.ui`](components.ui.md) | 15 |  |
| [`components.UnifiedDiff`](components.UnifiedDiff.md) | 1 | Renders a unified diff (from registry diffPackage or computed locally) with added/removed line colouring. |
| [`config`](config.md) | 9 |  |
| [`lib.dag`](lib.dag.md) | 5 |  |
| [`lib.format`](lib.format.md) | 8 |  |
| [`lib.navigation`](lib.navigation.md) | 2 |  |
| [`lib.schema`](lib.schema.md) | 4 |  |
| [`lib.secrets`](lib.secrets.md) | 7 |  |
| [`pages.AssistantPage`](pages.AssistantPage.md) | 2 |  |
| [`pages.AuditPage`](pages.AuditPage.md) | 1 |  |
| [`pages.ConnectionsPage`](pages.ConnectionsPage.md) | 1 |  |
| [`pages.DashboardPage`](pages.DashboardPage.md) | 1 |  |
| [`pages.LimitsPage`](pages.LimitsPage.md) | 1 |  |
| [`pages.LlmPage`](pages.LlmPage.md) | 1 |  |
| [`pages.LoginPage`](pages.LoginPage.md) | 2 |  |
| [`pages.MaterialsPage`](pages.MaterialsPage.md) | 2 |  |
| [`pages.PackageEditorPage`](pages.PackageEditorPage.md) | 1 |  |
| [`pages.PackagesPage`](pages.PackagesPage.md) | 3 |  |
| [`pages.ProblemsPage`](pages.ProblemsPage.md) | 1 |  |
| [`pages.ResultsPage`](pages.ResultsPage.md) | 1 |  |
| [`pages.RulesEditorPage`](pages.RulesEditorPage.md) | 4 |  |
| [`pages.RunsPage`](pages.RunsPage.md) | 2 |  |
| [`pages.SourcesPage`](pages.SourcesPage.md) | 2 |  |
| [`pages.TasksPage`](pages.TasksPage.md) | 2 |  |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`absoluteUrl`](config.md#функція-absoluteurl) | функція | `config` |
| [`AcceptanceResult`](api.types.md#тип-acceptanceresult) | тип | `api.types` |
| [`ActionDialog`](components.ui.md#компонент-actiondialog) | компонент | `components.ui` |
| [`Activation`](api.types.md#тип-activation) | тип | `api.types` |
| [`ActivationRequest`](api.types.md#тип-activationrequest) | тип | `api.types` |
| [`AdminConfig`](config.md#інтерфейс-adminconfig) | інтерфейс | `config` |
| [`ApiClients`](api.client.md#інтерфейс-apiclients) | інтерфейс | `api.client` |
| [`ApiError`](api.problem.md#клас-apierror) | клас | `api.problem` |
| [`App`](App.md#компонент-app) | компонент | `App` |
| [`AppProvider`](app.context.md#компонент-appprovider) | компонент | `app.context` |
| [`AssistantInfo`](api.types.md#тип-assistantinfo) | тип | `api.types` |
| [`AssistantPage`](pages.AssistantPage.md#компонент-assistantpage) | компонент | `pages.AssistantPage` |
| [`AttemptEvent`](api.types.md#тип-attemptevent) | тип | `api.types` |
| [`AttemptHistory`](components.AttemptHistory.md#компонент-attempthistory) | компонент | `components.AttemptHistory` |
| [`AuditEvent`](api.types.md#тип-auditevent) | тип | `api.types` |
| [`AuditPage`](pages.AuditPage.md#компонент-auditpage) | компонент | `pages.AuditPage` |
| [`AuthConfig`](config.md#тип-authconfig) | тип | `config` |
| [`AuthHooks`](api.client.md#інтерфейс-authhooks) | інтерфейс | `api.client` |
| [`AuthState`](app.context.md#інтерфейс-authstate) | інтерфейс | `app.context` |
| [`BudgetDefinition`](api.types.md#тип-budgetdefinition) | тип | `api.types` |
| [`buildDag`](lib.dag.md#функція-builddag) | функція | `lib.dag` |
| [`bumpVersion`](lib.format.md#функція-bumpversion) | функція | `lib.format` |
| [`checkJson`](components.JsonEditor.md#функція-checkjson) | функція | `components.JsonEditor` |
| [`clearApiKey`](auth.session.md#функція-clearapikey) | функція | `auth.session` |
| [`CodeEditor`](components.CodeEditor.md#компонент-codeeditor) | компонент | `components.CodeEditor` |
| [`CollectionErrors`](api.types.md#тип-collectionerrors) | тип | `api.types` |
| [`Column`](components.ui.md#інтерфейс-column) | інтерфейс | `components.ui` |
| [`Connection`](api.types.md#тип-connection) | тип | `api.types` |
| [`ConnectionPicker`](components.ConnectionPicker.md#компонент-connectionpicker) | компонент | `components.ConnectionPicker` |
| [`ConnectionsPage`](pages.ConnectionsPage.md#компонент-connectionspage) | компонент | `pages.ConnectionsPage` |
| [`ConnectionTestResult`](api.types.md#тип-connectiontestresult) | тип | `api.types` |
| [`createApiClients`](api.client.md#функція-createapiclients) | функція | `api.client` |
| [`createUserManager`](auth.oidc.md#функція-createusermanager) | функція | `auth.oidc` |
| [`Dag`](lib.dag.md#інтерфейс-dag) | інтерфейс | `lib.dag` |
| [`DagEdge`](lib.dag.md#інтерфейс-dagedge) | інтерфейс | `lib.dag` |
| [`DagNode`](lib.dag.md#інтерфейс-dagnode) | інтерфейс | `lib.dag` |
| [`DagView`](components.DagView.md#компонент-dagview) | компонент | `components.DagView` |
| [`DashboardPage`](pages.DashboardPage.md#компонент-dashboardpage) | компонент | `pages.DashboardPage` |
| [`decodeFile`](api.packages.md#функція-decodefile) | функція | `api.packages` |
| [`DEFAULT_CONFIG`](config.md#константа-default_config) | константа | `config` |
| [`DiffView`](pages.PackagesPage.md#компонент-diffview) | компонент | `pages.PackagesPage` |
| [`EditorLanguage`](components.CodeEditor.md#тип-editorlanguage) | тип | `components.CodeEditor` |
| [`EffectiveLimits`](api.types.md#тип-effectivelimits) | тип | `api.types` |
| [`EffectiveLimitsView`](components.EffectiveLimitsView.md#компонент-effectivelimitsview) | компонент | `components.EffectiveLimitsView` |
| [`EntityHistoryEntry`](api.types.md#тип-entityhistoryentry) | тип | `api.types` |
| [`EntityState`](api.types.md#тип-entitystate) | тип | `api.types` |
| [`ErrorBox`](components.ui.md#компонент-errorbox) | компонент | `components.ui` |
| [`errorMessage`](api.problem.md#функція-errormessage) | функція | `api.problem` |
| [`Executor`](api.types.md#тип-executor) | тип | `api.types` |
| [`fetchAllFiles`](api.packages.md#функція-fetchallfiles) | функція | `api.packages` |
| [`fetchPackageFile`](api.packages.md#функція-fetchpackagefile) | функція | `api.packages` |
| [`Field`](components.ui.md#компонент-field) | компонент | `components.ui` |
| [`flattenLimits`](components.EffectiveLimitsView.md#функція-flattenlimits) | функція | `components.EffectiveLimitsView` |
| [`ForkRequest`](api.types.md#тип-forkrequest) | тип | `api.types` |
| [`formatBytes`](lib.format.md#функція-formatbytes) | функція | `lib.format` |
| [`formatDate`](lib.format.md#функція-formatdate) | функція | `lib.format` |
| [`formatInstant`](lib.format.md#функція-formatinstant) | функція | `lib.format` |
| [`formatMoney`](lib.format.md#функція-formatmoney) | функція | `lib.format` |
| [`HandlerKind`](api.types.md#тип-handlerkind) | тип | `api.types` |
| [`Icon`](components.Icon.md#компонент-icon) | компонент | `components.Icon` |
| [`IconName`](components.Icon.md#тип-iconname) | тип | `components.Icon` |
| [`ifMatch`](api.client.md#функція-ifmatch) | функція | `api.client` |
| [`ImprovementProposal`](api.types.md#тип-improvementproposal) | тип | `api.types` |
| [`ImprovementRequest`](api.types.md#тип-improvementrequest) | тип | `api.types` |
| [`ImprovementResult`](api.types.md#тип-improvementresult) | тип | `api.types` |
| [`ImprovementResultView`](components.ImprovementResultView.md#компонент-improvementresultview) | компонент | `components.ImprovementResultView` |
| [`ImprovementRun`](api.types.md#тип-improvementrun) | тип | `api.types` |
| [`ImprovementRunFilter`](components.ImprovementRuns.md#інтерфейс-improvementrunfilter) | інтерфейс | `components.ImprovementRuns` |
| [`ImprovementRunList`](components.ImprovementRuns.md#компонент-improvementrunlist) | компонент | `components.ImprovementRuns` |
| [`initializeTheme`](app.theme.md#функція-initializetheme) | функція | `app.theme` |
| [`isSecretRef`](lib.secrets.md#функція-issecretref) | функція | `lib.secrets` |
| [`Job`](api.types.md#тип-job) | тип | `api.types` |
| [`JobPanel`](components.JobPanel.md#компонент-jobpanel) | компонент | `components.JobPanel` |
| [`JobStatus`](api.types.md#тип-jobstatus) | тип | `api.types` |
| [`JsonCheck`](components.JsonEditor.md#інтерфейс-jsoncheck) | інтерфейс | `components.JsonEditor` |
| [`JsonEditor`](components.JsonEditor.md#компонент-jsoneditor) | компонент | `components.JsonEditor` |
| [`JsonView`](components.ui.md#компонент-jsonview) | компонент | `components.ui` |
| [`KeyValue`](components.ui.md#компонент-keyvalue) | компонент | `components.ui` |
| [`languageOfPath`](components.CodeEditor.md#функція-languageofpath) | функція | `components.CodeEditor` |
| [`Limits`](api.types.md#тип-limits) | тип | `api.types` |
| [`LimitsPage`](pages.LimitsPage.md#компонент-limitspage) | компонент | `pages.LimitsPage` |
| [`LlmPage`](pages.LlmPage.md#компонент-llmpage) | компонент | `pages.LlmPage` |
| [`loadConfig`](config.md#функція-loadconfig) | функція | `config` |
| [`Loading`](components.ui.md#компонент-loading) | компонент | `components.ui` |
| [`LoadMore`](components.ui.md#компонент-loadmore) | компонент | `components.ui` |
| [`LoginPage`](pages.LoginPage.md#компонент-loginpage) | компонент | `pages.LoginPage` |
| [`looksLikeSecretKey`](lib.secrets.md#функція-lookslikesecretkey) | функція | `lib.secrets` |
| [`looksLikeSecretValue`](lib.secrets.md#функція-lookslikesecretvalue) | функція | `lib.secrets` |
| [`MANIFEST_FILE`](api.packages.md#константа-manifest_file) | константа | `api.packages` |
| [`MaterialsPage`](pages.MaterialsPage.md#компонент-materialspage) | компонент | `pages.MaterialsPage` |
| [`MaterialTrace`](api.types.md#тип-materialtrace) | тип | `api.types` |
| [`MaterialTracePage`](pages.MaterialsPage.md#компонент-materialtracepage) | компонент | `pages.MaterialsPage` |
| [`ModelAlias`](api.types.md#тип-modelalias) | тип | `api.types` |
| [`Money`](api.types.md#тип-money) | тип | `api.types` |
| [`NAV_GROUPS`](lib.navigation.md#константа-nav_groups) | константа | `lib.navigation` |
| [`navigationFor`](lib.navigation.md#функція-navigationfor) | функція | `lib.navigation` |
| [`newIdempotencyKey`](api.client.md#функція-newidempotencykey) | функція | `api.client` |
| [`nextManifest`](api.packages.md#функція-nextmanifest) | функція | `api.packages` |
| [`Notice`](components.ui.md#компонент-notice) | компонент | `components.ui` |
| [`OidcCallbackPage`](pages.LoginPage.md#компонент-oidccallbackpage) | компонент | `pages.LoginPage` |
| [`OnboardingRequest`](api.types.md#тип-onboardingrequest) | тип | `api.types` |
| [`OnboardingSession`](api.types.md#тип-onboardingsession) | тип | `api.types` |
| [`OnboardingSessionSummary`](api.types.md#тип-onboardingsessionsummary) | тип | `api.types` |
| [`OnboardingStatus`](api.types.md#тип-onboardingstatus) | тип | `api.types` |
| [`Package`](api.types.md#тип-package) | тип | `api.types` |
| [`PackageDiff`](api.types.md#тип-packagediff) | тип | `api.types` |
| [`PackageEditorPage`](pages.PackageEditorPage.md#компонент-packageeditorpage) | компонент | `pages.PackageEditorPage` |
| [`PackageFile`](api.packages.md#інтерфейс-packagefile) | інтерфейс | `api.packages` |
| [`PackageManifest`](api.types.md#тип-packagemanifest) | тип | `api.types` |
| [`PackagePage`](pages.PackagesPage.md#компонент-packagepage) | компонент | `pages.PackagesPage` |
| [`PackageRef`](api.types.md#тип-packageref) | тип | `api.types` |
| [`PackagesPage`](pages.PackagesPage.md#компонент-packagespage) | компонент | `pages.PackagesPage` |
| [`PackageVersion`](api.types.md#тип-packageversion) | тип | `api.types` |
| [`Page`](components.ui.md#компонент-page) | компонент | `components.ui` |
| [`parseConfig`](config.md#функція-parseconfig) | функція | `config` |
| [`PlatformConnection`](api.types.md#тип-platformconnection) | тип | `api.types` |
| [`PlatformLimits`](api.types.md#тип-platformlimits) | тип | `api.types` |
| [`pollDelay`](api.hooks.md#функція-polldelay) | функція | `api.hooks` |
| [`PollingConfig`](config.md#інтерфейс-pollingconfig) | інтерфейс | `config` |
| [`Problem`](api.problem.md#тип-problem) | тип | `api.problem` |
| [`ProblemGroup`](api.types.md#тип-problemgroup) | тип | `api.types` |
| [`ProblemGroupStatus`](api.types.md#тип-problemgroupstatus) | тип | `api.types` |
| [`ProblemsPage`](pages.ProblemsPage.md#компонент-problemspage) | компонент | `pages.ProblemsPage` |
| [`Proposal`](api.types.md#тип-proposal) | тип | `api.types` |
| [`ProposalView`](components.ImprovementResultView.md#компонент-proposalview) | компонент | `components.ImprovementResultView` |
| [`Provider`](api.types.md#тип-provider) | тип | `api.types` |
| [`PublishRequest`](api.types.md#тип-publishrequest) | тип | `api.types` |
| [`publishVersion`](api.packages.md#функція-publishversion) | функція | `api.packages` |
| [`readApiKey`](auth.session.md#функція-readapikey) | функція | `auth.session` |
| [`ReasonAction`](components.ui.md#компонент-reasonaction) | компонент | `components.ui` |
| [`redactSecrets`](lib.secrets.md#функція-redactsecrets) | функція | `lib.secrets` |
| [`refLabel`](lib.format.md#функція-reflabel) | функція | `lib.format` |
| [`ReprocessForm`](components.ReprocessForm.md#компонент-reprocessform) | компонент | `components.ReprocessForm` |
| [`ReprocessRequest`](api.types.md#тип-reprocessrequest) | тип | `api.types` |
| [`ResultsPage`](pages.ResultsPage.md#компонент-resultspage) | компонент | `pages.ResultsPage` |
| [`RulesEditorPage`](pages.RulesEditorPage.md#компонент-ruleseditorpage) | компонент | `pages.RulesEditorPage` |
| [`Run`](api.types.md#тип-run) | тип | `api.types` |
| [`RunPage`](pages.RunsPage.md#компонент-runpage) | компонент | `pages.RunsPage` |
| [`RunRequest`](api.types.md#тип-runrequest) | тип | `api.types` |
| [`RunsPage`](pages.RunsPage.md#компонент-runspage) | компонент | `pages.RunsPage` |
| [`safeProblemCode`](api.problem.md#функція-safeproblemcode) | функція | `api.problem` |
| [`Schedule`](api.types.md#тип-schedule) | тип | `api.types` |
| [`ScheduleEditor`](components.ScheduleEditor.md#компонент-scheduleeditor) | компонент | `components.ScheduleEditor` |
| [`SchemaIssue`](lib.schema.md#інтерфейс-schemaissue) | інтерфейс | `lib.schema` |
| [`SchemaRef`](lib.schema.md#тип-schemaref) | тип | `lib.schema` |
| [`SCHEMAS`](lib.schema.md#константа-schemas) | константа | `lib.schema` |
| [`SECRET_MASK`](lib.secrets.md#константа-secret_mask) | константа | `lib.secrets` |
| [`SECRET_REF_PATTERN`](lib.secrets.md#константа-secret_ref_pattern) | константа | `lib.secrets` |
| [`Section`](components.ui.md#компонент-section) | компонент | `components.ui` |
| [`SEMVER_PATTERN`](lib.format.md#константа-semver_pattern) | константа | `lib.format` |
| [`serviceBaseUrl`](config.md#функція-servicebaseurl) | функція | `config` |
| [`ServiceKey`](config.md#тип-servicekey) | тип | `config` |
| [`sessionIdFromJob`](pages.AssistantPage.md#функція-sessionidfromjob) | функція | `pages.AssistantPage` |
| [`setTheme`](app.theme.md#функція-settheme) | функція | `app.theme` |
| [`SLUG_PATTERN`](lib.format.md#константа-slug_pattern) | константа | `lib.format` |
| [`Source`](api.types.md#тип-source) | тип | `api.types` |
| [`SourcePage`](pages.SourcesPage.md#компонент-sourcepage) | компонент | `pages.SourcesPage` |
| [`SourcesPage`](pages.SourcesPage.md#компонент-sourcespage) | компонент | `pages.SourcesPage` |
| [`Stage`](api.types.md#тип-stage) | тип | `api.types` |
| [`StageItem`](api.types.md#тип-stageitem) | тип | `api.types` |
| [`stageLabel`](lib.dag.md#функція-stagelabel) | функція | `lib.dag` |
| [`StageVersions`](components.StageVersions.md#компонент-stageversions) | компонент | `components.StageVersions` |
| [`Status`](components.ui.md#компонент-status) | компонент | `components.ui` |
| [`StatusChange`](api.types.md#тип-statuschange) | тип | `api.types` |
| [`StoredObject`](api.types.md#тип-storedobject) | тип | `api.types` |
| [`StoredObjectDetail`](api.types.md#тип-storedobjectdetail) | тип | `api.types` |
| [`StoredSelection`](components.ReprocessForm.md#інтерфейс-storedselection) | інтерфейс | `components.ReprocessForm` |
| [`StrategiesSummary`](pages.RulesEditorPage.md#компонент-strategiessummary) | компонент | `pages.RulesEditorPage` |
| [`STRATEGY_LABELS`](pages.RulesEditorPage.md#константа-strategy_labels) | константа | `pages.RulesEditorPage` |
| [`STRATEGY_TEMPLATES`](pages.RulesEditorPage.md#константа-strategy_templates) | константа | `pages.RulesEditorPage` |
| [`Table`](components.ui.md#компонент-table) | компонент | `components.ui` |
| [`Tabs`](components.ui.md#компонент-tabs) | компонент | `components.ui` |
| [`TaskConfig`](api.types.md#тип-taskconfig) | тип | `api.types` |
| [`TaskPage`](pages.TasksPage.md#компонент-taskpage) | компонент | `pages.TasksPage` |
| [`TaskQuickRun`](components.TaskQuickRun.md#компонент-taskquickrun) | компонент | `components.TaskQuickRun` |
| [`TasksPage`](pages.TasksPage.md#компонент-taskspage) | компонент | `pages.TasksPage` |
| [`TaskSummary`](api.types.md#тип-tasksummary) | тип | `api.types` |
| [`TaskValidation`](api.types.md#тип-taskvalidation) | тип | `api.types` |
| [`TERMINAL_JOB_STATUSES`](api.hooks.md#константа-terminal_job_statuses) | константа | `api.hooks` |
| [`TestReport`](api.types.md#тип-testreport) | тип | `api.types` |
| [`TestReportView`](components.JobPanel.md#компонент-testreportview) | компонент | `components.JobPanel` |
| [`TestResultsRecord`](api.types.md#тип-testresultsrecord) | тип | `api.types` |
| [`TestRunRequest`](api.types.md#тип-testrunrequest) | тип | `api.types` |
| [`TestSummary`](api.types.md#тип-testsummary) | тип | `api.types` |
| [`THEME_KEY`](app.theme.md#константа-theme_key) | константа | `app.theme` |
| [`ThemeControl`](components.ThemeControl.md#компонент-themecontrol) | компонент | `components.ThemeControl` |
| [`ThemePreference`](app.theme.md#тип-themepreference) | тип | `app.theme` |
| [`toJsonText`](components.JsonEditor.md#функція-tojsontext) | функція | `components.JsonEditor` |
| [`toProblem`](api.problem.md#функція-toproblem) | функція | `api.problem` |
| [`UnifiedDiff`](components.UnifiedDiff.md#компонент-unifieddiff) | компонент | `components.UnifiedDiff` |
| [`UnknownMaterial`](api.types.md#тип-unknownmaterial) | тип | `api.types` |
| [`unwrap`](api.client.md#функція-unwrap) | функція | `api.client` |
| [`unwrapWithEtag`](api.client.md#функція-unwrapwithetag) | функція | `api.client` |
| [`UpstreamStatus`](api.types.md#тип-upstreamstatus) | тип | `api.types` |
| [`UsageReport`](api.types.md#тип-usagereport) | тип | `api.types` |
| [`useApi`](app.context.md#функція-useapi) | функція | `app.context` |
| [`useAuth`](app.context.md#функція-useauth) | функція | `app.context` |
| [`useConfig`](app.context.md#функція-useconfig) | функція | `app.context` |
| [`useCursorList`](api.hooks.md#функція-usecursorlist) | функція | `api.hooks` |
| [`useJob`](api.hooks.md#функція-usejob) | функція | `api.hooks` |
| [`useTheme`](app.theme.md#функція-usetheme) | функція | `app.theme` |
| [`validateAgainst`](lib.schema.md#функція-validateagainst) | функція | `lib.schema` |
| [`validateConnectionSecrets`](lib.secrets.md#функція-validateconnectionsecrets) | функція | `lib.secrets` |
| [`VersionStatus`](api.types.md#тип-versionstatus) | тип | `api.types` |
| [`writeApiKey`](auth.session.md#функція-writeapikey) | функція | `auth.session` |
