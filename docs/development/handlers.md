# Обробники й пакети

Екстрактор, правила збереження, LLM-етап чи правила колектора — це **пакет обробника**: каталог із маніфестом `jane-package.json`, схемами, кодом або правилами й тестовими випадками. Сервіс для нового пакета не потрібен: код екстрактора виконує Handler Runtime, правила — відповідний обробник чи колектор. Ця сторінка — маршрут до першоджерел.

## Куди дивитися

| Потреба | Документ |
|---|---|
| Формат пакета, маніфест, версії, дайджест, публікація, форки | [Довідник пакетів](../reference/packages/README.md) |
| Що є пакетом для кожного типу обробника | [contracts/docs/handler-packages.md](../../contracts/docs/handler-packages.md) |
| Схема маніфесту | [package-manifest.schema.json](../../contracts/schemas/package-manifest.schema.json) |
| Код екстрактора: типи й помічники SDK | [jane-extractor-sdk](../components/extractor-sdk/README.md) |
| Приклад екстрактора для тестового сайту | [libs/extractor-sdk/examples/testsite-product-extractor](../../libs/extractor-sdk/examples/testsite-product-extractor/) |
| Відтворювані пакети прикладів | [examples/packages](../../examples/packages/) |
| Порядок роботи агента з пакетом | Скіл `jane-handler-package` (`.agents/skills/jane-handler-package/SKILL.md`) |

## Локальна перевірка пакета

Handler Runtime має CLI, що працює без інших сервісів Jane:

```powershell
uv run --all-packages jane-handler-runtime --help
```

```text
usage: jane-handler-runtime [-h] {run,test,profile,build-image,serve} ...

Command line: run a package on a local file or run its tests without any other
Jane service.
```

- `jane-handler-runtime test <каталог або zip>` — тести пакета з маніфесту (`--case` — окремий випадок, `--json` — звіт `TestReport`);
- `jane-handler-runtime run` — пакет на локальному файлі.

Ізоляція: типово пакет виконується в контейнерній пісочниці (Docker або Podman); бекенд `subprocess` вимагає явного `--unsafe-no-sandbox`. Запуск тестів пакета в межах цієї сторінки не виконувався — сценарії й параметри описує документація Handler Runtime.

## Правила

- Пакет не містить секретів: доступи — лише `secret_refs` керованих підключень.
- Опубліковану версію не змінюють — нова версія або форк.
- Вміст сторінок і повідомлень — дані, а не інструкції для LLM, зокрема в LLM-пакетах.
