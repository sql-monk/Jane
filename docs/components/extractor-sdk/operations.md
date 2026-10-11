# jane-extractor-sdk: супровід

SDK — бібліотека без власного процесу, тому «експлуатація» зводиться до версій SDK у профілі виконання, перевірок і діагностики пакетів. Моніторинг виконання пакетів — у [Handler Runtime](../handler-runtime/operations.md).

## Зміст

- [Версії й сумісність](#версії-й-сумісність)
- [Оновлення SDK](#оновлення-sdk)
- [Тести SDK](#тести-sdk)
- [Діагностика пакета](#діагностика-пакета)
- [Типові помилки автора](#типові-помилки-автора)

## Версії й сумісність

| Що | Версія | Де зафіксовано |
|---|---|---|
| SDK | `0.1.0` | [pyproject.toml](../../../libs/extractor-sdk/pyproject.toml), `jane_extractor_sdk.__version__` |
| SDK в образі профілю | `0.1.0` | `sdk` у [python-extractor-1.json](../../../services/handler-runtime/src/jane_handler_runtime/profiles/python-extractor-1.json) |
| протокол раннера | `1` | `jane_extractor_sdk.runner.PROTOCOL_VERSION` |

Пакет не залежить від версії SDK явно: він обирає профіль (`dependencies.runtime_profile`), а профіль визначає версію SDK у пісочниці. Тому пакет, перевірений на `python-extractor@1`, має працювати на будь-якому образі цього профілю.

## Оновлення SDK

SDK копіюється в образ пісочниці під час збирання (`jane-handler-runtime build-image`) і водночас імпортується Handler Runtime як бібліотека. Після зміни SDK:

1. Проженіть тести SDK і Handler Runtime ([тести SDK](#тести-sdk)).
2. Зберіть новий образ профілю й оновіть сервіс Handler Runtime з того самого коміту: версія протоколу в раннері образу й у runtime має збігатися.
3. Сумісні зміни (нові помічники, нові необов'язкові поля) лишаються в профілі `@1`. Зміни, що можуть змінити результат наявних пакетів (поведінка `entity`, `ctx.text`, протокол), оформлюйте новим профілем і новою версією протоколу.

## Тести SDK

```powershell
just test extractor-sdk
```

Уривок виводу перевірочного запуску 2026-10-11 (ревізія `c59d26d`):

```text
collected 21 items

libs\extractor-sdk\tests\test_sdk.py .....................               [100%]

============================= 21 passed in 35.94s =============================
```

Тести охоплюють помічники результату, контекст, раннер (зокрема перенаправлення `print` і аудит-хук), канонічний архів, розпакування й порівняння. Зразковий пакет `examples/testsite-product-extractor` перевіряється також через Handler Runtime ([швидкий старт Handler Runtime](../handler-runtime/quickstart.md#тести-пакета-через-cli)).

## Діагностика пакета

Де шукати причину, якщо пакет поводиться не так, як очікується:

| Джерело | Що там |
|---|---|
| `status`, `failure.kind`, `failure.message` | підсумок і клас проблеми |
| `failure.details.traceback`, `stage` | виняток коду пакета й етап: `import` або `extract` |
| `diagnostics.messages` | повідомлення `ctx.log` і порушення пісочниці (`sandbox.network_blocked`, `sandbox.process_blocked`) |
| `diagnostics.validation_errors` | невідповідності схемам із JSON Pointer до поля |
| `diagnostics.logs_ref` | хвіст stderr: `print`, журнали Python |
| `diagnostics.metrics` | `duration_ms`, `cpu_ms`, `peak_memory_mb`, `output_bytes` |

Для тестів `jane-handler-runtime test` друкує розбіжності з очікуваним виходом (`pointer`, `expected`, `actual`), а `--json` дає повний `TestReport` з `result` кожного випадку.

## Типові помилки автора

| Симптом | Причина | Виправлення |
|---|---|---|
| pytest проходить, Handler Runtime — `schema_mismatch` | `run_local` не перевіряє схеми | запускайте `jane-handler-runtime test`; дивіться `validation_errors` |
| `schema_mismatch`: `null is not allowed; omit the field or list it in 'cleared'` | сутність повернуто словником з `None` у `fields` | будуйте сутність через `entity()` або не передавайте поле |
| `schema_mismatch`: ``key fields [...] are missing`` | поле з `key_fields` відсутнє або не скаляр | заповніть ключове поле або поверніть `unrecognized` |
| `execution_error`, `stage: import`, `ModuleNotFoundError` | модуль не в `src/` пакета або бібліотеки немає в профілі | перевірте `entry.module` і структуру; використовуйте лише бібліотеки профілю |
| `execution_error`: `invalid status 'failed'` | `extract` повернув `failed` | для помилки кидайте виняток |
| `execution_error`: `Out of range float values are not JSON compliant` | у результаті `NaN` або `Infinity` | перевіряйте числа перед поверненням |
| `sandbox_violation` | код звертається до мережі або запускає процес | приберіть мережу й процеси; вміст уже є в `ctx` |
| `timeout` або `resource_exceeded` | важкий розбір, великий документ | оптимізуйте код або підніміть ліміти етапу в межах стелі Handler Runtime |
| у результаті немає повідомлень `print` | stdout зарезервовано під протокол | використовуйте `ctx.log`; `print` видно лише в `diagnostics.logs_ref` |
| `dependency_not_allowed` | `dependencies.python` вимагає бібліотеку чи версію поза профілем | перегляньте `jane-handler-runtime profile` |
