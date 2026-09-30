# Профілі лімітів WP-14

`dev-laptop.json`, `ci.json` і `single-node.json` — документи `PlatformLimits` за
`contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits`. Їхні значення перенесено без
змін із довідкових прикладів WP-00 у `contracts/examples/schemas/common/limits@PlatformLimits/`.
Це **кандидати**, а не перевірені стартові значення: вимірювань на цільових середовищах WP-14
ще немає. Орієнтовні ресурси наведено в ADR-0007; відповідність реальних машин цим умовам
не підтверджено.

| Файл | Призначення | Статус |
|---|---|---|
| `dev-laptop.json` | Docker Desktop Windows 11 або Docker Linux, 4 vCPU, 8–16 ГБ RAM, SSD | кандидат, не виміряно |
| `ci.json` | ізольований runner, testsite, без реальних сайтів та платного LLM | кандидат, не виміряно |
| `single-node.json` | одна Linux VM із Docker Compose, орієнтир 8 vCPU / 32 ГБ RAM | кандидат, не виміряно |

Перевірка форми всіх трьох файлів із чистого checkout:
`uv run --all-packages python deploy/profiles/check.py`. Вона не вимірює продуктивність.

## Застосування

Оркестратор читає файл `PlatformLimits` із `JANE_ORCHESTRATOR_LIMITS_FILE` **лише під час
першого заповнення** документа лімітів у своїй БД. Для наявної БД прочитайте
`GET /v1/limits/platform`, збережіть ETag і передайте обраний JSON через
`PUT /v1/limits/platform` з `If-Match: <ETag>` та правом `orchestrator:admin`.
Перевірте результат через `GET /v1/limits/platform` і
`GET /v1/limits/effective?source_id=...&task_id=...&stage_id=...`.
Нові ліміти застосовуються до **нових** запусків; поточний запуск уже зафіксував ефективні
значення. Обмеження сайту, провайдера та `hard_caps` можуть лише звузити профіль.

Профіль `ci` має довідкову частоту 50 запитів/с на хост. Використовуйте її тільки проти
локального testsite в ізольованій мережі. Перед будь-яким реальним сайтом задайте нижчу
межу на рівні джерела; не вважайте 50 запитів/с дозволеною частотою для зовнішнього хоста.

Порядок вимірювання, критерії прийняття і журнал доказів: [валідація профілів](../../docs/operations/limits-validation.md).
