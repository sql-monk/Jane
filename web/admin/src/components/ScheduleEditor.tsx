import type { Schedule } from "../api/types";
import type { SchemaIssue } from "../lib/schema";
import { Field } from "./ui";

/** Editor of TaskConfig.schedule (manual | once | cron | interval), fields from task-config.schema.json. */
export function ScheduleEditor({
  value,
  onChange,
  issues = [],
}: {
  value: Schedule | undefined;
  onChange: (s: Schedule | undefined) => void;
  issues?: SchemaIssue[];
}) {
  const schedule: Schedule = value ?? { type: "manual" };
  const set = (patch: Partial<Schedule>) => onChange({ ...schedule, ...patch });
  const error = (field: string) => issues.find((issue) => issue.pointer === `/schedule/${field}`)?.message;
  return (
    <div className="grid-3" aria-label="Розклад">
      <Field label="Тип розкладу">
        <select
          value={schedule.type}
          onChange={(e) => {
            const type = e.target.value as Schedule["type"];
            const base: Schedule = { type };
            if (schedule.timezone) base.timezone = schedule.timezone;
            if (schedule.overlap) base.overlap = schedule.overlap;
            onChange(type === "manual" && !schedule.timezone && !schedule.overlap ? { type } : base);
          }}
        >
          <option value="manual">вручну</option>
          <option value="once">одноразово</option>
          <option value="cron">cron</option>
          <option value="interval">інтервал</option>
        </select>
      </Field>
      {schedule.type === "once" ? (
        <Field
          label="Час запуску"
          hint={`Часовий пояс пристрою: ${Intl.DateTimeFormat().resolvedOptions().timeZone}.`}
          error={error("at")}
        >
          <input
            type="datetime-local"
            value={localDateTime(schedule.at)}
            onChange={(e) => {
              const next = { ...schedule };
              if (e.target.value) next.at = new Date(e.target.value).toISOString();
              else delete next.at;
              onChange(next);
            }}
          />
        </Field>
      ) : null}
      {schedule.type === "cron" ? (
        <Field label="Cron (5 полів)" error={error("cron")}>
          <input
            value={schedule.cron ?? ""}
            placeholder="0 2 * * 0"
            onChange={(e) => set({ cron: e.target.value })}
          />
        </Field>
      ) : null}
      {schedule.type === "interval" ? (
        <Field label="Інтервал, секунд" error={error("interval_seconds")}>
          <input
            type="number"
            min={1}
            value={schedule.interval_seconds ?? ""}
            onChange={(e) => {
              const next = { ...schedule };
              if (e.target.value === "") delete next.interval_seconds;
              else next.interval_seconds = Number(e.target.value);
              onChange(next);
            }}
          />
        </Field>
      ) : null}
      {schedule.type !== "manual" ? (
        <>
          <Field label="Часовий пояс" error={error("timezone")}>
            <input
              list="schedule-timezones"
              value={schedule.timezone ?? "UTC"}
              onChange={(e) => set({ timezone: e.target.value })}
            />
            <datalist id="schedule-timezones">
              <option value="Europe/Kyiv" />
              <option value="UTC" />
            </datalist>
          </Field>
          <Field label="Якщо попередній запуск ще йде">
            <select
              value={schedule.overlap ?? "skip"}
              onChange={(e) => set({ overlap: e.target.value as NonNullable<Schedule["overlap"]> })}
            >
              <option value="skip">пропустити</option>
              <option value="queue">поставити в чергу</option>
              <option value="allow">дозволити паралельно</option>
            </select>
          </Field>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={schedule.enabled !== false}
              onChange={(e) => set({ enabled: e.target.checked })}
            />
            Розклад увімкнено
          </label>
        </>
      ) : null}
    </div>
  );
}

function localDateTime(value: string | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "";
  const pad = (number: number) => String(number).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
