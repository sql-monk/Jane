# Запуск Admin

Admin — вебінтерфейс до публічних API Jane. Для демонстрації підключи його до сервісів уже запущеного [стеку](README.md).

## Локальна розробка

У корені Jane встанови залежності, потім запусти Vite в окремому терміналі:

```powershell
pnpm --dir web/admin install --frozen-lockfile
pnpm --dir web/admin dev --host 127.0.0.1
```

Vite показує адресу сторінки. Маршрути `/api/<service>` визначаються [dev-proxy.ts](../../web/admin/dev-proxy.ts); для підключення реального сервісу задавай `JANE_ADMIN_TARGET_<API>` його адресою з `stack.py env`, або використовуй проксі всього стеку.

## Зібрана версія

```powershell
pnpm --dir web/admin build
```

Вкажи абсолютний шлях `web/admin/dist` у `JANE_ADMIN_DIST_PATH` **перед створенням стеку з proxy**. Публічний `config.json` задає `api_base`, назви сервісів, режим входу, polling і розмір сторінки. Приклад та перевірка полів — [налаштування Admin](../components/admin/configuration.md).

Ключ Admin бери з локального stack-файла `.jane/stack-<project>.json`; введи його на екрані входу. Він не належить до `config.json`. Для розгорнутого середовища узгодь OIDC із [правилами автентифікації](../architecture/security.md).

## Що відкрити спочатку

1. **Джерела** — `testsite-shop`.
2. **Завдання** — `testsite-catalog` і `testsite-price-check`.
3. **Запуски** — завершені запуски та їхні етапи.
4. **Результати** — сутності товарів, походження й історія.

Сценарії та точні назви елементів — [посібник користувача](../user-guide/README.md).
