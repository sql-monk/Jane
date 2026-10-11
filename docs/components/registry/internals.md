# Будова й дані Registry

[app.py](../../../services/registry/src/jane_registry/app.py) передає роботу RegistryService. Доменний сервіс залежить від protocol stores, PackageValidator і ProfileSource, а не від FastAPI.

## Класи

![Класи Registry](../../diagrams/registry/classes.light.png)

[Темна тема](../../diagrams/registry/classes.dark.png) · [Draw.io](../../diagrams/registry/classes.drawio)

MetadataStore реалізують MemoryStore/PostgresStore; BlobStore — FileBlobStore/S3BlobStore. PackageRecord описує змінні метадані, VersionRecord — digest, manifest і файли точної версії. Декларації — в [довіднику](reference/types/README.md).

## Власні дані

![Дані Registry](../../diagrams/registry/data.light.png)

[Темна тема](../../diagrams/registry/data.dark.png) · [Draw.io](../../diagrams/registry/data.drawio)

[postgres.py](../../../services/registry/src/jane_registry/postgres.py) створює registry_packages, registry_versions, registry_status_history, registry_test_reports та marker міграцій. Job і ключі повторів Jane Kit використовують ту саму власну БД. Blob key має форму prefix+sha256 hex.

Діаграма показує логічні зв’язки. Latest визначається найвищим SemVer серед версій, які не rejected/yanked; це не гарантує approved. Build metadata SemVer не змінює порядок.

## Алгоритм публікації

![Алгоритм Registry](../../diagrams/registry/publish-flow.light.png)

[Темна тема](../../diagrams/registry/publish-flow.dark.png) · [Draw.io](../../diagrams/registry/publish-flow.drawio)

Перевіряються шляхи й розмір ZIP/JSON, manifest та його семантика, файли/тести, права, номер версії, секрети й залежності. Потім створюється канонічний ZIP, записується blob і draft version, оновлюється каталог. Великий файл не приймається без secret scan. Наявність tests у manifest не є виконаним TestReport.

## Статуси

![Статуси Registry](../../diagrams/registry/states.light.png)

[Темна тема](../../diagrams/registry/states.dark.png) · [Draw.io](../../diagrams/registry/states.drawio)

draft → approved/rejected/deprecated/yanked; approved → deprecated/yanked; deprecated → approved/yanked. Rejected та yanked кінцеві. Історія зберігає час, автора й причину; concurrent зміна дає conflict.

## Форки

Форк має незалежний package_id, parent і вихідну версію. Оновлення parent лише відображається в upstream status. Prepare_port порівнює base/parent/local і планує тристороннє злиття; conflict блокує застосування. Apply_port публікує нову версію явною командою, не переписує існуючу й не активує task.
