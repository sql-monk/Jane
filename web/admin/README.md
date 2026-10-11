# Admin UI

Адміністративний вебінтерфейс Jane: React, TypeScript, Vite, pnpm. Працює на контрактних моках або з API сервісів через reverse proxy.

```powershell
corepack pnpm --dir web/admin install --frozen-lockfile
corepack pnpm --dir web/admin mocks
corepack pnpm --dir web/admin dev
```

Команди виконуються з кореня репозиторію; `mocks` і `dev` — у різних терміналах. Адреса за замовчуванням — `http://127.0.0.1:4600`.

- Документація модуля — [docs/components/admin](../../docs/components/admin/README.md): запуск, конфігурація `config.json`, інтеграція з API, будова, експлуатація.
- Сценарії роботи оператора — [посібник користувача](../../docs/user-guide/README.md).
