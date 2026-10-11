# WP-19a. Рецепт storage-адаптера після C-2

**Гілка:** `wp/19a-storage-workspace-docs` · **База й ревізія перевірених manifests:**
`58405428bd8b4ac7fd8e8f26577a921af3255d9a` (`origin/codex/jane-integration`) · **Стан:** готово до злиття координатором.

Виконано документальний запит власнику storage, зафіксований у
[stream-c.md](../post-m3/stream-c.md#c-2-accepted-і-злито) після прийнятого C-2
(merge `fdad2106c0fb6531639d1071d720a990a646b0b7`).

У [services/storage/README.md](../../../services/storage/README.md) з TOML-рецепта нового адаптера вилучено
лише локальний `jane-contracts = { path = "../../../../contracts/python", editable = true }`.
`jane-storage = { path = "../..", editable = true }` збережено. Додано коротке пояснення успадкування
`jane-contracts = { workspace = true }` з кореня й relative link до
[DEVELOPMENT.md](../../../DEVELOPMENT.md).

Звірено actual root `pyproject.toml` і всі шість прийнятих manifests storage-адаптерів:
`contracts/python` є членом workspace, `jane-contracts` заданий у root sources, адаптери не мають
локального override й зберігають path source `jane-storage`. README тепер відповідає цим manifests.

Власність інкремента — тільки `services/storage/README.md` та цей новий звіт.
Manifests, контракти, код і попередні accepted-звіти не змінювалися; frozen checkout WP-19 не редагувався.
Повторних tests, gates, full check/e2e, Docker, reviewer та guardian немає: це docs-only зміна за
[спільними правилами](../post-m3/README.md#спільні-правила-для-всіх-потоків).

## Реальні команди й вивід

Початкові `git fetch origin` і `git worktree add -b wp/19a-storage-workspace-docs
C:/repos/Jane/.claude/worktrees/wp19a origin/codex/jane-integration` завершилися з exit 0;
створено окремий checkout на наведеній базі, `.jane-wp=19`.
Сирі докази наступних команд — `.jane/wp19a-*.txt` у цьому checkout.

```text
$ python .jane/wp19a-inspect.py
root workspace member: contracts/python = True
root jane-contracts source: {'workspace': True}
services/storage/adapters/files/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
services/storage/adapters/minio/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
services/storage/adapters/mongodb/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
services/storage/adapters/postgres/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
services/storage/adapters/s3/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
services/storage/adapters/sqlserver/pyproject.toml: jane-contracts local source = None; jane-storage = {'path': '../..', 'editable': True}
README old jane-contracts path override occurrences: 0
README jane-storage path source preserved: True
README ../../DEVELOPMENT.md resolves to existing root file: True
EXIT_CODE=0
```

```text
$ git diff --check
EXIT_CODE=0
```

```text
$ python .claude/hooks/jane_wp.py check-diff origin/codex/jane-integration
WP-19: 2 changed file(s), 0 outside ownership
EXIT_CODE=0
```

## Запити до інших власників

Координатор потоку A зливає цей docs-only інкремент в integration; запит C-2 до власника storage виконано.
Фінальний CI потоку A залишається за координатором після full CI B/C і C-4.
