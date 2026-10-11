# Детальні оголошення AUTO.RIA

`autos.autoria-ad-page@1.1.0` витягує повну сутність `car_ad` з HTML сторінки
оголошення. Природний ключ — `site` + `ad_id`; він сумісний із частковими записами
`autos.autoria-search-page@1.0.0` зі сторінки каталогу.

## Поля та походження

JSON-LD `Vehicle` дає марку, модель, рік, ціну продавця, валюту й статус.
Серверний стан `window.__PINIA__` дає пробіг, пальне, об’єм двигуна, коробку,
кузов, привід, колір, регіон, тип продавця й решту характеристик.

| Група | Додаткові поля |
|---|---|
| Кузов і модель | `doors`, `seats`, `generation`, `modification`, `trim` |
| Двигун | `power_hp`, `power_kw`, `modification_power_hp`, `emission_standard` |
| Заявлений стан | `technical_state`, `paint_condition`, `inspection_ready`, `condition_options` |
| Витрати пального | `fuel_consumption_l_per_100km`: `city`, `highway`, `combined` |
| Обладнання | `equipment`: безпека, комфорт, мультимедіа, салон, освітлення, паркування та інші категорії |

Усі нові поля необов’язкові. Відсутнє поле пропускається; `null` не надсилається.
Назви опцій зберігаються з джерела, повтори розмітки не дублюють опції.
Потужність не перераховується між одиницями: `power_kw` з’являється тільки за
явного значення кВт. `power_hp` бере параметр двигуна, а за його відсутності —
назву модифікації. `modification_power_hp` зберігає окрему заяву в назві модифікації.
Розбіжність викликає діагностику `extract.conflicting_power`.

Опис обмежує параметр `description_max_chars` (типово 500, допустимо 0–500).
Значення 0 пропускає опис. Телефони, адреси електронної пошти й вулиці в описі
маскуються; імена продавців, VIN і номерні знаки не входять до полів сутності.

## Перевірка

У корені checkout з установленими workspace-залежностями виконайте:

```powershell
uv run python examples/automarket/packages/autos.autoria-ad-page/tests/verify.py
uv run jane-handler-runtime test examples/automarket/packages/autos.autoria-ad-page
uv run jane-handler-runtime test examples/automarket/packages/autos.autoria-search-page
```

Перша команда запускає точні тести маніфестів, валідує поля за JSON Schema,
природний ключ, пропуск `null`, правила посилань та три ручні порівняння із
[доказами AUTO.RIA](../../evidence/autoria.json). Друга й третя команди виконують
пакети у налаштованій пісочниці runtime; типовий Docker backend потребує образу
`python-extractor@1` та доступного Docker.

Мінімізовані реальні приклади BMW 5 Series, Peugeot Rifter і Volkswagen Passat
зберігають структуровані фрагменти джерела без контактів. Доказ містить SHA-256
оригінального матеріалу, час отримання, URL, ручні очікування та SHA-256 fixture.
Параметр `--live-samples <каталог>` у першій команді додатково перевіряє локальні
оригінальні матеріали проти цього доказу.

## Обхід

[Правила AUTO.RIA](../autos.autoria-rules/README.md) знаходять оголошення
зі сторінок каталогу. Кількість сторінок, період повторного відвідування та розклад
задаються конфігурацією завдання Jane.
