# ADR-0003. Пісочниця для Python-коду екстракторів

**Статус:** прийнято (WP-00, 2026-09-27)

## Контекст
ТЗ §11: виконання коду обмежується за часом, ресурсами й доступами; код екстракторів може
створювати LLM, тобто він недовірений. WP-06: обмеження часу, пам'яті й CPU, мережа вимкнена за
замовчуванням, без секретів, примусова зупинка при зависанні; має працювати на **Windows і Linux**
(plan.md §9: виконання — в контейнері; ізоляцію перевіряють тести WP-06 у CI на Linux).

## Рішення
**Один контейнер на виклик (або на пакет тестів) через API Docker Engine / Podman**, який
керує handler-runtime. Абстракція `SandboxBackend` у WP-06 з реалізаціями:

| Backend | Коли | Ізоляція |
|---|---|---|
| `docker` (типовий) | dev на Windows (Docker Desktop, Linux-контейнери) і Linux | Linux namespaces + cgroups |
| `docker` + `runtime: runsc` (gVisor) | прод на Linux за бажанням | + ізоляція ядра |
| `podman` (rootless) | Linux без root-демона | те саме API |
| `subprocess` | **лише** локальні unit-тести SDK на довірених пакетах; вимкнено за замовчуванням, у прод заборонено | немає |

Параметри контейнера (усі числа — з `limits.sandbox` і `limits.timeouts`, ADR не фіксує значень):
- образ профілю runtime (`python-extractor@1`: Python 3.12, SDK екстракторів, дозволені бібліотеки —
  lxml, selectolax, beautifulsoup4, parsel, jsonpath-ng, python-dateutil тощо; перелік публікує WP-06);
  образ за дайджестом, без встановлення пакетів під час виконання;
- `--network none` (для `access.network=allowlist` — окрема мережа з egress-проксі, лише якщо
  платформа дозволяє; у v1 не обов'язково);
- `--read-only`, `tmpfs` для `/tmp` (`tmpfs_mb`), пакет змонтовано read-only;
- `--memory` (`memory_mb`), `--cpus` (`cpu_cores`), `--pids-limit` (`max_processes`);
- `--user` не root, `--cap-drop ALL`, `--security-opt no-new-privileges`, типовий seccomp;
- без змінних середовища з секретами, без томів хоста, крім пакета й вводу;
- вхід (Material, params) — через stdin/файл, вихід — JSON у stdout, обрізаний до `max_output_bytes`;
- wall-time (`wall_time_ms`): після нього `docker kill`, результат `failed` з `failure.kind = timeout`;
  OOM → `resource_exceeded`; спроба мережі → помилка в коді (`sandbox_violation` у діагностиці).

Доступ runtime до Docker API — через сокет або socket-proxy з мінімальними правами; у прод
рекомендовано rootless Podman або окремий вузол для runtime.

## Наслідки
- Однакова поведінка на Windows і Linux, бо код завжди виконується в Linux-контейнері.
- Запуск контейнера додає затримку (сотні мс); WP-06 може тримати пул теплих контейнерів, але
  кожен виклик — у чистому процесі без стану попереднього.
- handler-runtime потребує контейнерного рушія (зафіксовано в карті автономності).
- Перевірки ізоляції (зависання, мережа, пам'ять) — у тестах WP-06, CI на Linux.

## Альтернативи
| Варіант | Чому ні |
|---|---|
| `subprocess` + `resource.setrlimit` | Немає на Windows; немає мережевої ізоляції; не безпечна межа |
| nsjail / bubblewrap / firejail | Лише Linux |
| RestrictedPython, аудит-хуки | Не є межею безпеки, обходиться |
| WebAssembly (Pyodide, wasmtime-py) | Нативні бібліотеки парсингу (lxml) недоступні або повільні; складні ліміти пам'яті |
| Firecracker / Kata | Лише Linux із KVM; надмірно для v1, можна додати як backend пізніше |
| Окремий довгоживучий контейнер-воркер на всі виклики | Стан і дані одного виклику можуть протекти в інший |
