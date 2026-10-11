# DOC-08 — Експлуатація та відновлення

Статус: review. Автор: координатор. Основа: `91876d1`, 2026-10-11; Windows 11, Python 3.12, Docker 29.8.0, Linux containers. Застосовано jane-documentation.

## Результат

Створено огляд експлуатації, діагностику, порядок оновлення та узгодженого резервування. [Виконуваний приклад](../../operations/examples/backup_restore.py) перевіряє дані окремого тестового проєкту; production-дані не використовує.

## Реальна репетиція

Виконано backup/restore для ізольованого `jane-docs-20261011`. Writer-сервіси й MinIO зупинено до копіювання; відновлення виконано у нові тестові бази й клони томів. Порівняно SHA-256 упорядкованого вмісту кожної таблиці та кожного файла, після цього клони видалено, початкові процеси відновлено.

```powershell
uv run --all-packages python docs/operations/examples/backup_restore.py --project jane-docs-20261011
```

Фактичний стислий результат:

```text
handler_runtime: 3 tables, 75 rows, data_equal: true
orchestrator: 14 tables, 160 rows, data_equal: true
registry: 7 tables, 57 rows, data_equal: true
llm: 7 tables, 2 rows, data_equal: true
assistant: 3 tables, 0 rows, data_equal: true
storage_results: 4 tables, 67 rows, data_equal: true
minio: 33 files, data_equal: true
storage: 112 files, data_equal: true
telegram: 1 file, data_equal: true
web: 1 file, data_equal: true
ok: true
```

Повний machine-readable доказ записано у `.jane/documentation-backups/jane-docs-20261011/verification.json`; dump і tar містять тестові дані й залишаються git-ignored. Приклад перевіряє regex назви `jane-docs-*` і Compose-label ресурсу перед операцією.

## Межі доказу

Це фактичне відновлення даних тестового стенду, а не перевірка довільної production-інфраструктури або відкату несумісної схеми. Зовнішні SQL Server/MongoDB/S3, provider credentials і реальні Telegram-сесії не використовувалися. Статичний Markdown і відображення сторінок входять до спільного фінального DOC-03/DOC-11 gate. Незалежне приймання ще не завершене.
