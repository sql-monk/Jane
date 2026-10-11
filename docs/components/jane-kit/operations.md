# Jane Kit: експлуатація

Бібліотека оновлюється разом із застосунком-власником.

## Оновлення

1. Зафіксуйте версії Python, пакета та lockfile.
2. Зіставте використані сигнатури з [довідником](reference/types/README.md).
3. Перевірте settings, scopes, сховища та health checks у локальному середовищі.
4. Перезапустіть процес, що імпортує бібліотеку.

Версія в цьому checkout — `0.1.0`. Команди з кореня:

```powershell
uv run --package jane-kit pytest libs/jane-kit/tests/test_service.py libs/jane-kit/tests/test_config.py
```

## Стан і резервування

Збережіть SQLite-файл або зробіть consistent backup PostgreSQL БД за процедурою її власника. Для SQLite зупиніть writers або використайте SQLite backup API, зберігаючи цілісність WAL. In-memory job та ключі після restart втрачаються. Процес-власник визначає відновлення незавершених операцій і retention.

## Діагностика

| Ознака | Що перевірити |
|---|---|
| `AuthConfigError` на старті | Ключі, JWKS/issuer/audience, scopes усіх маршрутів, bind у none |
| 401/403 | Формат bearer token, термін JWT, потрібний scope |
| 503 від JWT | Доступність JWKS і наявність кешованих ключів |
| `LimitError` | Невідомий шлях, null, помилковий тип, hard cap |
| 409/422 для POST | Конкурентний claim або повторне використання ключа з іншим тілом |
| Job завис після restart | Durable store, lease/claim та власна resume-процедура |
| Health degraded | Підключені checks і `health_check_timeout_ms` |

Журнали мають `trace_id` та `request_id`; метрики доступні на `/metrics`, якщо їх не вимкнено. Не додавайте секрети до log context.
