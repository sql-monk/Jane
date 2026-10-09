# WP-23c. C-3: формат Python-контрактів

Дата: 2026-10-09. Гілка: `wp/23c-contracts-format`.
База: `2366213564a28679ba2a65ae21e069aa51c5c056` (`origin/codex/jane-integration` після `git fetch origin`).
Стан: **review**; незалежне рев'ю й contract-guardian замовляє координатор потоку C.

## Результат і межі

- Відтворено C-3: `storage_adapter.py` не проходив `ruff format --check`; єдина потрібна правка —
  перенесення довгої сигнатури `StorageAdapter.commit_entity`.
- Кореневий `pyproject.toml` виключає `contracts/` із Ruff. `scripts/dev.py` тепер передає явний
  шлях `contracts/python` до `ruff format --check` у `just lint` і до `ruff format` у `just fmt`.
  Реальний Ruff перевірив усі три Python-файли цього пакета попри загальне виключення `contracts/`.
- Правила `ruff check`, OpenAPI, JSON Schema, семантика Protocol-ів, залежності й workspace не змінювалися.
  Порівняння AST до/після форматування підтвердило незмінну семантику `storage_adapter.py`.
- Споживачі інтерфейсу: `services/storage` і шість адаптерів `files`, `postgres`, `sqlserver`,
  `mongodb`, `minio`, `s3`; оновлення їм не потрібні, сигнатури й типи незмінні.

## «Готово, коли» і доречний DoD

| Критерій | Доказ |
|---|---|
| C-3: файл відформатовано | Прямий `ruff format --check storage_adapter.py`: `1 file already formatted`, exit 0 |
| C-3: `just lint` охоплює `contracts/python` | Фактична команда `ruff format --check . contracts/python`: `466 files already formatted`, exit 0 |
| Інструменти лишилися працездатними | `scripts/tests/test_dev.py`: `31 passed in 12.68s` |
| Контракти валідні та сумісні | Лінтер контрактів у `just lint`; compat щодо інтеграції: `0 breaking, 0 warning(s)`; AST рівний |
| Власність WP-23 | Перевірка після коміту наведена нижче |

Сервісні пункти DoD про новий API, Dockerfile, конфігурацію й інтеграційні сценарії тут не застосовуються:
інкремент змінює форматування та охоплення вже наявної команди розробника.

## Справжній вивід перевірок

Журнали — `.jane/wp23c-*.txt` у власному checkout
`C:/repos/Jane/.claude/worktrees/wp23c`; `.jane/` і `.jane-wp` не комітяться.
Ruff: `0.16.9`, Python: `3.12.12` (uv workspace).

До правки, журнал `wp23c-before-storage.txt` (скорочено лише diff):

```text
$ C:/repos/Jane/.venv/Scripts/ruff.exe format --check contracts/python/src/jane_contracts/storage_adapter.py
1 file would be reformatted
exit=1
```

До правки, явне охоплення теки, журнал `wp23c-before-dir.txt`:

```text
$ C:/repos/Jane/.venv/Scripts/ruff.exe format --check contracts/python
1 file would be reformatted, 2 files already formatted
exit=1
```

Після правки, журнали `wp23c-format.txt`, `wp23c-lint.txt` (опущено лише абсолютний шлях виклику лінтера):

```text
$ uv run --all-packages ruff format --check contracts/python/src/jane_contracts/storage_adapter.py
1 file already formatted
exit=0

$ uvx --from rust-just just lint
$ uv run --all-packages ruff check .
All checks passed!
$ uv run --all-packages ruff format --check . contracts/python
466 files already formatted
$ uv run --all-packages python scripts/contracts_lint.py
[ok] JSON Schema meta-validation and $refs
[ok] OpenAPI 3.1 validation
[ok] Jane API conventions and inline examples
[ok] Standalone schema examples
[ok] Python interfaces compile
[ok] Mock server can serve every operation
[ok] Autonomous APIs do not reference orchestrator/assistant contracts
[skip] Redocly lint

Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=118, openapi_documents=8, openapi_examples=532, operations=118, python_files=3, schema_examples=46, schemas=16
All contract checks passed.
exit=0
```

Журнали `wp23c-unit.txt`, `wp23c-compat.txt`, `wp23c-ast.txt`:

```text
$ uv run --all-packages pytest scripts/tests/test_dev.py -q
...............................                                          [100%]
31 passed in 12.68s
exit=0

$ uv run --script contracts/tools/compat.py --base origin/codex/jane-integration
Base: origin/codex/jane-integration (24 contract files); working tree: 24 files; added: 0

0 breaking, 0 warning(s).
exit=0

AST equality: storage_adapter.py unchanged
exit=0
```

Після коміту коду `d5232ce`, журнал `wp23c-ownership.txt` (звіт уже враховано як новий файл):

```text
$ C:/repos/Jane/.venv/Scripts/python.exe .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
WP-23: 3 changed file(s), 0 outside ownership
exit=0
```

## Відомі обмеження й неперевірені інтеграції

Повні `just check` та e2e локально не запускалися відповідно до обов'язкових правил потоків.
Повний CI після злиття проводить координатор. Redocly та oasdiff окремо не запускалися;
зміни схем і OpenAPI відсутні. Нові тести не додавалися: малу зміну охоплення перевірено
реальним Ruff, а наявні тести команд розробника виконано повністю.

## Запити до інших власників

Немає. Журнал потоку `stream-c.md` і документацію C-1 цей інкремент не змінює.
