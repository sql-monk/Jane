const paths = {
  overview: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  sources: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M3 12h18 M12 3c-5 5-5 13 0 18 M12 3c5 5 5 13 0 18",
  tasks: "M8 5h13 M8 12h13 M8 19h13 M3 5h.01 M3 12h.01 M3 19h.01",
  runs: "M8 5v14l12-7z",
  materials: "M5 3h10l4 4v14H5z M14 3v5h5 M8 12h8 M8 16h8",
  results: "M4 19V9 M10 19V5 M16 19v-7 M22 19H2",
  problems: "M12 3 2 21h20z M12 9v5 M12 17h.01",
  packages: "m12 2 10 5v10l-10 5-10-5V7z M2 7l10 5 10-5 M12 12v10 M7 4.5l10 5",
  assistant: "m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z",
  connections:
    "M9 15l6-6 M7 17l-1 1a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0 M17 7l1-1a4 4 0 0 1 6 6l-4 4a4 4 0 0 1-6 0",
  llm: "M7 4h10v16H7z M10 8h4 M10 12h4 M10 16h4 M3 8h4 M17 8h4 M3 16h4 M17 16h4",
  limits: "M4 7h16 M4 17h16 M8 4v6 M16 14v6",
  audit: "M12 3a9 9 0 1 0 9 9 M12 7v5l4 2 M16 3h5v5",
  search: "M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14 M15 15l6 6",
  arrow: "M5 12h14 M14 7l5 5-5 5",
  refresh: "M20 7v5h-5 M4 17v-5h5 M6 6a8 8 0 0 1 13 2 M18 18A8 8 0 0 1 5 16",
  moon: "M20 14A9 9 0 0 1 10 4a9 9 0 1 0 10 10",
  sun: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1 1 M18 18l1 1 M5 19l1-1 M18 6l1-1",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  close: "M6 6l12 12 M18 6 6 18",
  check: "M5 12l4 4L19 6",
  plus: "M12 5v14 M5 12h14",
} as const;

export type IconName = keyof typeof paths;

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
