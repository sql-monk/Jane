# testsite_products.main

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [testsite_products.main.AVAILABILITY](#testsite_productsmainavailability)
- [testsite_products.main.extract](#testsite_productsmainextract)

## testsite_products.main.AVAILABILITY

**Константа.** Код: [libs/extractor-sdk/examples/testsite-product-extractor/src/testsite_products/main.py:16](../../../../../../libs/extractor-sdk/examples/testsite-product-extractor/src/testsite_products/main.py#L16).

```python
AVAILABILITY = {'InStock': 'in_stock', 'OutOfStock': 'out_of_stock'}
```

## testsite_products.main.extract

**Функція.** Код: [libs/extractor-sdk/examples/testsite-product-extractor/src/testsite_products/main.py:81](../../../../../../libs/extractor-sdk/examples/testsite-product-extractor/src/testsite_products/main.py#L81).

```python
def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Material` | `—` | positional-or-keyword |
| `params` | `dict[str, Any]` | `—` | positional-or-keyword |
| `ctx` | `Context` | `—` | positional-or-keyword |

Результат: `ExtractResult`.
