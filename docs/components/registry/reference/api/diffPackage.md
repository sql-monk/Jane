# GET /v1/packages/{package_id}/diff

> Згенеровано `scripts/docs_reference.py` з [registry.v1.yaml](../../../../../contracts/openapi/registry.v1.yaml#L622). Не редагуйте вручну.

**Відмінності між версіями або від батька (для форку)**

| Властивість | Значення |
|---|---|
| operationId | `diffPackage` |
| Метод і шлях | `GET /v1/packages/{package_id}/diff` |
| Scope | `registry:read` |
| Ідемпотентність | — |
| Теги | versions, forks |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `package_id` | path | `string` | так |  |
| `from` | query | `string` | ні | Версія цього пакета; або `parent:<version>` — версія батька. |
| `to` | query | `string` | так |  |
| `context_lines` | query | `integer` | ні |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Відмінності. | `PackageDiff` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `from` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `from.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `from.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `from.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `to` | `package-ref` | так | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `to.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `to.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `to.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `manifest_changes` | array of `object` | ні |  |
| `manifest_changes[].pointer` | `string` | так |  |
| `manifest_changes[].op` | enum: `add`, `remove`, `replace` | так |  |
| `manifest_changes[].old` | — | ні |  |
| `manifest_changes[].new` | — | ні |  |
| `files` | array of `object` | так |  |
| `files[].path` | `string` | так |  |
| `files[].status` | enum: `added`, `removed`, `modified`, `unchanged` | так |  |
| `files[].unified_diff` | `string` | ні |  |
| `files[].binary` | `boolean` | ні |  |

Приклад `diff`:

```json
{
  "from": {
    "package_id": "shop-example.product-extractor",
    "version": "1.1.0"
  },
  "to": {
    "package_id": "shop-example.product-extractor",
    "version": "1.2.0"
  },
  "manifest_changes": [
    {
      "pointer": "/provenance/change_summary",
      "op": "replace",
      "old": "Initial version.",
      "new": "Fallback to og:title when h1 is missing."
    }
  ],
  "files": [
    {
      "path": "src/product_extractor/main.py",
      "status": "modified",
      "unified_diff": "@@ -10,3 +10,5 @@\n-    title = h1.text()\n+    title = h1.text() if h1 else og_title(tree)\n"
    },
    {
      "path": "tests/og-title/page.html",
      "status": "added"
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
