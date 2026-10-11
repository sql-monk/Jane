# Контракти: швидкий старт

Перевіряє контракти лінтером, піднімає мок `handler.v1` з прикладів контракту, викликає його, генерує Python-клієнт і перевіряє зворотну сумісність. Docker, Node.js і сервіси Jane не потрібні. Кроки виконано 2026-10-11 на Windows 11 (Git Bash і PowerShell), ревізія `48389a3`; на Linux не перевірялися.

## Передумови

- `uv` 0.12 або новіший і `just` (без встановленого just — `uvx --from rust-just just <рецепт>`).
- `git` — для перевірки сумісності з гілкою `main`.
- Робочий каталог — корінь репозиторію; вільний порт `18810` на `127.0.0.1`.

## Кроки

1. Запустіть лінтер контрактів:

   ```powershell
   just contracts-check
   ```

   Очікуваний результат (уривок):

   ```text
   [ok] JSON Schema meta-validation and $refs
   [ok] OpenAPI 3.1 validation
   [ok] Jane API conventions and inline examples
   [ok] Standalone schema examples
   [ok] Python interfaces compile
   [ok] Mock server can serve every operation
   [ok] Autonomous APIs do not reference orchestrator/assistant contracts
   [skip] Redocly lint

   Checked: autonomy_checked_apis=5, invalid_examples=13, mock_routes=118, openapi_documents=8, openapi_examples=544, operations=118, python_files=3, schema_examples=46, schemas=16
   All contract checks passed.
   ```

   Redocly пропущено: рецепт запускає його лише з `just contracts-check --redocly` (потрібен Node.js).

2. Перегляньте операції API, які обслуговуватиме мок:

   ```powershell
   uv run contracts/tools/mock.py handler --list
   ```

   ```text
   GET     /v1/connections                                              listConnections [200,401]
   ...
   GET     /v1/health                                                   getHealth [200,503]
   GET     /v1/info                                                     getServiceInfo [200,401]
   POST    /v1/invocations                                              invokeHandler [200,202,400,401,404,409,413,422,429,502,503]
   GET     /v1/invocations/{invocation_id}                              getInvocation [200,401,404]
   GET     /v1/jobs/{job_id}                                            getJob [200,401,404]
   POST    /v1/jobs/{job_id}/cancel                                     cancelJob [200,202,401,404]
   POST    /v1/test-runs                                                startTestRun [202,400,401,404,422]
   ```

3. Запустіть мок у першому терміналі:

   ```powershell
   just contracts-mock handler --port 18810
   ```

   ```text
   jane mock 'handler' on http://127.0.0.1:18810 (12 operations)
   ```

4. У другому терміналі викличте мок: health, запит без обов'язкового `Idempotency-Key` і запит, що просить відповідь `202`.

   Bash:

   ```bash
   curl -s http://127.0.0.1:18810/v1/health
   curl -s -X POST http://127.0.0.1:18810/v1/invocations -H 'Content-Type: application/json' -d '{}'
   curl -s -i -X POST http://127.0.0.1:18810/v1/invocations -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: demo-1' -H 'Prefer: code=202' -d '{}'
   ```

   PowerShell:

   ```powershell
   (Invoke-WebRequest http://127.0.0.1:18810/v1/health).Content
   $r = Invoke-WebRequest -Method Post http://127.0.0.1:18810/v1/invocations -ContentType application/json -Body '{}' -Headers @{"Idempotency-Key" = "demo-1"; "Prefer" = "code=202"}
   $r.StatusCode; $r.Headers.Location; $r.Content
   ```

   Очікуваний результат — перший приклад відповіді з контракту, Problem для пропущеного заголовка й `202` з `Location` (вивід Bash; заголовки `Server`, `Date`, `Access-Control-*` пропущено):

   ```text
   {"status": "ok", "checks": {"state_store": {"status": "ok"}}}
   {"type": "urn:jane:problem:validation_failed", "title": "Validation failed", "status": 422, "code": "validation_failed", "detail": "missing required header(s): Idempotency-Key", "retryable": false}
   HTTP/1.0 202 Accepted
   Content-Type: application/json
   Location: /v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F

   {"job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F", "kind": "collection", "status": "queued", "created_at": "2026-09-27T10:00:00Z", "links": {"self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F", "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"}}
   ```

   Мок `contracts/tools/mock.py` не перевіряє тіло запиту за схемою (тому `{}` приймається) — лише обов'язкові заголовки й наявність тіла. Валідацію тіла дає Prism або мок `jane_kit.contracts.build_mock_app` ([інтеграція](integration.md#моки)).

5. Зупиніть мок: `Ctrl+C` у першому терміналі.

6. Згенеруйте Python-клієнт `storage.v1` у тимчасовий каталог (тут — `.jane/` поза Git):

   ```powershell
   just contracts-gen storage .jane/gen/storage
   ```

   ```text
   $ uv run --all-packages jane-codegen client contracts/openapi/storage.v1.yaml --out .jane/gen/storage --no-models
   generated .jane\gen\storage
   ```

   Каталог містить `__init__.py` і `client.py` з класом `JaneStorageReadApiClient` — async-метод на кожну операцію (`list_entities`, `get_object`, `get_object_content`…).

7. Перевірте зворотну сумісність робочого дерева з гілкою `main`:

   ```powershell
   just contracts-compat
   ```

   ```text
   [ok] case 0: expect BREAKING 'became required'
   ...
   [ok] identical schema has no findings
   [ok] default oasdiff image is pinned by tag and digest: tufin/oasdiff:v1.33.0@sha256:6263a96dd2ef0726c54e21fea9b8e1607eac4841add0079324b424c1f52b819c
   $ uv run --script contracts/tools/compat.py --base main
   Base: main (24 contract files); working tree: 24 files; added: 0

   0 breaking, 0 warning(s).
   ```

## Прибирання

Команда видаляє лише згенерований у кроці 6 клієнт:

PowerShell:

```powershell
Remove-Item -Recurse -Force .jane/gen
```

Bash:

```bash
rm -rf .jane/gen
```

## Далі

- Конвенції API та підключення клієнтів — [інтеграція](integration.md).
- Як змінювати контракт — [експлуатація](operations.md#зміна-контракту).
