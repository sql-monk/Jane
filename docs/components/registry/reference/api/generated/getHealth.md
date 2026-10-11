# getHealth

Стан сервісу (liveness/readiness)

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/health
```

## Доступ

```json
{
  "scope": [],
  "security": []
}
```

## Параметри

Параметрів у контракті немає.

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сервіс працює (ok або degraded). | ні |
| `503` | Сервіс не готовий. | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "ok": {
            "value": {
              "checks": {
                "state_store": {
                  "status": "ok"
                }
              },
              "status": "ok"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Health"
        }
      }
    },
    "description": "Сервіс працює (ok або degraded)."
  },
  "503": {
    "content": {
      "application/json": {
        "examples": {
          "down": {
            "value": {
              "checks": {
                "state_store": {
                  "message": "connection refused",
                  "status": "down"
                }
              },
              "status": "down"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Health"
        }
      }
    },
    "description": "Сервіс не готовий."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-health": true,
  "x-jane-scope": []
}
```

## Схеми

- [contracts/openapi/common.yaml#/components/schemas/Health](../../../../../../contracts/openapi/common.yaml#/components/schemas/Health)
