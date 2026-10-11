# lib/navigation

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.navigation.NAV_GROUPS](#adminlibnavigationnav_groups)
- [admin.lib.navigation.navigationFor](#adminlibnavigationnavigationfor)

## admin.lib.navigation.NAV_GROUPS

**Константа.** Код: [web/admin/src/lib/navigation.ts:3](../../../../../../web/admin/src/lib/navigation.ts#L3).

```typescript
NAV_GROUPS: { label: string; items: Array<{ to: string; label: string; icon: IconName; description: string; }>; }[] = [
  {
    label: "Робочий простір",
    items: [
      {
        to: "/",
        label: "Огляд",
        icon: "overview",
        description: "Стан платформи, останні запуски та те, що потребує вашої уваги.",
      },
      {
        to: "/sources",
        label: "Джерела",
        icon: "sources",
        description: "Сайти й канали, правила збору та підключення нових джерел.",
      },
      {
        to: "/tasks",
        label: "Завдання",
        icon: "tasks",
        description:
          "Керуйте розкладами та ланцюжками. Запускайте збір або перевіряйте його в тестовому режимі.",
      },
      {
        to: "/runs",
        label: "Запуски",
        icon: "runs",
        description: "Історія виконання, прогрес етапів, повтори та скасування.",
      },
    ],
  },
  {
    label: "Дані та якість",
    items: [
      {
        to: "/materials",
        label: "Матеріали",
        icon: "materials",
        description: "Зібрані оригінали та шлях кожного матеріалу через етапи обробки.",
      },
      {
        to: "/storages",
        label: "Сховища",
        icon: "packages",
        description: "Стан сховищ, кількість збережених об’єктів і результати перевірок.",
      },
      {
        to: "/results",
        label: "Результати",
        icon: "results",
        description: "Витягнуті сутності та збережені результати обробки.",
      },
      {
        to: "/problems",
        label: "Проблеми",
        icon: "problems",
        description:
          "Знайдіть причину збою, вдоскональте обробник або повторно обробіть збережені матеріали.",
      },
      {
        to: "/packages",
        label: "Пакети",
        icon: "packages",
        description: "Код обробників, правила колекторів, тести, версії та незалежні форки.",
      },
      {
        to: "/assistant",
        label: "Асистент",
        icon: "assistant",
        description: "Підключіть джерело з допомогою LLM або вдоскональте пакет на проблемних прикладах.",
      },
    ],
  },
  {
    label: "Налаштування",
    items: [
      {
        to: "/connections",
        label: "Підключення",
        icon: "connections",
        description: "Підключення до сервісів і сховищ. Секрети передаються лише за посиланнями.",
      },
      {
        to: "/llm",
        label: "LLM",
        icon: "llm",
        description: "Провайдери, моделі, бюджети та фактичне споживання.",
      },
      {
        to: "/limits",
        label: "Ліміти",
        icon: "limits",
        description: "Обмеження платформи та ефективні ліміти для джерел і завдань.",
      },
      {
        to: "/audit",
        label: "Аудит",
        icon: "audit",
        description: "Хто, коли й навіщо змінив конфігурацію платформи.",
      },
    ],
  },
]
```

Доступ: читання — так; запис — так.

## admin.lib.navigation.navigationFor

**Функція.** Код: [web/admin/src/lib/navigation.ts:110](../../../../../../web/admin/src/lib/navigation.ts#L110).

```typescript
function navigationFor(pathname: string): { to: string; label: string; icon: IconName; description: string; } | undefined
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pathname` | `string` | `—` | required |

Результат: `{ to: string; label: string; icon: IconName; description: string; } | undefined`.
