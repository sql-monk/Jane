# jane-extractor-sdk

Бібліотека для авторів екстракторів Jane на Python: функція `extract(material, params, ctx)`, помічники результату `success`, `empty`, `unrecognized`, `entity`, контекст і локальні тести. Залежить лише від стандартної бібліотеки; встановлена в образ пісочниці Handler Runtime.

Повна документація модуля — [docs/components/extractor-sdk](../../docs/components/extractor-sdk/README.md): [швидкий старт](../../docs/components/extractor-sdk/quickstart.md), [інтеграція](../../docs/components/extractor-sdk/integration.md), [будова й протокол раннера](../../docs/components/extractor-sdk/internals.md).

Приклад пакета — [examples/testsite-product-extractor](examples/testsite-product-extractor/jane-package.json). Тести SDK: `just test extractor-sdk`.
