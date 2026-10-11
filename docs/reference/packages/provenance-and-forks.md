# Походження й форки

Кожна версія пакета знає, хто її створив і з чого: це поле `provenance` маніфесту. Форк — незалежна копія чужого пакета з посиланням на батька (`fork_of`); зміни батька не впливають на форк і переносяться в нього лише явною командою користувача (ТЗ, розділ 7). API цих операцій — `registry.v1`, деталі запитів — [довідник API Registry](../../components/registry/reference/api/README.md).

## Зміст

- [Походження версії](#походження-версії)
- [Хто може публікувати автоматично](#хто-може-публікувати-автоматично)
- [Форк](#форк)
- [Порівняння версій](#порівняння-версій)
- [Нові версії батька](#нові-версії-батька)
- [Перенесення змін батька](#перенесення-змін-батька)

## Походження версії

| Поле `provenance` | Хто заповнює | Зміст |
|---|---|---|
| `created_by` | автор; Registry — для форку й перенесення | `human`, `llm` або `import` |
| `based_on` | автор | Попередня версія, з якої зроблено цю (`PackageRef`) |
| `change_summary` | автор | Що змінено й чому |
| `authors`, `created_at` | автор | Автори й час |
| `llm` | Assistant | Провайдер, модель, `assistant_job_id`, причина (`onboarding`, `improvement`, `unknown_material`, `upstream_port`) |
| `upstream_port` | Registry | Лише у версії, створеній перенесенням змін батька |

Registry зберігає `created_by` також окремим полем версії, а ім'я ключа, яким опублікували версію, — у `published_by`. Історія статусів (`status_history`) фіксує, хто й коли змінював статус.

## Хто може публікувати автоматично

Два механізми не дають LLM змінити пакет без дозволу:

- **Актор ключа.** Ключ API може мати атрибут `actor: llm` (у dev-стеку — ключ Assistant). Такий клієнт публікує лише версії з `provenance.created_by: llm`; інше — `403 forbidden`.
- **`auto_changes_allowed` пакета.** Якщо `false`, будь-яка версія з `created_by: llm` відхиляється з `403 forbidden` («Automatic changes are forbidden for this package»). Увімкнути `true` для пакета, де було `false`, може лише клієнт зі scope `registry:approve` (`PATCH /v1/packages/{id}`).

Реальна відповідь на публікацію LLM-версії в пакет з `auto_changes_allowed: false`:

```json
{
  "type": "urn:jane:problem:forbidden",
  "title": "Automatic changes are forbidden for this package",
  "status": 403,
  "detail": "automatic changes are forbidden for this package (auto_changes_allowed=false)",
  "instance": "/v1/packages/my.channel-rules/versions",
  "code": "forbidden",
  "retryable": false,
  "trace_id": "9e3459f92efab238261d2e049c331f9c"
}
```

## Форк

![Форк пакета й явне перенесення змін батька](../../diagrams/packages/fork-port.light.png#gh-light-mode-only)
![Форк пакета й явне перенесення змін батька](../../diagrams/packages/fork-port.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/packages/fork-port.light.png), [темне](../../diagrams/packages/fork-port.dark.png); джерело — [fork-port.drawio](../../diagrams/packages/fork-port.drawio).

Форк створює Registry командою `POST /v1/packages/{id}/forks`:

| Поле запиту | Обов'язкове | Зміст |
|---|---|---|
| `new_package_id` | так | Ідентифікатор нового пакета; має бути вільним |
| `from_version` | так | Версія батька, яку копіюють |
| `initial_version` | ні | Перша версія форку; типово — та сама, що `from_version` |
| `title` | ні | Назва; типово — назва батька |
| `auto_changes_allowed` | ні | Типово `false`: форк захищений від автоматичних змін |

Що робить Registry:

1. Копіює всі файли версії батька в новий пакет того самого `kind`, з описом і мітками батька.
2. У маніфесті змінює `package_id` і `version`, додає `fork_of` = `{package_id, version, digest}` батька й замінює `provenance`: `created_by` батька, `based_on` = `fork_of`, `change_summary` = `Fork of <батько>@<версія>.`
3. Публікує першу версію форку як звичайну нову версію (статус `draft`, усі перевірки публікації).

Наступні версії форку публікуються як звичайні, але `fork_of` у маніфесті має лишатися точно таким, як його задав Registry; звичайний пакет не може містити `fork_of`. Підключень і секретів форк не копіює — їх у пакеті немає. Форки пакета показує `GET /v1/packages?fork_of=<id>`, кількість — поле `forks_count` пакета.

## Порівняння версій

`GET /v1/packages/{id}/diff?to=<версія>[&from=<версія>][&context_lines=N]` порівнює дві версії:

- `from` за замовчуванням — найближча менша версія того самого пакета, а для першої версії форку — версія батька з `fork_of`;
- `parent:<версія>` у `from` чи `to` посилається на версію батька форку;
- `manifest_changes` — зміни `jane-package.json` як JSON Pointer з `op` `add`, `remove` або `replace` (об'єкти порівнюються за ключами, масиви — цілими);
- `files` — інші файли зі статусом `added`, `removed`, `modified`, `unchanged`; змінені текстові файли мають `unified_diff`, нетекстові — `binary: true`, а файли понад `diff.max_diff_file_bytes` — лише статус;
- `context_lines` обмежується `diff.max_context_lines` (типово 50).

Реальний diff версії форку, створеної перенесенням змін (`from=1.1.0&to=1.2.0&context_lines=1`; уривок — без файлів зі статусом `unchanged`):

```json
{
  "from": {"package_id": "my.price-extractor", "version": "1.1.0", "digest": "sha256:e3fc5c5fc1d2822f346d3665d0b30720a29f8d9a705766c113ec7ab6a6e7dcb5"},
  "to": {"package_id": "my.price-extractor", "version": "1.2.0", "digest": "sha256:e34c2e925d47a2c5c8c9e04651ca7fdfb7ae99ded63f5255a8717e83a17f2145"},
  "manifest_changes": [
    {"pointer": "/provenance/based_on/digest", "op": "add", "new": "sha256:e3fc5c5fc1d2822f346d3665d0b30720a29f8d9a705766c113ec7ab6a6e7dcb5"},
    {"pointer": "/provenance/based_on/version", "op": "replace", "old": "1.0.0", "new": "1.1.0"},
    {"pointer": "/provenance/change_summary", "op": "replace", "old": "Default currency USD.", "new": "Ported changes of examples.testsite-price-extractor 1.0.0 -> 1.1.0 into 1.1.0."},
    {"pointer": "/provenance/upstream_port", "op": "add", "new": {"parent_version": "1.1.0", "requested_by": "anonymous"}},
    {"pointer": "/version", "op": "replace", "old": "1.1.0", "new": "1.2.0"}
  ],
  "files": [
    {
      "path": "src/jane_example_price/main.py",
      "status": "modified",
      "unified_diff": "--- my.price-extractor@1.1.0/src/jane_example_price/main.py\n+++ my.price-extractor@1.2.0/src/jane_example_price/main.py\n@@ -17,3 +17,3 @@\n \n-AVAILABILITY = {\"InStock\": \"in_stock\", \"OutOfStock\": \"out_of_stock\", \"PreOrder\": \"preorder\"}\n+AVAILABILITY = {\"InStock\": \"in_stock\", \"OutOfStock\": \"out_of_stock\", \"PreOrder\": \"preorder\", \"SoldOut\": \"out_of_stock\"}\n \n"
    }
  ]
}
```

## Нові версії батька

`GET /v1/packages/{id}/upstream` для форку показує, чи з'явилися в батька нові версії:

| Поле | Зміст |
|---|---|
| `fork_of` | Батько й вихідна версія |
| `last_ported_version` | Найбільша версія батька, вже наявна у форку: `fork_of.version` або `upstream_port.parent_version` його версій |
| `parent_latest_version` | Остання версія батька (без `rejected` і `yanked`) |
| `newer_parent_versions` | Версії батька, новіші за `last_ported_version` (без `rejected` і `yanked`) |

Для пакета, що не є форком, — `409 conflict`. Registry нічого не переносить сам: цей запит лише інформує користувача або Admin UI.

## Перенесення змін батька

`POST /v1/packages/{id}/upstream-ports` — явна команда перенести зміни версії батька у форк. Це асинхронна операція: відповідь `202` з job `upstream_port` і заголовком `Location: /v1/jobs/{job_id}`; результат — у `GET /v1/jobs/{job_id}`.

| Поле запиту | Обов'язкове | Зміст |
|---|---|---|
| `parent_version` | так | Версія батька, зміни якої переносяться |
| `new_version` | так | Номер нової версії форку; має бути вільним |
| `base_version` | ні | Версія форку, у яку переносять; типово — `latest_version` форку |

Registry виконує тристороннє злиття ([merge.py](../../../services/registry/src/jane_registry/merge.py)):

- **base** — версія батька, востаннє перенесена в `base_version` (`upstream_port.parent_version` або `fork_of.version`);
- **ours** — файли `base_version` форку;
- **theirs** — файли `parent_version` батька.

Правила злиття:

- файл змінено лише з одного боку — береться змінений; однакова зміна з обох боків — береться один раз;
- текстовий файл змінено з обох боків — злиття за рядками; перекриття змін — конфлікт;
- двійковий файл змінено з обох боків, зміна з одного боку й видалення з іншого, текстовий файл понад `diff.max_merge_file_bytes` — конфлікт;
- маніфест зливається як JSON за ключами; `package_id`, `version`, `fork_of`, `provenance` завжди беруться з форку.

Без конфліктів Registry публікує нову версію форку (`draft`) з `provenance.created_by` = актор клієнта, `based_on` = `base_version` форку та `upstream_port` = `{parent_version, requested_by}`; job стає `succeeded`, а `result` містить `PackageVersion`. Власні зміни форку зберігаються: у прикладі вище форк мав типову валюту `USD`, і після перенесення вона лишилася.

Якщо є хоч один конфлікт, нічого не публікується: job стає `failed` з помилкою `upstream_conflict`. Реальний `error` такого job:

```json
{
  "type": "urn:jane:problem:upstream_conflict",
  "title": "Upstream changes conflict with the fork",
  "status": 409,
  "detail": "1 conflict(s) while porting examples.testsite-price-extractor@1.2.0",
  "code": "upstream_conflict",
  "retryable": false,
  "trace_id": "0b999ca64b98c34e22dcccbba662baa2",
  "details": {
    "conflicts": [{"path": "src/jane_example_price/main.py", "reason": "1 conflicting hunk(s)"}],
    "merge_base": "1.1.0",
    "parent_version": "1.2.0",
    "base_version": "1.3.0"
  }
}
```

Конфлікт розв'язують вручну: публікують нову версію форку з потрібними змінами. Job можна скасувати (`POST /v1/jobs/{job_id}/cancel`); скасування перевіряється перед публікацією, тож скасоване перенесення версії не створює.
