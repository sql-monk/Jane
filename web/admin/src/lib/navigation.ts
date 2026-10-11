import type { IconName } from "../components/Icon";

export const NAV_GROUPS: Array<{
  label: string;
  items: Array<{ to: string; label: string; icon: IconName; description: string }>;
}> = [
  {
    label: "Робочий простір",
    items: [
      {
        to: "/monitoring",
        label: "Моніторинг",
        icon: "overview",
        description: "Графіки, черги, швидкість обробки й доступність модулів.",
      },
      {
        to: "/modules",
        label: "Модулі",
        icon: "connections",
        description: "Стан, налаштування та діагностика кожного модуля.",
      },
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
];

export function navigationFor(pathname: string) {
  return NAV_GROUPS.flatMap((group) => group.items).find((item) =>
    item.to === "/" ? pathname === "/" : pathname === item.to || pathname.startsWith(`${item.to}/`),
  );
}
