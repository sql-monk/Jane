# Розробка Jane: короткий довідник

Точка входу для розробника: що встановити й які команди запускати. Пояснення, приклади й перевірені запуски — у розділі [docs/development](docs/development/README.md).

## Встановлення

| Інструмент | Версія | Примітка |
|---|---|---|
| uv | 0.12.13 | Python 3.12 завантажує сам |
| just | 1.58.0 | `uv tool install "rust-just==1.58.0"` або без встановлення `uvx --from rust-just just <рецепт>` |
| Docker з Compose v2 | — | Dev-стек, інтеграційні, e2e й ізоляційні тести |
| Node.js | 24 | Admin UI через `corepack pnpm`; Redocly |
| gitleaks | 8.30.1 | Git-хук і хуки агентів |

Після клонування:

```powershell
uv sync --all-packages
just hooks
just check
```

Деталі для Windows і Linux — [Середовище](docs/development/environment.md).

## Команди

| Команда | Що робить |
|---|---|
| `just check` | lint + types + unit + contract + web — те, що перевіряє CI |
| `just lint` / `just fmt` / `just types` | ruff і лінтер контрактів / автоформатування / mypy |
| `just unit` / `just contract` | Unit-тести / контракти й контрактні тести |
| `just test <сервіс> [аргументи pytest]` | Тести одного пакета, наприклад `just test jane-kit -k limits` |
| `just up [сервіси]` / `just down [-v]` | Dev-стек з унікальним compose-проєктом і портами; `-v` видаляє дані |
| `just ps` / `just logs` / `just env` | Стан, журнали, адреси й згенеровані облікові дані стеку |
| `just integration` / `just e2e` / `just isolation` | Тести зі стеком / наскрізні сценарії / ізоляція пісочниці (Linux) |
| `just web` | Перевірки Admin UI через pnpm |
| `just testsite` | Тестовий сайт на `http://127.0.0.1:8080` |
| `just new-service <ім'я>` | Сервіс із `templates/service` |
| `just contracts-check` / `just contracts-compat` | Лінтер контрактів / зворотна сумісність із `main` |
| `just contracts-mock <api>` / `just contracts-gen <api> <каталог>` | Мок API з прикладів / Python-клієнт контракту |
| `just hooks` | Git-хук pre-commit з gitleaks |

Повний опис аргументів — [Команди перевірки](docs/development/checks.md).

## Куди далі

| Тема | Сторінка |
|---|---|
| Тести й маркери | [docs/development/testing.md](docs/development/testing.md) |
| CI | [docs/development/ci.md](docs/development/ci.md) |
| Новий сервіс, обробники й пакети | [new-service.md](docs/development/new-service.md), [handlers.md](docs/development/handlers.md) |
| Контракти | [docs/development/contracts.md](docs/development/contracts.md) |
| Процес WP і гігієна | [wp-process.md](docs/development/wp-process.md), [hygiene.md](docs/development/hygiene.md) |
| Документація | [docs/development/documentation.md](docs/development/documentation.md) |
| Спільна бібліотека сервісів | [jane-kit](docs/components/jane-kit/README.md) |
