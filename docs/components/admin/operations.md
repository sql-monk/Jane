# Admin: експлуатація

Розгортаються статичні assets і runtime config; бізнес-дані та їхні backup належать backend сервісам.

[Розгортання](#розгортання) · [Моніторинг](#моніторинг) · [Оновлення-й-відновлення](#оновлення-й-відновлення) · [Типові-проблеми](#типові-проблеми)

## Розгортання

```powershell
pnpm --dir web/admin install --frozen-lockfile
pnpm --dir web/admin build
```

Публікуйте dist на static server з SPA fallback: `/sources/…`, `/tasks/…`, `/packages/…` мають віддавати index.html. `/config.json` має бути доступний без stale cache; `/api/<service>` маршрутизується reverse proxy до API. Сервер auth/scopes має відповідати браузерному режиму входу. Реальний OIDC тут не перевірено.

## Моніторинг

Admin не має `/metrics` або власного backend health endpoint. Перевіряйте завантаження index/assets/config, HTTP status API, console errors і стан server health. Вкладка Network має показувати правильний service prefix та заголовки bearer/Idempotency-Key/If-Match. Технічні подробиці не мають розкривати secret values; для користувача показується Problem, а для діагностики — trace ID.

## Оновлення й відновлення

Збережіть попередній dist і public config перед заміною. Новий build публікуйте атомарно разом із assets із hash-іменами; довге кешування index.html може посилатися на вже видалені assets. Runtime config замінюється без build, після чого потрібен reload сторінки. Перед зміною contracts клієнтські типи генеруються й перевіряються разом з API сумісністю.

Rollback повертає попередній bundle/config, але не відкотить зміни завдань/пакетів, які користувач уже надіслав API. API ключі та OIDC session tokens не входять у backup dist; після очищення sessionStorage користувач входить заново. Власна DB migration/backup N/A: Admin не має такої бази. Координатор окремо перевіряє real UI проти тестового proxy.

## Типові проблеми

| Симптом | Перевірка | Дія |
|---|---|---|
| Порожня сторінка після оновлення | Assets 404, console, stale index | Відновіть узгоджений dist і оновіть кеш index |
| Route працює лише через головну | SPA fallback | Налаштуйте index.html для прямих route URL |
| Замість даних HTML / 404 | api_base/services/proxy | Перевірте prefix та strip режим |
| Списки показують мокові записи | API_TARGET/гібридні змінні | Налаштуйте real proxy і перезапустіть Vite |
| 401/403 | auth mode, scopes, JWT audience | Повторний вхід і серверна policy |
| 412 у редакторі | ETag попередньої версії | Перечитайте, перегляньте diff і повторіть зміну |
| Помилка config bootstrap | JSON/oidc required поля | Виправте config.json і перезавантажте сторінку |
| Job довго running | Job error/progress та API polling | Перевірте backend; закриття UI не скасовує job |
| Preview обірвано | preview_max_bytes / HTTP Range | Це обмежений preview; повний object отримайте через API |
| Dev port occupied | strictPort і власні процеси | Оберіть інший JANE_ADMIN_PORT |

[Поля runtime config](configuration.md), [proxy режими](integration.md).
