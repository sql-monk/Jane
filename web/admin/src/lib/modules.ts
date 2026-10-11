import type { AdminConfig } from "../config";
import type { components } from "../api/generated/operations";

export type ModuleConfiguration = components["schemas"]["module-configuration.schema"];
export type ModuleField = ModuleConfiguration["fields"][number];
export type ModuleTelemetry = components["schemas"]["module-telemetry.schema"];
export type ModuleDefinition = {
  id: string;
  name: string;
  executor: string;
  description: string;
  links: { label: string; to: string }[];
};

export function modules(config: AdminConfig): ModuleDefinition[] {
  const definitions = [
    {
      id: "web-collector",
      name: "Вебколектор",
      executor: config.services.collector,
      description: "Обхід сайтів, завантаження сторінок і рендеринг JavaScript.",
      links: [{ label: "Джерела", to: "/sources" }],
    },
    {
      id: "telegram-collector",
      name: "Telegram-колектор",
      executor: "telegram-collector",
      description: "Історія каналів, нові повідомлення та ревізії.",
      links: [{ label: "Джерела", to: "/sources" }],
    },
    {
      id: "handler-runtime",
      name: "Обробники",
      executor: config.services.handler,
      description: "Виконання пакетів у пісочниці, перевірка й екстракція.",
      links: [
        { label: "Пакети", to: "/packages" },
        { label: "Проблеми", to: "/problems" },
      ],
    },
    {
      id: "storage",
      name: "Збереження",
      executor: config.services.storage,
      description: "Оригінали, сутності й підключення сховищ.",
      links: [
        { label: "Матеріали", to: "/materials" },
        { label: "Підключення", to: "/connections" },
      ],
    },
    {
      id: "llm",
      name: "LLM",
      executor: config.services.llm,
      description: "Провайдери, моделі, бюджети й використання LLM.",
      links: [{ label: "Провайдери та бюджети", to: "/llm" }],
    },
    {
      id: "assistant",
      name: "Асистент",
      executor: config.services.assistant,
      description: "Підключення джерел і вдосконалення пакетів.",
      links: [{ label: "Асистент", to: "/assistant" }],
    },
    {
      id: "registry",
      name: "Репозиторій пакетів",
      executor: config.services.registry,
      description: "Версії пакетів, публікація, перевірка й активація.",
      links: [{ label: "Пакети", to: "/packages" }],
    },
    {
      id: "orchestrator",
      name: "Оркестратор",
      executor: config.services.orchestrator,
      description: "Черга, воркери, запуск ланцюжків і розклади.",
      links: [
        { label: "Запуски", to: "/runs" },
        { label: "Завдання", to: "/tasks" },
        { label: "Ліміти платформи", to: "/limits" },
      ],
    },
  ];
  return definitions.map((definition) => ({
    ...definition,
    executor: config.module_services[definition.id] ?? definition.executor,
  }));
}

const LABELS: Record<string, string> = {
  settings: "Робота модуля",
  engine: "Воркери й черга",
  contract: "Операційні ліміти",
  concurrency: "Паралельність",
  timeouts: "Час очікування",
  retries: "Повторні спроби",
  queue: "Черги",
  rate: "Частота запитів",
  crawl: "Обхід",
  sandbox: "Пісочниця",
  transfer: "Передавання даних",
  jobs: "Асинхронні операції",
  collector: "Збір і рендеринг",
  telegram: "Telegram",
  llm: "LLM",
  idempotency: "Захист від дублів",
  claims: "Утримання операцій",
  pages: "Списки",
  page: "Списки",
  workers: "Кількість воркерів",
  run_workers: "Увімкнути воркери",
  scheduler_enabled: "Увімкнути планувальник",
  log_level: "Рівень журналювання",
  health_check_timeout_ms: "Час перевірки доступності, мс",
  render_enabled: "Рендеринг JavaScript",
  render_wait_until: "Очікувати завантаження сторінки до",
  user_agent: "User-Agent колектора",
  operations_sample_interval_seconds: "Інтервал вимірювань, с",
  operations_retention_seconds: "Зберігати історію, с",
  operations_max_points: "Максимум точок графіка",
  max_attempts: "Максимум спроб",
  max_queue_depth: "Місткість черги",
  max_parallel_fetches: "Одночасні завантаження",
  max_parallel_fetches_per_host: "Завантаження з одного хоста",
  max_parallel_invocations: "Одночасні виклики обробників",
  max_parallel_runs_per_task: "Одночасні запуски завдання",
  max_parallel_stage_items: "Одночасні елементи етапу",
  max_inflight_materials: "Матеріали у виконанні",
  max_unacked_materials: "Матеріали без підтвердження",
  requests_per_second_per_host: "Запити до хоста за секунду",
  min_delay_ms_per_host: "Пауза між запитами до хоста, мс",
  respect_crawl_delay: "Враховувати Crawl-delay",
  max_depth: "Глибина обходу",
  max_pages_per_run: "Сторінки за запуск",
  max_bytes_per_run: "Обсяг за запуск, байт",
  max_material_bytes: "Розмір матеріалу, байт",
  max_redirects: "Максимум перенаправлень",
  max_links_per_page: "Посилання на сторінці",
  max_seed_urls: "Початкові адреси",
  max_frontier_size: "Місткість черги адрес",
  revisit_interval_seconds: "Повторне відвідування, с",
  connect_timeout_ms: "Підключення, мс",
  request_timeout_ms: "Запит, мс",
  invocation_timeout_ms: "Виконання обробника, мс",
  run_timeout_ms: "Запуск ланцюжка, мс",
  initial_backoff_ms: "Початкова пауза повтору, мс",
  max_backoff_ms: "Максимальна пауза повтору, мс",
  backoff_multiplier: "Множник паузи",
  jitter: "Випадкове рознесення повторів",
  lease_ms: "Утримання елемента, мс",
  lease_seconds: "Утримання збору, с",
  heartbeat_ms: "Підтвердження активності, мс",
  heartbeat_interval_ms: "Підтвердження активності, мс",
  poll_interval_ms: "Перевірка черги, мс",
  feed_page_size: "Матеріали за одну порцію",
  feed_wait_ms: "Очікування матеріалів, мс",
  backpressure_recheck_ms: "Перевірка вільного місця, мс",
  scheduler_interval_ms: "Перевірка розкладів, мс",
  inline_max_bytes: "Вбудований вміст, байт",
  transit_ttl_seconds: "Зберігання транзитного вмісту, с",
  render_max_pages: "Одночасні сторінки браузера",
  render_timeout_ms: "Рендеринг сторінки, мс",
  render_extra_wait_ms: "Додаткове очікування JavaScript, мс",
  memory_bytes: "Пам’ять, байт",
  cpu_seconds: "Процесорний час, с",
  wall_time_ms: "Час виконання, мс",
  network_enabled: "Доступ до мережі",
  defaults: "Типові значення",
  hard_caps: "Жорсткі межі",
  profile: "Назва профілю",
  state: "Стан і сесії",
  onboarding: "Підключення джерел",
  improvement: "Вдосконалення пакетів",
  unknown: "Невідомі матеріали",
  content: "Завантаження вмісту",
  search: "Пошук",
  material: "Приклади матеріалів",
  packages: "Пакети обробників",
  storage: "Запис у сховища",
  monitoring: "Історія моніторингу",
  pool_max_size: "Підключення до бази даних",
  db_pool_max: "Підключення до бази даних",
  in_progress_lease_ms: "Утримання активної операції, мс",
  job_lease_ms: "Утримання фонового завдання, мс",
  session_retention_seconds: "Зберігання сесій, с",
  cpu_cores: "Процесорні ядра",
  memory_mb: "Пам’ять пісочниці, МБ",
  tmpfs_mb: "Тимчасова пам’ять, МБ",
  max_output_bytes: "Розмір результату, байт",
  max_processes: "Процеси в пісочниці",
  max_archive_bytes: "Розмір архіву пакета, байт",
  max_unpacked_bytes: "Розмір розпакованого пакета, байт",
  max_files: "Файли в пакеті",
  cache_max_entries: "Пакети в кеші",
  max_input_bytes: "Вхідні дані, байт",
  max_stored_results: "Збережені результати",
  sync_retry_ms: "Пауза повторної доставки, мс",
  sync_max_attempts: "Спроби доставки",
  max_sample_chars: "Довжина прикладу, символи",
  max_problem_samples: "Приклади проблем",
  max_successful_examples: "Успішні приклади",
  max_proposal_bytes: "Розмір пропозиції, байт",
  min_confidence: "Мінімальна впевненість, 0–1",
  max_fixture_bytes: "Розмір тестового матеріалу, байт",
  max_list_items: "Елементи списку в прикладі",
  max_string_chars: "Довжина рядка, символи",
  short_string_chars: "Довжина короткого рядка, символи",
  chars_per_token: "Символи на токен",
  prompt_overhead_chars: "Службовий текст запиту, символи",
  part_overhead_chars: "Службовий текст частини, символи",
};

const WORDS: Record<string, string> = {
  max: "Максимум",
  min: "Мінімум",
  timeout: "Час очікування",
  retention: "Зберігання",
  seconds: "с",
  ms: "мс",
  bytes: "байт",
  interval: "Інтервал",
  size: "Розмір",
  limit: "Обмеження",
  retries: "Повтори",
  attempts: "Спроби",
  poll: "Перевірка",
  jobs: "Операції",
  results: "Результати",
  state: "Стан",
  ttl: "Час життя",
  cleanup: "Очищення",
  gc: "Очищення",
  batch: "Порція",
  cost: "Вартість",
  tokens: "Токени",
  messages: "Повідомлення",
  memory: "Пам’ять",
  worker: "Воркер",
  parallel: "Одночасно",
  per: "на",
  run: "Запуск",
  material: "Матеріал",
  budget: "Бюджет",
  cache: "Кеш",
  shared: "Спільний",
  enabled: "Увімкнено",
  pages: "Сторінки",
  fetch: "Завантаження",
  sample: "Приклад",
  chars: "символи",
  patterns: "Шаблони",
  examples: "Приклади",
  files: "Файли",
  file: "Файл",
  output: "Результат",
  input: "Вхідні дані",
  stored: "Збережені",
  count: "Кількість",
  query: "Запит",
  requests: "Запити",
  sessions: "Сесії",
  page: "Сторінка",
  transport: "Передавання",
  items: "Елементи",
  item: "Елемент",
  text: "Текст",
  depth: "Глибина",
  history: "Історія",
  models: "Моделі",
  model: "Модель",
  hosts: "Хости",
  links: "Посилання",
  urls: "Адреси",
  url: "Адреса",
  response: "Відповідь",
  sync: "Синхронний",
  lease: "Утримання",
};

export function fieldLabel(path: string): string {
  const name = path.split(".").at(-1) ?? path;
  return (
    LABELS[name] ??
    name
      .split("_")
      .map((word) => WORDS[word] ?? word)
      .join(" ")
  );
}

export function fieldGroup(path: string): string {
  const parts = path.split(".");
  if (parts[1]?.startsWith("operations_")) return LABELS.monitoring!;
  return fieldLabel(
    parts[0] === "settings"
      ? "settings"
      : parts[1] === "contract"
        ? (parts[2] ?? "contract")
        : (parts[1] ?? path),
  );
}

export function fieldHelp(path: string): string | undefined {
  const name = path.split(".").at(-1) ?? path;
  return {
    workers: "Кількість виконавців, які одночасно обробляють чергу. Нуль зупиняє її обробку.",
    run_workers: "Запускає фонову обробку операцій цього модуля.",
    scheduler_enabled: "Дозволяє автоматично запускати завдання за розкладом.",
    operations_sample_interval_seconds:
      "Як часто модуль записує нову точку. Менше значення дає детальнішу історію.",
    operations_retention_seconds: "Старші вимірювання автоматично видаляються. 86400 секунд — одна доба.",
    operations_max_points: "Межа точок у відповіді. Для довгого періоду точки рівномірно проріджуються.",
    log_level: "INFO підходить для звичайної роботи; DEBUG додає подробиці для діагностики.",
    render_enabled: "Вмикає браузер для сайтів, що завантажують дані через JavaScript.",
    pool_max_size: "Максимум одночасних підключень модуля до його бази даних.",
  }[name];
}
