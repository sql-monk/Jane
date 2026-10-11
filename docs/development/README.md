# Розробка Jane

Розробка модуля починається з його контракту й власних шляхів. Спільні HTTP, помилки, конфігурація, jobs та idempotency реалізовані в [Jane Kit](../components/jane-kit/README.md).

## Середовище

```powershell
uv sync --all-packages
uv tool install rust-just
just test web-collector
```

`just check` виконує lint, types, unit і contract, як у CI. Docker-перевірки — `just integration`, `just isolation` і `just e2e`; вони мають окремі передумови. Команди та їхній склад реалізовані у [scripts/dev.py](../../scripts/dev.py).

## Новий модуль або пакет

```powershell
just new-service sample
```

Це створює scaffold із `templates/service`. Перед реалізацією зареєструй власність за правилами [плану](../../plan.md) і `jane-wp`, визнач контракт та необхідні залежності. Колектор або обробник повинен працювати без Orchestrator; підключення й ліміти надходять із конфігурації.

Для екстрактора почни з [мінімального пакета](../reference/packages/README.md). Для адаптера — з Protocol у `contracts/python` і модульної інструкції Storage. Власні сховища не читаються іншими сервісами напряму.

## Документація й контракти

Застосовуй [jane-documentation](../../.agents/skills/jane-documentation/SKILL.md), [стиль](documentation-style.md), [шаблони](documentation-templates/module.md) та [інструменти](documentation-tools.md). Draw.io-джерело й обидва прозорі PNG входять у зміну разом.

Зміни API потребують `jane-contracts`, сумісності, прикладів і незалежного contract-guardian. Оновлюй генерацію й ручні пояснення поруч зі зміною публічного члена. Не послаблюй тести для проходження перевірки.
