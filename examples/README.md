# Сценарії Jane: каталог, ціни, Telegram

Це відтворюваний **порядок налаштування** з контрактними JSON-документами цього checkout.
Саме виконання повного ланцюжка на реальних сервісах у WP-14 **не перевірено**. Значення
`shop.example.test`, `city_events_example`, `tg-main`, digest пакетів і підключення у
контрактних зразках є демонстраційними. Перед запуском їх слід замінити фактичними URL,
ідентифікаторами, зареєстрованими незмінними версіями пакетів і дозволеними тестовими
підключеннями. Не використовуйте реальний Telegram без тестового доступу.

## Підготовка

1. Підніміть залежності й застосунки за [операційною інструкцією](../docs/operations/README.md).
   `just up` піднімає dev-залежності й testsite, але не всі застосунки.
2. У registry опублікуйте та перевірте правила Web Collector, пакети витягування товарів і
   цін, обробники збереження. Звірте фактичні `package_id`, `version`, `digest`; у цьому
   checkout готового пакета витягування товарів/цін для наведених зразків немає.
3. Створіть керовані підключення для RAW і результатів. Для Telegram потрібен окремий
   обліковий запис і `secret_refs`; самих секретів у JSON немає.
4. Перевірте `GET /v1/health`, `GET /v1/executors`, `GET /v1/limits/platform`. Для зовнішнього
   сайту виставте дозволені source-ліміти; профілі WP-14 ще не виміряні.

## Каталог товарів та окрема перевірка цін

| Крок | Документ у `contracts/examples/schemas/` | API оркестратора |
|---|---|---|
| Джерело | [`source/shop.json`](../contracts/examples/schemas/source/shop.json) | `POST /v1/sources` |
| Правила вебзбору | [`collector-rules/web-shop.json`](../contracts/examples/schemas/collector-rules/web-shop.json) | версія пакета в registry; `POST /v1/rules/validations` у Web Collector |
| Повний каталог | [`task-config/catalog-full.json`](../contracts/examples/schemas/task-config/catalog-full.json) | `POST /v1/task-validations`, потім `POST /v1/tasks` |
| Перевірка цін | [`task-config/price-check.json`](../contracts/examples/schemas/task-config/price-check.json) | окремі `POST /v1/task-validations` і `POST /v1/tasks` |

Для змінювальних POST задайте унікальний `Idempotency-Key`; validation POST його не потребує.
Запускайте незалежно `POST /v1/tasks/shop-catalog/runs` та
`POST /v1/tasks/shop-price-check/runs` із `{}` або контрактним `RunRequest`.
Отримайте `job_id` із 202 і дочекайтеся завершення через `GET /v1/jobs/{job_id}`.
Звірте RAW, поточну ціну та історію через відповідні API сховища й trace матеріалу.
Перевірка цін має залишатися окремим завданням із власним розкладом: її успіх не означає
повторний повний обхід каталогу.

Для локального testsite замініть `shop.example.test` у source/rules/task на адресу з
`just env`, а URL товарів — на шляхи з
[`expected_urls.json`](../tests/fixtures/testsite/expected_urls.json). Схема й scope правил
мають відповідати новому хосту. Швидкість тестового сайту не є дозволом підвищувати
частоту запитів до реальних сайтів.

## Події з Telegram

| Крок | Документ | API оркестратора |
|---|---|---|
| Джерело | [`source/telegram.json`](../contracts/examples/schemas/source/telegram.json) | `POST /v1/sources` |
| Правила каналу | [`collector-rules/telegram-channel.json`](../contracts/examples/schemas/collector-rules/telegram-channel.json) | опублікувати правила й перевірити Telegram Collector |
| Завдання | [`task-config/telegram-events.json`](../contracts/examples/schemas/task-config/telegram-events.json) | `POST /v1/task-validations`, потім `POST /v1/tasks` |

Після налаштування тестового каналу та LLM fake/дозволеного провайдера запустіть
`POST /v1/tasks/news-tg-events/runs` з `Idempotency-Key`, опитайте job, звірте RAW і
витягнуті події. Для реального провайдера витрати обмежуйте на platform/source/task;
зразок бюджету не є підтвердженим безпечним значенням. Перевірте повтор після рестарту,
редагування повідомлення як нову ревізію і відсутність дублів.

## Статус доказів

Контрактні JSON-зразки перевіряє `uv run contracts/tools/check_contracts.py`.
Це доводить форму документів, але не наявність referenced package digest, доступ до
Telegram чи виконання ланцюжка. Критерій WP-14 «приклади відтворюються з чистого checkout»
залишається **не підтвердженим** до реального прогону з пакетом товарів/цін і контрольованим
Telegram-джерелом на фінальній ревізії.
