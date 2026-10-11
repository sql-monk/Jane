# Навігація Jane

Актуальний огляд, модулі та запуск — у [README](../../README.md).

## Адмінка: матеріали, сховища та ланцюжки (2026-10-11)

Погоджено користувачем; [план](admin-materials-chains-plan.md). Інтеграція в `codex/admin-materials-chains`, базова ревізія `1eb6dbd`.

| WP | Назва | Статус | Гілка |
|---|---|---|---|
| 24 | Стан і статистика сховищ | accepted (R2) | wp/24-storage-observability |
| 25 | Матеріали й браузер сховищ | accepted (R2) | wp/25-materials-storage-browser |
| 26 | Візуальний редактор ланцюжків | accepted (R2) | wp/26-visual-chain-editor |
| 27 | Інтеграція та приймання | accepted; full CI; deployed | codex/admin-materials-chains |

Інтеграція: 74 unit passed, typecheck/lint/build exit 0, реальний filesystem browser smoke 1 passed. Незалежні WP-reviewer прийняли всі три WP; контрактний guardian підтвердив сумісність. [Підсумковий звіт і межі перевірки](WP-27.md). Повний CI `38096339188`: 14/14 success, mandatory e2e 79 passed. Перевірений код `ada3586` розгорнуто в jane-demo; реальний browser smoke пройшов. [CI, виправлення, розгортання й межі](WP-27-ci-deployment.md).
