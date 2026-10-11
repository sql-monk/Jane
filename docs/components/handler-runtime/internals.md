# Будова й дані Handler Runtime

Runtime поєднує PackageStore, ContentFetcher, Executor, ContractSchemas та SandboxBackend. HTTP-шар окремо додає ServiceState, JobRunner і ключі повторів.

## Класи

![Класи Runtime](../../diagrams/handler-runtime/classes.light.png)

[Темна тема](../../diagrams/handler-runtime/classes.dark.png) · [Draw.io](../../diagrams/handler-runtime/classes.drawio)

PreparedInvocation містить перевірені package/inputs/params/image/limits та invocation_id. LoadedPackage пов’язує manifest/root/digest; його read-only властивість ref повертає точне посилання. DockerSandbox/SubprocessSandbox реалізують один Protocol із різними гарантіями ізоляції.

## Алгоритм

![Алгоритм Runtime](../../diagrams/handler-runtime/execution-flow.light.png)

[Темна тема](../../diagrams/handler-runtime/execution-flow.dark.png) · [Draw.io](../../diagrams/handler-runtime/execution-flow.drawio)

Prepare перевіряє manifest, kind/runtime, network policy, profile, params та inputs, читає ContentRef і обчислює caps. Помилка тут є JaneError до запуску. Bundle готує SDK input; run утримує per-instance semaphore і викликає backend з wall/invocation timeouts.

Interpret перетворює exit/OOM/timeout/обсяг/порушення sandbox або неправильний output на HandlerResult.failed. Валідний runner output проходить перевірку схем сутностей; diagnostics містить причини й обмежений stderr. Пакет не формує HTTP-відповідь сам.

## Стани

![Стани Runtime](../../diagrams/handler-runtime/states.light.png)

[Темна тема](../../diagrams/handler-runtime/states.dark.png) · [Draw.io](../../diagrams/handler-runtime/states.drawio)

| Result status | Значення |
|---|---|
| success | Є витягнуті дані |
| empty | Розпізнано, даних немає |
| unrecognized | Не розпізнано структуру/частину входу |
| failed | Технічна помилка/порушення/невалідний output |

Job окремо має queued/running/cancelling/succeeded/failed/cancelled. Cancel звертається до backend.kill за invocation label; прийнятий cancel не є миттєвим підтвердженням зупинки.

## Власні дані

![Дані Runtime](../../diagrams/handler-runtime/data.light.png)

[Темна тема](../../diagrams/handler-runtime/data.dark.png) · [Draw.io](../../diagrams/handler-runtime/data.drawio)

ServiceState містить ResultStore, JobStore та IdempotencyStore. У PostgreSQL створюється own state_schema; results індексуються invocation_id. Job/result/key зв’язки на схемі логічні, а не заявлені SQL foreign keys.

Без state_dsn дані в пам’яті губляться при restart. PackageStore кешує за digest; кеш не є backup результатів або бізнес-сховищем. [Довідник типів](reference/types/README.md) містить декларації, правила помилок і приклади.
