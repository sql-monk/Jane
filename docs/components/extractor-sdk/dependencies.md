# Extractor SDK: залежності

## Мінімум

Python `>=3.12`. Дистрибутив `jane-extractor-sdk==0.1.0` не оголошує зовнішніх dependencies: основні механізми використовують стандартну бібліотеку.

## За сценарієм

| Сценарій | Залежності |
|---|---|
| Прямий виклик extract | SDK та власний код |
| HTML-екстрактор | Parser, оголошений залежністю вашого пакета |
| `testing.run_local` | Локальний маніфест, файли прикладів і залежності callable |
| Виконання у sandbox | [Handler Runtime](../handler-runtime/README.md) та його sandbox image |
| Встановлення опублікованого пакета | [Registry](../registry/README.md) або локальний archive/directory |

Відсутній import callable дає результат із error stage `import`; виняток всередині extract — stage `extract`.

## Заміна середовища

Власний застосунок може створити `Context` і викликати extract без HTTP. Для blob передайте `content_loader`, який надає вже завантажені й перевірені bytes. Контракт `extract(material, params, ctx)` зберігається при переході до Handler Runtime.
