# LLM: інтеграція

[Python-клієнт](quickstart.md#перша-відповідь) викликає `createCompletion` з інструкцією, окремими data parts, output_schema та scope. Джерельний текст завжди передавайте через `data`, бо gateway відокремлює його від інструкцій.

## Scope і бюджет

`scope.purpose` є обов’язковим; `source_id`, `task_id`, `run_id` дозволяють віднести usage до сценарію. `limits` запиту має форму `LlmLimits`, а не загального об’єкта `{"llm": ...}`. Бюджет із `period=run` потребує стабільного `scope.run_id` на всі виклики одного запуску. Нульовий amount забороняє виклик; дешеві/fake виклики не дозволяють обійти ліміт кількості запитів.

Шлюз резервує кошти, викликає модель і перевіряє результат до обліку usage.

![Шлюз резервує кошти, викликає модель і перевіряє результат до обліку usage.](../../diagrams/llm/completion-flow.light.png)

[Темна тема](../../diagrams/llm/completion-flow.dark.png) · [Редаговане джерело](../../diagrams/llm/completion-flow.drawio)

## Асинхронний режим

`mode=async` повертає 202 із Job і Location. Poll `GET /v1/jobs/{job_id}` з backoff; успіх завершується `result`, помилка — `error`. `Idempotency-Key` зберігайте при повторі того самого completion. Для `mode=sync` timeout клієнта має покривати provider timeout, attempts і schema retries; типові 30 секунд загальних HTTP-запитів не достатні для генерації.

## Заміна провайдера

Налаштуйте connection, provider та models, потім змініть alias через `PUT /v1/model-aliases/{alias}`. Клієнт продовжує надсилати той самий `model` alias. Для Anthropic connection містить `kind=llm_provider`, посилання на API key; формат звіряйте з [ConnectionPolicy](../../../services/llm/src/jane_llm/connections.py) та [seed прикладом](../../../services/llm/config/seed.example.yaml). Значення секрету не входить у provider, пакет чи seed.

Невідомий alias/provider/model відхиляється, вимкнений provider не використовується. Зміна списку моделей або ціни впливає на резервування і має бути узгоджена з реальним провайдером. Зовнішній виклик тут не перевірено.

## LLM-пакет у ланцюжку

`POST /v1/invocations` реалізує handler.v1 для `kind=llm`: локальний пакет або Registry надає інструкції, схему і параметри. Orchestrator викликає шлюз як виконавця етапу; це опційна композиція. [Пакети шлюзу](../../../services/llm/packages/), [публічні API](reference/api/README.md).
