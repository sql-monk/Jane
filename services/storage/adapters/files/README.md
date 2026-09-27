# jane-storage-files — файловий адаптер збереження

Адаптер `filesystem` для сервісу storage (WP-07). Реєструється в ядрі через entry points
(`jane.storage.adapters` → `filesystem`, `jane.storage.packages` → `jane.storage-files`); опис механізму —
[services/storage/README.md](../../README.md#адаптери).

## Підключення

```json
{"connection_id": "raw-files", "kind": "filesystem", "params": {"base_path": "/var/lib/jane/storage"}}
```

Параметри етапу (`schemas/params.schema.json` пакета `jane.storage-files`): `prefix` — підкаталог усередині
`base_path`; `format.raw` = `original | html | json` (типово `original`: вебсторінка `text/html` → `.html`);
`format.entities` = `json | jsonl` (історія сутностей — файл на версію або JSON Lines).

## Розкладка й атомарність

| Шлях (від `base_path/prefix`) | Вміст |
|---|---|
| `entities/<entity_type>/<sha256(canonical_key)>.json` | актуальний стан (`EntitySnapshot`) |
| `history/<entity_type>/<sha256>/<version:012d>.json` або `history/<entity_type>/<sha256>.jsonl` | історія |
| `deliveries/<sha256(delivery_key)>.json` | запис доставки |
| `objects/<object_key>` і `…meta.json` | RAW/документ і його метадані |
| `index/objects/<object_id>.json` | `object_id` → `object_key` |
| `locks/…` | файли-блокування |

- Документи пишуться у тимчасовий файл у тому самому каталозі, `fsync`, потім `os.replace` — однаково на Windows
  і Linux; на Windows заміна повторюється, поки файл тримає читач (`replace_retry_ms`).
- Створення «лише якщо немає» — `os.link` повністю записаного тимчасового файла (без часткових файлів);
  де жорсткі посилання недоступні — `O_CREAT | O_EXCL`.
- `commit_entity` і `put_object` виконуються під файлом-блокуванням на ключ (`O_CREAT | O_EXCL`); блокування,
  старіше за `lock_stale_ms` (впав процес), знімається.
- Порядок коміту: запис доставки → подія історії → знімок. Запис доставки, який знімок/історія не
  підтверджують (збій посередині), вважається незавершеним і переробляється.

## Ліміти адаптера

| Параметр | Типово | Де задається |
|---|---|---|
| `lock_timeout_ms` | 30000 | `params` підключення або `JANE_STORAGE_LIMITS__ADAPTERS__LOCK_TIMEOUT_MS` |
| `lock_stale_ms` | 120000 | те саме (`…__LOCK_STALE_MS`) |
| `lock_poll_ms` | 10 | те саме (`…__LOCK_POLL_MS`) |
| `replace_retry_ms` | 5000 | те саме (`…__REPLACE_RETRY_MS`) |

## Тести

`just test storage` (набір сумісності C-01…C-16 — `tests/test_compat.py`, плюс специфічні тести
блокувань і відновлення після збою — `tests/test_files_adapter.py`).
