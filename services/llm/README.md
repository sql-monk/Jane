# LLM gateway

Сервіс викликів мовних моделей Jane: провайдери й псевдоніми моделей, бюджети рівнів і облік витрат, етап `kind: llm` у ланцюжку обробки (`llm.v1` і `handler.v1`).

Повна документація модуля — [docs/components/llm](../../docs/components/llm/README.md): швидкий старт, залежності, конфігурація, інтеграція, будова, експлуатація.

- Запуск без бази й ключів: `JANE_LLM_STORE=memory`, команда `uv run --package jane-llm python -m jane_llm` — [швидкий старт](../../docs/components/llm/quickstart.md).
- Тести: `just test llm`; з PostgreSQL — `just integration --project <проєкт> services/llm` після `just up --project <проєкт> postgres`.
- Контракти: [llm.v1.yaml](../../contracts/openapi/llm.v1.yaml), [handler.v1.yaml](../../contracts/openapi/handler.v1.yaml).
- Вбудовані LLM-пакети — `packages/`, приклад seed-файлу — `config/seed.example.yaml`.
