import { useTheme, type ThemePreference } from "../app/theme";
import { Icon } from "./Icon";

export function ThemeControl() {
  const theme = useTheme();
  return (
    <label className="theme-control">
      <Icon name={theme.theme === "dark" ? "moon" : "sun"} />
      <span className="sr-only">Тема оформлення</span>
      <select
        aria-label="Тема оформлення"
        value={theme.preference}
        onChange={(event) => theme.setTheme(event.target.value as ThemePreference)}
      >
        <option value="dark">Темна</option>
        <option value="light">Світла</option>
        <option value="system">Системна</option>
      </select>
    </label>
  );
}
