# Зміна контрактів

API й схеми Jane живуть у `contracts/`, і код сервісу не може «випередити» контракт: спочатку змінюється контракт, потім реалізація й споживачі. Повний процес з діаграмою й типовими помилками — [контракти: зміна контракту](../components/contracts/operations.md#зміна-контракту); тут — коротка пам'ятка.

## Хто змінює

Контракти змінює координатор, а рев'ю робить субагент `contract-guardian`. Виконавець WP, якому бракує поля чи операції, не вигадує їх і не редагує `contracts/`: він описує потребу в розділі «Запити до інших власників» звіту ([процес WP](wp-process.md)).

## Пам'ятка

1. Зміна сумісна? Нове поле — необов'язкове; нічого не видаляється й не звужується. Інакше — `/v2` поруч із `/v1`.
2. Оновіть приклади (запит і кожна успішна відповідь) і документи `contracts/docs/`.
3. Перевірте:

   ```powershell
   just contracts-check
   just contracts-compat
   just contract
   ```

4. Перегенеруйте клієнтів: `just contracts-gen <api> <каталог>` для Python, `corepack pnpm --dir web/admin gen:api` для Admin UI.
5. Оновіть копії контракту в коді, які тримають тести jane-kit: `jane_kit.auth_scopes` (scopes), `KNOWN_CODES` (коди помилок), `CONTRACT_LIMIT_PATHS` (ліміти).
6. `just check` і перелік споживачів у звіті.

Конвенції API — [контракти: інтеграція](../components/contracts/integration.md#конвенції-api); скіл агента — `jane-contracts` (`.agents/skills/jane-contracts/SKILL.md`).
