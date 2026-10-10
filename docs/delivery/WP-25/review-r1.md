# WP-25 — незалежне рев’ю R1

Субагент `review25`; зміни `8863e1`, інтеграція `b9474f5`. Вердикт **changes requested**.

- P2: `MaterialsPage.tsx:30` JSON.parse/stringify змінює числові значення матеріалу: `{"id":9007199254740993,"count":1e400}` стає `{"id":9007199254740992,"count":null}`. Потрібно зберегти первісний текст і додати регресію.
- Координаторський P2: migration `runs-data.spec.ts:64` не доповнив контрактний список підключень `raw-files`; selectOption чекає відсутній option. Виправлено координатором через schema-valid discovery fixture; попередні assertions збережено, потрібен адресний повтор сценарію.
- Відомий guardian R1 async blocker не дублювався: WP-25 перейде на status job після WP-24.

Перевірки рев’юера: ownership **9 changed / 0 outside**, protected файли незмінені; typecheck й scoped eslint exit 0; unit **7 passed**; browser WP25 **2 passed**; разом із legacy **7 passed, 1 failed (1.5m)**. Незалежно переглянуто вузький screenshot; 390 px придатний. Порти 5025, 5031–5037 звільнено.
