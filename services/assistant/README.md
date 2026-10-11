# Assistant

Сервіс Jane, який за допомогою LLM підключає нові джерела (вибірка, аналіз, варіанти правил збору, пошук, адаптація або створення екстракторів із тестами) і вдосконалює екстрактори на проблемних прикладах (`assistant.v1`).

Повна документація модуля — [docs/components/assistant](../../docs/components/assistant/README.md): швидкий старт, залежності, конфігурація, інтеграція, будова, експлуатація.

- Запуск: `uv run --package jane-assistant python -m jane_assistant`; адреси сусідів — `JANE_ASSISTANT_*_URL` — [швидкий старт](../../docs/components/assistant/quickstart.md).
- Тести: `just test assistant` (unit, сценарії на контрактних фейках сусідів, процесний e2e, контрактні); стан у PostgreSQL — `just integration --project <проєкт> services/assistant`.
- Контракт: [assistant.v1.yaml](../../contracts/openapi/assistant.v1.yaml); сусіди — `llm`, `registry`, `collector`, `handler`, `orchestrator`, `storage`.
