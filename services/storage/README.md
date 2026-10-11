# Storage

Обробник збереження Jane: записує RAW-матеріали, сутності з історією й документи результатів у вибране сховище через адаптери (`handler.v1`) і віддає збережене через `storage.v1`. Адаптери — окремі пакети в [adapters](adapters/): `files`, `postgres`, `sqlserver`, `mongodb`, `minio`, `s3`.

Документація модуля — [docs/components/storage](../../docs/components/storage/README.md).

## Запуск

З кореня репозиторію (адаптери встановлюються як окремі пакети, тому `--all-packages`):

```powershell
uv sync --all-packages
uv run --all-packages python -m jane_storage
```

Сервіс слухає `http://127.0.0.1:8107` без автентифікації. Перший запис і читання з файловим адаптером — [швидкий старт](../../docs/components/storage/quickstart.md); змінні середовища — [конфігурація](../../docs/components/storage/configuration.md).

Образ із ядром і всіма адаптерами:

```powershell
docker build -f services/storage/Dockerfile -t jane-storage .
```

## Тести

```powershell
just test storage
```

Запускає тести ядра й адаптерів без зовнішніх сервісів, зокрема набір сумісності файлового адаптера. Набори сумісності інших адаптерів потребують dev-стеку — [як перевірити адаптер](../../docs/components/storage/adapters.md#як-перевірити-адаптер).

## Контракти

- Запис: [handler.v1.yaml](../../contracts/openapi/handler.v1.yaml); читання: [storage.v1.yaml](../../contracts/openapi/storage.v1.yaml).
- Протокол адаптера: [storage_adapter.py](../../contracts/python/src/jane_contracts/storage_adapter.py), сценарії сумісності — [storage-adapter.md](../../contracts/docs/storage-adapter.md).
