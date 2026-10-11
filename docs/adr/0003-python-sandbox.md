# ADR-0003 — Python у контейнерній пісочниці

Дата: 2026-10-11. Основа: `91876d1`. Стан: опис реалізованого рішення; новий текст у review.

## Проблема

Екстрактор містить код користувача або LLM. ТЗ §11 вимагає обмежити його ресурси й доступи та повертати діагностику помилок.

## Розглянуті підходи

| Підхід | Наслідок |
|---|---|
| Виконання в процесі сервісу | Спільні права, пам’ять і життєвий цикл |
| Окремий процес без ізоляції | Окреме завершення, але доступи вузла лишаються |
| Контейнер із профілем | Контроль доступів і ресурсів; потрібен container engine |

## Рішення

Docker backend створює окремий контейнер на invocation. Профіль визначає образ Python і дозволені бібліотеки. Мережа вимкнена, root filesystem лише для читання, користувач без root, capabilities скинуті; CPU, RAM, процеси, час і вихід обмежені `limits.sandbox`.

## Наслідки

Пакет працює у визначеному середовищі. Довільний доступ до мережі та встановлення залежностей під час запуску не випливають із маніфеста. Runtime має привілей керування engine й потребує відповідного захисту вузла.

## Докази

[Docker backend](../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py) · [profiles](../../services/handler-runtime/src/jane_handler_runtime/profiles/) · [sandbox image](../../services/handler-runtime/sandbox/python-extractor-1/Dockerfile) · [manifest dependencies](../../contracts/schemas/package-manifest.schema.json).

Межа реалізації: [C-02](../architecture/conformance.md#c-02--залежності-й-мережа-python-пакета).
