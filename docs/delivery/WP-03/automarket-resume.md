# WP-03. Перевірка відновлення тієї самої collection

**Гілка:** `wp/03-automarket-cached-resume` · **База:** `1406aa2` · **Стан:** review

У [тесті відновлення](../../../services/web-collector/strategies/discovery/tests/test_resume.py)
уточнено очікування для незавершеного sitemap seeds після kill: успішний `/sitemap.xml`
повторно використовується з navigation cache тієї самої collection ID, тому HTTP-запит один.
Незавершений child-запит лишився з точним очікуванням двох HTTP-запитів.

Це відновлення за [правилом 6](../../../contracts/docs/discovery-strategy.md#правила).
Ядро кешує успішні 2xx navigation-відповіді за collection ID, strategy ID і URL, зберігаючи
початковий `fetched_at`. Умови кешу перевірені читанням поточного коду; ядро не редагувалося.
Висновок не поширюється на нову logical collection і не підтверджує сценарій повторного збору R23.

Усі перевірки повноти об’єднаного набору URL, дедуплікації, невидачі acknowledged матеріалів,
припустимого повторення in-flight матеріалів і межі між seeds та crawl залишилися без змін.
Тест продовжує вбивати й перезапускати справжній окремий процес колектора на його збереженому стані.

## Перевірки

```powershell
uv run --frozen --all-packages --group dev pytest services/web-collector/strategies/discovery/tests/test_resume.py::test_strategies_resume_after_kill -q
uv run --frozen --all-packages --group dev ruff check services/web-collector/strategies/discovery/tests/test_resume.py
uv run --frozen --all-packages --group dev ruff format --check services/web-collector/strategies/discovery/tests/test_resume.py
git diff --check
```

```text
..                                                                       [100%]
2 passed in 23.64s
All checks passed!
1 file already formatted
```

`git diff --check` завершився з exit code 0 без виводу. Запущено лише параметри `during-seeds`
і `during-crawl`; широкі тести, нові scans, зміни API, source та поточних контейнерів не виконувалися.
Перший запуск з `--package jane-web-collector` не виконав тестів через відсутній executable `pytest`;
запуск з dev-залежностями всього workspace (`--all-packages`) виконав обидва наведені тести.
`--frozen` зберіг `uv.lock` без змін.

## Незалежне рев’ю

Очікується перевірка неавтором з повтором цього самого тесту з двома параметрами.
Координатор інтегрує коміт і запускає CI; push у `main` виконавцем не здійснюється.
