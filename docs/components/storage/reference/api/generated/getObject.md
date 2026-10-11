# getObject

Метадані збереженого об'єкта і відновлений Material для повторної обробки

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/objects/{object_id}
```

## Опис із контракту

```text
Для RAW — відновлений Material для повторної обробки. Вміст залежить від формату збереження
(`format.raw` пакета, `contracts/docs/storage-adapter.md`, «Формати RAW»): `html` / `original` —
постійне посилання адаптера на ті самі байти (`file://` чи `s3://`, `store: persistent`) або inline
до `limits.transfer.inline_max_bytes`; `json` (документ Material із вбудованим вмістом) — початковий
вміст, вийнятий із документа, inline до `limits.transfer.inline_max_bytes`. Більший за ліміт вміст без
постійного посилання (`json`, а також адаптери без blob-URI: PostgreSQL, MongoDB, SQL Server) віддається
транзитним blob самого storage (`store: transit`, `expires_at` = зараз + `limits.transfer.transit_ttl_seconds`,
ADR-0004 §2), якщо в розгортанні налаштовано його транзитне сховище; без нього `material` відсутній
(байти — `getObjectContent`).
```

## Доступ

```json
{
  "scope": "storage:read",
  "security": [
    {
      "bearerAuth": []
    }
  ]
}
```

## Параметри

| Ім’я | Розміщення | Обов’язковий |
|---|---|---|
| `object_id` | `path` | так |
| `connection_id` | `query` | так |

```json
[
  {
    "in": "path",
    "name": "object_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  },
  {
    "in": "query",
    "name": "connection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Об'єкт і, для RAW, Material із посиланням на вміст (або inline-вмістом). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "raw": {
            "value": {
              "material": {
                "collector": {
                  "name": "web-collector",
                  "version": "0.1.0"
                },
                "content": {
                  "expires_at": null,
                  "kind": "blob",
                  "media_type": "text/html",
                  "sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
                  "size_bytes": 151,
                  "store": "persistent",
                  "uri": "file:///var/lib/jane/raw/shop-example/2026/09/27/web_9b1f0c1d/obs_01J9ZQ4A0000000000000001.html"
                },
                "fetched_at": "2026-09-27T10:00:05Z",
                "format": {
                  "media_type": "text/html"
                },
                "locator": {
                  "url": "https://shop.example.test/product/a-100"
                },
                "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
                "observation_id": "obs_01J9ZQ4A0000000000000001",
                "revision": {
                  "content_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
                },
                "source": {
                  "kind": "web",
                  "source_id": "shop-example"
                }
              },
              "object": {
                "adapter": "filesystem",
                "connection_id": "raw-files",
                "media_type": "text/html",
                "object_id": "obj_01J9ZQ4C00000000000000D1",
                "size_bytes": 151
              },
              "stored_at": "2026-09-27T10:00:07Z"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/StoredObjectDetail"
        }
      }
    },
    "description": "Об'єкт і, для RAW, Material із посиланням на вміст (або inline-вмістом)."
  },
  "401": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unauthenticated": {
            "value": {
              "code": "unauthenticated",
              "status": 401,
              "title": "Unauthenticated",
              "type": "urn:jane:problem:unauthenticated"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Немає або недійсний токен (`unauthenticated`)."
  },
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notFound": {
            "$ref": "#/components/examples/ProblemNotFound"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Ресурс не знайдено (`not_found`)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "storage:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/storage.v1.yaml#/components/schemas/StoredObjectDetail](../../../../../../contracts/openapi/storage.v1.yaml#/components/schemas/StoredObjectDetail)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
