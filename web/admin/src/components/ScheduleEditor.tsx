import type { Schedule } from "../api/types";
import { Field } from "./ui";

/** Editor of TaskConfig.schedule (manual | once | cron | interval), fields from task-config.schema.json. */
export function ScheduleEditor({
  value,
  onChange,
}: {
  value: Schedule | undefined;
  onChange: (s: Schedule | undefined) => void;
}) {
  const schedule: Schedule = value ?? { type: "manual" };
  const set = (patch: Partial<Schedule>) => onChange({ ...schedule, ...patch });
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
        <Field label="Час запуску (RFC 3339)">
          <input
            value={schedule.at ?? ""}
            placeholder="2026-10-01T02:00:00Z"
            onChange={(e) => set({ at: e.target.value })}
          />
        </Field>
      ) : null}
      {schedule.type === "cron" ? (
        <Field label="Cron (5 полів)">
          <input
            value={schedule.cron ?? ""}
            placeholder="0 2 * * 0"
            onChange={(e) => set({ cron: e.target.value })}
          />
        </Field>
      ) : null}
      {schedule.type === "interval" ? (
        <Field label="Інтервал, секунд">
          <input
            type="number"
            min={1}
            value={schedule.interval_seconds ?? ""}
            onChange={(e) => set({ interval_seconds: Number.parseInt(e.target.value, 10) || 1 })}
          />
        </Field>
      ) : null}
      {schedule.type !== "manual" ? (
        <>
          <Field label="Часовий пояс">
            <input value={schedule.timezone ?? "UTC"} onChange={(e) => set({ timezone: e.target.value })} />
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
