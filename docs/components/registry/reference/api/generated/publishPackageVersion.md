# publishPackageVersion

Опублікувати нову незмінну версію

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
POST /v1/packages/{package_id}/versions
```

## Опис із контракту

```text
Тіло — zip-архів пакета (`application/zip`, у корені `jane-package.json`) або JSON із
маніфестом і файлами (зручно для LLM-асистента). Репозиторій валідує маніфест за
`package-manifest.schema.json`, перевіряє файли, на які він посилається, залежності
(профіль runtime), шукає секрети, обчислює дайджест. Нова версія — `status: draft`.
```

## Доступ

```json
{
  "scope": "registry:write",
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
| `package_id` | `path` | так |
| `Idempotency-Key` | `header` | так |

```json
[
  {
    "in": "path",
    "name": "package_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "description": "Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований\nключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь\n(заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом —\n422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress`\n(retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`.\n",
    "example": "0b7d5c1e-3f7e-4a53-9d0e-5a0f5c0a9b11",
    "in": "header",
    "name": "Idempotency-Key",
    "required": true,
    "schema": {
      "maxLength": 255,
      "minLength": 1,
      "pattern": "^[\\x21-\\x7E]+$",
      "type": "string"
    }
  }
]
```

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "llmGenerated": {
          "value": {
            "files": {
              "schemas/product.schema.json": {
                "data": "{\"$schema\":\"https://json-schema.org/draft/2020-12/schema\",\"type\":\"object\",\"required\":[\"sku\"]}",
                "encoding": "utf-8"
              },
              "src/product_extractor/__init__.py": {
                "data": "",
                "encoding": "utf-8"
              },
              "src/product_extractor/main.py": {
                "data": "def extract(material, params, ctx):\n    ...\n",
                "encoding": "utf-8"
              },
              "tests/product-a100/expected.json": {
                "data": "{\"entities\":[]}",
                "encoding": "utf-8"
              },
              "tests/product-a100/page.html": {
                "data": "<html><h1>Kettle A-100</h1></html>",
                "encoding": "utf-8"
              }
            },
            "manifest": {
              "dependencies": {
                "python": [
                  "selectolax>=0.3,<0.4"
                ],
                "runtime_profile": "python-extractor@1"
              },
              "entry": {
                "callable": "extract",
                "module": "product_extractor.main",
                "runtime": "python"
              },
              "kind": "extractor",
              "output": {
                "entities": [
                  {
                    "entity_type": "product",
                    "key_fields": [
                      "sku"
                    ],
                    "schema": "schemas/product.schema.json"
                  }
                ]
              },
              "package_id": "shop-example.product-extractor",
              "provenance": {
                "based_on": {
                  "package_id": "shop-example.product-extractor",
                  "version": "1.2.0"
                },
                "change_summary": "Support .price-new selector.",
                "created_by": "llm"
              },
              "schema_version": "1",
              "tests": [
                {
                  "expected": "tests/product-a100/expected.json",
                  "expected_status": "success",
                  "input": {
                    "file": "tests/product-a100/page.html",
                    "media_type": "text/html"
                  },
                  "name": "product-a100"
                }
              ],
              "title": "Shop Example product cards",
              "version": "1.3.0"
            }
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/PublishRequest"
      }
    },
    "application/zip": {
      "schema": {
        "contentMediaType": "application/zip",
        "type": "string"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `201` | Версію опубліковано. | ні |
| `400` | Некоректний синтаксис запиту (`bad_request`). | так |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `403` | Пакет заборонено змінювати автоматично (`forbidden`, auto_changes_allowed=false і created_by=llm). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `409` | Версія вже існує (`version_exists`). | так |
| `413` | Тіло перевищує `limits.transfer.max_request_body_bytes` — передайте вміст як blob (`payload_too_large`). | так |
| `422` | Невалідний маніфест, `secret_detected`, `dependency_not_allowed`. | так |

```json
{
  "201": {
    "content": {
      "application/json": {
        "examples": {
          "version": {
            "$ref": "#/components/examples/PackageVersion"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/PackageVersion"
        }
      }
    },
    "description": "Версію опубліковано.",
    "headers": {
      "Location": {
        "$ref": "common.yaml#/components/headers/Location"
      }
    }
  },
  "400": {
    "content": {
      "application/problem+json": {
        "examples": {
          "bad": {
            "value": {
              "code": "bad_request",
              "detail": "request body is not valid JSON",
              "status": 400,
              "title": "Bad request",
              "type": "urn:jane:problem:bad_request"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Некоректний синтаксис запиту (`bad_request`)."
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
  "403": {
    "content": {
      "application/problem+json": {
        "examples": {
          "autoForbidden": {
            "value": {
              "code": "forbidden",
              "status": 403,
              "title": "Automatic changes are forbidden for this package",
              "type": "urn:jane:problem:forbidden"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Пакет заборонено змінювати автоматично (`forbidden`, auto_changes_allowed=false і created_by=llm)."
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
  },
  "409": {
    "content": {
      "application/problem+json": {
        "examples": {
          "exists": {
            "value": {
              "code": "version_exists",
              "status": 409,
              "title": "Version already exists",
              "type": "urn:jane:problem:version_exists"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Версія вже існує (`version_exists`)."
  },
  "413": {
    "content": {
      "application/problem+json": {
        "examples": {
          "tooLarge": {
            "value": {
              "code": "payload_too_large",
              "details": {
                "limit": 10485760
              },
              "status": 413,
              "title": "Payload too large",
              "type": "urn:jane:problem:payload_too_large"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Тіло перевищує `limits.transfer.max_request_body_bytes` — передайте вміст як blob (`payload_too_large`)."
  },
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "deps": {
            "value": {
              "code": "dependency_not_allowed",
              "errors": [
                {
                  "message": "requests is not available in runtime profile python-extractor@1",
                  "pointer": "/manifest/dependencies/python/0"
                }
              ],
              "status": 422,
              "title": "Dependency not allowed",
              "type": "urn:jane:problem:dependency_not_allowed"
            }
          },
          "secret": {
            "value": {
              "code": "secret_detected",
              "errors": [
                {
                  "code": "aws_access_key",
                  "message": "value looks like an AWS access key (line 12)",
                  "pointer": "/files/src~1product_extractor~1main.py"
                }
              ],
              "status": 422,
              "title": "Secret detected in package",
              "type": "urn:jane:problem:secret_detected"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Невалідний маніфест, `secret_detected`, `dependency_not_allowed`."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "registry:write"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/registry.v1.yaml#/components/schemas/PublishRequest](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PublishRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersion](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageVersion)
- [contracts/openapi/registry.v1.yaml#/components/examples/PackageVersion](../../../../../../contracts/openapi/registry.v1.yaml#/components/examples/PackageVersion)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
