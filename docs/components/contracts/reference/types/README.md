# Типи й члени: jane-contracts

> Згенеровано `scripts/docs_reference.py` з [contracts/python/src/jane_contracts](../../../../../contracts/python/src/jane_contracts). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_contracts`](jane_contracts.md) | 0 | 0 | Jane internal interface contracts (plan.md WP-00). |
| [`jane_contracts.discovery`](jane_contracts.discovery.md) | 9 | 0 | Material discovery strategy contract for the Web Collector. |
| [`jane_contracts.storage_adapter`](jane_contracts.storage_adapter.md) | 13 | 1 | Storage adapter contract for the storage handler. |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`AdapterError`](jane_contracts.storage_adapter.md#клас-adaptererror) | виняток | `jane_contracts.storage_adapter` |
| [`CommitOutcome`](jane_contracts.storage_adapter.md#клас-commitoutcome) | перелік | `jane_contracts.storage_adapter` |
| [`CommitResult`](jane_contracts.storage_adapter.md#клас-commitresult) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`DeliveryRecord`](jane_contracts.storage_adapter.md#клас-deliveryrecord) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`DiscoveredMaterial`](jane_contracts.discovery.md#клас-discoveredmaterial) | dataclass (незмінний) | `jane_contracts.discovery` |
| [`DiscoveredUrl`](jane_contracts.discovery.md#клас-discoveredurl) | dataclass (незмінний) | `jane_contracts.discovery` |
| [`DiscoveryContext`](jane_contracts.discovery.md#клас-discoverycontext) | протокол | `jane_contracts.discovery` |
| [`DiscoveryStrategy`](jane_contracts.discovery.md#клас-discoverystrategy) | протокол | `jane_contracts.discovery` |
| [`EntityDiscoveryAdapter`](jane_contracts.storage_adapter.md#клас-entitydiscoveryadapter) | протокол | `jane_contracts.storage_adapter` |
| [`EntitySnapshot`](jane_contracts.storage_adapter.md#клас-entitysnapshot) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`FetchedResource`](jane_contracts.discovery.md#клас-fetchedresource) | dataclass (незмінний) | `jane_contracts.discovery` |
| [`FetchRejected`](jane_contracts.discovery.md#клас-fetchrejected) | виняток | `jane_contracts.discovery` |
| [`HistoryEvent`](jane_contracts.storage_adapter.md#клас-historyevent) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`LinkSelector`](jane_contracts.discovery.md#клас-linkselector) | dataclass (незмінний) | `jane_contracts.discovery` |
| [`ObjectRecord`](jane_contracts.storage_adapter.md#клас-objectrecord) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`order_tuple`](jane_contracts.storage_adapter.md#функція-order_tuple) | функція | `jane_contracts.storage_adapter` |
| [`OrderKey`](jane_contracts.storage_adapter.md#клас-orderkey) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`RawObject`](jane_contracts.storage_adapter.md#клас-rawobject) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`RefreshingStrategy`](jane_contracts.discovery.md#клас-refreshingstrategy) | протокол | `jane_contracts.discovery` |
| [`ResolvedConnection`](jane_contracts.storage_adapter.md#клас-resolvedconnection) | dataclass (незмінний) | `jane_contracts.storage_adapter` |
| [`StorageAdapter`](jane_contracts.storage_adapter.md#клас-storageadapter) | протокол | `jane_contracts.storage_adapter` |
| [`StorageStatisticsAdapter`](jane_contracts.storage_adapter.md#клас-storagestatisticsadapter) | протокол | `jane_contracts.storage_adapter` |
| [`StrategyRegistry`](jane_contracts.discovery.md#клас-strategyregistry) | протокол | `jane_contracts.discovery` |
