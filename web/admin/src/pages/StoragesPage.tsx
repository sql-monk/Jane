import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import { TERMINAL_JOB_STATUSES, useJob } from "../api/hooks";
import { ApiError } from "../api/problem";
import type { StorageConnection } from "../api/types";
import { storageName, useStorageConnections } from "../components/StorageConnections";
import { ErrorBox, KeyValue, Loading, LoadMore, Notice, Page, Section } from "../components/ui";
import { entityTypeLabel, resultsHref } from "../lib/results-context";
import { formatBytes, formatDate } from "../lib/format";
import "../materials-storage.css";

export function StoragesPage() {
  const list = useStorageConnections();
  return (
    <Page
      title="Сховища"
      actions={
        <Link className="btn" to="/materials">
          Усі матеріали
        </Link>
      }
    >
      <p className="muted">
        Стан за останньою перевіркою підключення. Натисніть «Перевірити зараз», щоб оновити доступність і
        статистику.
      </p>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      {!list.isLoading && !list.error && !list.items.length ? (
        <Notice>
          Немає налаштованих сховищ. <Link to="/connections">Налаштувати підключення</Link>
        </Notice>
      ) : null}
      <div className="storage-cards">
        {list.items.map((c) => (
          <StorageCard key={c.connection_id} connection={c} />
        ))}
      </div>
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

function StorageCard({ connection }: { connection: StorageConnection }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const id = connection.connection_id;
  const queryKey = ["storage-status", id];
  const [jobId, setJobId] = useState<string | null>(null);
  const job = useJob("storage", api.storage as never, jobId);
  const terminal = Boolean(job.data && TERMINAL_JOB_STATUSES.has(job.data.status));
  const busy = Boolean(jobId && !terminal);
  useEffect(() => {
    if (job.data && TERMINAL_JOB_STATUSES.has(job.data.status)) {
      void queryClient.invalidateQueries({ queryKey: ["storage-status", id] });
    }
  }, [job.data, id, queryClient]);
  const status = useQuery({
    queryKey,
    queryFn: () =>
      unwrap(api.storage.GET("/v1/storage-status", { params: { query: { connection_id: id } } })),
  });
  const check = useMutation({
    mutationFn: () =>
      unwrap(
        api.storage.POST("/v1/storage-status/checks", {
          body: { connection_id: id },
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
        }),
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(["job", "storage", data.job_id], data);
      setJobId(data.job_id);
    },
  });
  const data = status.data;
  return (
    <Section title={storageName(connection)}>
      <div className="button-row">
        <Link className="btn" to={`/materials?connection_id=${encodeURIComponent(id)}`}>
          Матеріали
        </Link>
        <Link className="btn" to={resultsHref({ connectionId: id })}>
          Результати
        </Link>
        <button
          type="button"
          className="btn"
          disabled={check.isPending || busy}
          onClick={() => check.mutate()}
        >
          {check.isPending || busy ? "Перевіряємо…" : "Перевірити зараз"}
        </button>
        <button
          type="button"
          className="btn"
          disabled={status.isFetching}
          onClick={() => void status.refetch()}
        >
          Оновити стан
        </button>
      </div>
      <ErrorBox error={status.error ?? check.error ?? job.error} />
      {jobId ? (
        <div role="status" aria-label="Перевірка сховища">
          <p>{jobStatusLabel(job.data?.status ?? "queued")}</p>
          {job.data?.progress ? (
            <p>
              Прогрес: {job.data.progress.completed ?? 0}
              {job.data.progress.total != null ? ` / ${job.data.progress.total}` : ""}
            </p>
          ) : null}
          {job.data?.error ? (
            <ErrorBox error={new ApiError(job.data.error.status, job.data.error)} title="Помилка перевірки" />
          ) : null}
          {job.error ? (
            <button type="button" className="btn" onClick={() => void job.refetch()}>
              Оновити перевірку
            </button>
          ) : null}
        </div>
      ) : null}
      {status.isLoading ? <Loading /> : null}
      <KeyValue
        rows={[
          ["Тип", connection.kind],
          [
            "Доступність",
            data?.availability === "available"
              ? "Доступне"
              : data?.availability === "unavailable"
                ? "Недоступне"
                : "Не перевірено",
          ],
          ["Остання перевірка", data?.checked_at ? formatDate(data.checked_at) : "Не перевірено"],
          ["Діагностика", data?.message ?? "—"],
          [
            "RAW і документи результатів",
            data?.statistics.object_count == null ? "Невідомо" : String(data.statistics.object_count),
          ],
          [
            "Обсяг вмісту RAW і документів",
            data?.statistics.total_size_bytes == null
              ? "Невідомо"
              : formatBytes(data.statistics.total_size_bytes),
          ],
          [
            "Статистика оновлена",
            data?.statistics.checked_at ? formatDate(data.statistics.checked_at) : "Не перевірено",
          ],
        ]}
      />
      <h3>Розібрані дані</h3>
      <KeyValue
        rows={[
          [
            "Кількість сутностей",
            data?.entity_statistics?.entity_count == null
              ? "Недоступно"
              : data.entity_statistics.entity_count.toLocaleString("uk-UA"),
          ],
          [
            "Обсяг актуальних станів",
            data?.entity_statistics?.total_size_bytes == null
              ? "Недоступно"
              : formatBytes(data.entity_statistics.total_size_bytes),
          ],
          [
            "Облік обсягу",
            data?.entity_statistics?.size_basis === "postgresql_relation_with_indexes"
              ? "Таблиця актуальних станів з індексами"
              : data?.entity_statistics?.size_basis === "snapshot_documents"
                ? "Файли актуальних станів"
                : data?.entity_statistics?.size_basis === "mongodb_collections_with_indexes"
                  ? "Колекції актуальних станів з індексами"
                  : "Недоступно",
          ],
        ]}
      />
      {data?.entity_statistics?.types?.length ? (
        <div className="button-row">
          {data.entity_statistics.types.map((row) => (
            <Link
              key={row.entity_type}
              className="btn"
              to={resultsHref({ connectionId: id, entityType: row.entity_type })}
            >
              {entityTypeLabel(row.entity_type)}: {row.entity_count.toLocaleString("uk-UA")}
            </Link>
          ))}
        </div>
      ) : null}
      {data?.entity_statistics?.unavailable_reason ? (
        <p className="muted">
          Статистика сутностей недоступна: {statisticsReasonLabel(data.entity_statistics.unavailable_reason)}
        </p>
      ) : null}
      <p className="muted">Обсяг актуальних станів не включає історію оновлень, RAW та записи доставки.</p>
      {data?.statistics.unavailable_reason ? (
        <p className="muted">
          Статистика недоступна: {statisticsReasonLabel(data.statistics.unavailable_reason)}
        </p>
      ) : null}
      <p className="muted">
        Статистика охоплює збережені об'єкти цього підключення; не показує загальний розмір диска чи бази.
      </p>
    </Section>
  );
}

export function statisticsReasonLabel(reason: string): string {
  const labels: Record<string, string> = {
    not_checked: "Перевірку ще не виконано.",
    adapter_statistics_not_supported: "Цей тип сховища не надає статистику.",
    statistics_check_failed: "Не вдалося отримати статистику. Спробуйте перевірити ще раз.",
    check_failed: "Не вдалося перевірити підключення.",
  };
  return labels[reason] ?? "Причину недоступності статистики не визначено.";
}

function jobStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    queued: "Перевірка очікує виконання.",
    running: "Перевіряємо доступність і статистику…",
    cancelling: "Перевірка скасовується…",
    cancelled: "Перевірку скасовано.",
    succeeded: "Перевірку завершено.",
    failed: "Перевірка завершилася з помилкою.",
  };
  return labels[status] ?? "Стан перевірки невідомий.";
}
