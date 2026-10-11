# Початок роботи

Як підготувати середовище й отримати перший перевірений результат Jane. Терміни — [глосарій](../overview/glossary.md).

## Зміст

- [Маршрути](#маршрути)
- [Передумови](#передумови)
- [Підготовка репозиторію](#підготовка-репозиторію)
- [Windows і Linux](#windows-і-linux)

## Маршрути

| Мета | Сторінка | Що потрібно |
|---|---|---|
| Побачити платформу в дії: від джерела до збережених сутностей | [Наскрізний сценарій](end-to-end.md) | Docker; близько 10 хвилин на першу збірку образів |
| Підняти всю платформу з Admin UI | [Платформа з Admin UI](platform.md) | Docker, Node.js для збірки адмінки |
| Запустити один модуль без Docker і Orchestrator | [Web Collector окремо](../../README.md#модуль-окремо-web-collector), `quickstart.md` модуля з [каталогу](../components/README.md) | лише uv |

## Передумови

| Інструмент | Версія | Навіщо |
|---|---|---|
| uv | будь-яка свіжа; перевірено 0.12.13 | Python 3.12 і залежності workspace (`.python-version`) |
| just | `rust-just`; без встановлення — `uvx --from rust-just just <рецепт>` | команди розробки з [justfile](../../justfile) |
| Docker з Compose v2 | перевірено Docker 29.8.0, Compose v5.5.1 | dev-стек і пісочниці екстракторів |
| Node.js і pnpm | Node.js 24 (`.node-version`), pnpm через corepack | лише для збірки Admin UI |

Встановлення just як інструмента uv:

```powershell
uv tool install rust-just
```

Рецепти `just` передають кожен рядок у `scripts/dev.py` без оболонки, тому однакові команди працюють у PowerShell і Bash.

## Підготовка репозиторію

Усі команди виконуються з кореня репозиторію.

1. Встановіть залежності всіх пакетів workspace:

   ```powershell
   uv sync --all-packages
   ```

2. Переконайтеся, що Docker запущено:

   ```powershell
   docker compose version
   ```

   Очікуваний результат — Compose версії 2 або новішої; у перевірочному запуску:

   ```text
   Docker Compose version v5.5.1
   ```

Згенеровані паролі, ключі API та файли стану стеків зберігаються в каталозі `.jane/` кореня репозиторію; він не потрапляє в Git.

## Windows і Linux

Інструкції розділу виконано 2026-10-11 на Windows 11 (Docker Desktop, PowerShell і Git Bash), ревізія `48389a3`. На Linux не перевірялися.

- Команди `uv`, `just` і Python однакові для обох систем.
- Там, де команда залежить від оболонки (читання JSON, HTTP-запит), наведено два підписані варіанти: PowerShell і Bash.
- Handler Runtime у контейнері звертається до Docker через сокет `/var/run/docker.sock`; інший шлях задає змінна `JANE_DOCKER_SOCKET`, групу сокета — `JANE_DOCKER_GID` (`deploy/profiles/stack.py` визначає її сам).
