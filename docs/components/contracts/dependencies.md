# Контракти: залежності

Що потрібно інструментам `contracts/tools` і пакету `jane-contracts`, і що стається без кожної залежності. Інструменти — uv-скрипти (PEP 723): свої залежності вони оголошують у заголовку файла, і `uv run` ставить їх в окреме середовище, без workspace.

## Зміст

- [Обов'язкові](#обовязкові)
- [Залежності скриптів](#залежності-скриптів)
- [Опційні](#опційні)
- [Поведінка за недоступності](#поведінка-за-недоступності)

## Обов'язкові

| Залежність | Версія | Для чого |
|---|---|---|
| `uv` | перевірено з 0.12.13 (як у CI) | Запуск скриптів і рецептів |
| Python | `>=3.12` | Скрипти й пакет `jane-contracts` |
| `just` | перевірено з 1.58.0 | Рецепти `contracts-*` (можна викликати скрипти напряму через `uv run`) |

## Залежності скриптів

| Скрипт | Залежності (із заголовка файла) |
|---|---|
| [check_contracts.py](../../../contracts/tools/check_contracts.py) | `jsonschema[format-nongpl]>=4.23,<5`, `referencing>=0.35`, `pyyaml>=6`, `openapi-spec-validator>=0.7.1,<0.8` |
| [compat.py](../../../contracts/tools/compat.py) | `pyyaml>=6` |
| [mock.py](../../../contracts/tools/mock.py) | `pyyaml>=6` (сервер — стандартний `http.server`) |
| Пакет `jane-contracts` ([pyproject.toml](../../../contracts/python/pyproject.toml)) | Немає залежностей; лише `typing.Protocol` і dataclasses |

## Опційні

| Залежність | Версія | Хто використовує |
|---|---|---|
| Node.js із `npx` | 24 (`.node-version`) | Redocly lint, мок Prism, бандл для генераторів |
| `@redocly/cli` | 2.54.3 (закріплено в `check_contracts.py`) | Крок 7 лінтера; обов'язковий у CI (`JANE_CONTRACTS_REDOCLY=1`) |
| `@stoplight/prism-cli` | 5.16.0 | Мок із валідацією запитів за схемою |
| `oasdiff` | бінарний файл у `PATH` або Docker-образ `tufin/oasdiff:v1.33.0` (тег і digest закріплено в `compat.py`) | `compat.py --oasdiff` |
| Docker | — | Запуск образу oasdiff, якщо бінарного файла немає |
| `git` | — | `compat.py` читає контракти з базової ревізії через `git` |
| `datamodel-code-generator` | 0.83.0 у dev-групі workspace | Pydantic-моделі для специфікацій, які він приймає (контракти Jane не приймає — див. [інтеграція](integration.md#генерація-клієнтів)) |
| `openapi-typescript` | версія з `web/admin/pnpm-lock.yaml` | Типи TypeScript для Admin UI (`pnpm gen:api`) |

## Поведінка за недоступності

| Що недоступне | Поведінка |
|---|---|
| Node.js / `npx` | Лінтер пропускає Redocly (`[skip] Redocly lint`); з `--require-redocly` — помилка й ненульовий код виходу |
| oasdiff і Docker разом | `compat.py --oasdiff` пише `oasdiff: skipped (neither oasdiff nor docker found)` і виконує лише власне порівняння |
| `git` або базова ревізія | `compat.py` не може прочитати базу й завершується з помилкою |
| Мережа (перший запуск) | `uv` не може встановити залежності скрипта; надалі вони беруться з кешу `uv` |
| Каталог `contracts/` у образі сервісу | Сервіси, що валідують дані за схемами, не стартують (`ContractsNotFound`, [jane-kit](../jane-kit/dependencies.md#поведінка-за-недоступності)) |
