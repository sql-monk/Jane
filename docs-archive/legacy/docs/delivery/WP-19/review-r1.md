# WP-19: незалежне рев'ю, раунд 1

**ВЕРДИКТ: changes requested.** Агент `wp19_review`, не автор WP.
Frozen HEAD `f79c8438a840ce1214a071cc43d66a1c6a37c5d5`, code `14d0337`, база `2c70543`.

## Блокуючі зауваження

1. `stores/sqlite.py:153`, `stores/postgres.py:217`: expiry lease видаляє fingerprint до TTL ключа.
   Реальні SQLite і PG: BODY_A, expired lease, живий TTL86400 -> BODY_B executes200 замість422.
   R04 / ADR-0008 §5. Потрібні збереження fingerprint до TTL і same-body takeover, regression обох backend.
2. `sqlite.py:166,184,203`, `postgres.py:234,250,274`: новий claim перезаписує `_claims[key]`;
   late complete/release старого request використовує NEW token. Два concurrent run_idempotent tasks
   на ОДНОМУ store: old handler paused -> lease expired -> new handler claims -> old completes -> new completes.
   Обидва backend: `REPLAY={'from':'stale-request'}, replayed=True`; очікувався current-request.
   R17 fencing / ТЗ §11. Потрібен token конкретного виконання і regression complete та release.

Repro scripts/output збережено у `.jane/wp19-review-r1/` координатора:
`wp19-review-r1-r04.py/.txt`, `wp19-review-r1-same-process.py/.txt`.

## Незалежні перевірки

У normal runs 80 passed, exit0: kit38 (SQLite/content/schemas/rules/secrets/media); storage15
(connection swap/reprocess); PG kit8, runtime6, assistant3, registry2, llm2, orchestrator3,
storage1; web hard-kill1; Telegram queued cancellation1.
Сирі точні команди/виводи у `wp19-review-r1.py`, `wp19-review-r1-results.json`, `wp19-review-r1-*.txt`
архіву координатора. Normal tests passed, але два додаткові repro виявили непокриті invariants вище.

Мутанти виконано лише в пам'яті ізольованих процесів, tracked source незмінний:

- PG: повторний lease check перед UPDATE вилучено -> **1 failed** (`test_state.py:283`, expected failed/got succeeded).
- Storage: close-immediately + forget-every-PUT -> **2 failed**, незмінний adapter і in-flight writes;
  помилка `adapter is not open`. Незмінені тести проходять.

Ownership actual base / integration:93 changed,0 outside. Main:94/1, лише coordinator wp-paths
з базового2c70543, а не зміна WP19. Hooks/settings незмінені.
Types/lint/Redocly exit0; oasdiff0breaking0warnings; gen-api10current.
Web fixture зберігає assertions/deadline/production defaults; у незалежному real hard-kill був host slot,
після recovery0. Базові blob SHA перевірені.

Cleanup у finally: `jane-review-wp19-r1`, `jane-review-wp19-r1-fence`; containers/volumes за labels відсутні.
Frozen HEAD і чистий tracked checkout збережені.
Full CI/e2e, Linux і зовнішні LLM/IdP/AWS/Telegram/MongoDB/SQLServer/S3 цим проходом не перевірені.
Files-only R18 та погоджений coordinator e2e root after merge не є додатковими findings.
