import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import type { StorageConnection } from "../api/types";
import { storageName, useStorageConnections } from "../components/StorageConnections";
import { ErrorBox, KeyValue, Loading, LoadMore, Notice, Page, Section } from "../components/ui";
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
  const status = useQuery({
    queryKey,
    queryFn: () =>
      unwrap(api.storage.GET("/v1/storage-status", { params: { query: { connection_id: id } } })),
  });
  const check = useMutation({
    mutationFn: () =>
      unwrap(
        api.storage.POST("/v1/connections/{connection_id}/test", {
          params: { path: { connection_id: id } },
          headers: { "Idempotency-Key": newIdempotencyKey() },
        }),
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey });
    },
  });
  const data = status.data;
  return (
    <Section title={storageName(connection)}>
      <div className="button-row">
        <Link className="btn" to={`/materials?connection_id=${encodeURIComponent(id)}`}>
          Матеріали
        </Link>
        <Link className="btn" to={`/results?connection_id=${encodeURIComponent(id)}`}>
          Результати
        </Link>
        <button type="button" className="btn" disabled={check.isPending} onClick={() => check.mutate()}>
          {check.isPending ? "Перевіряємо…" : "Перевірити зараз"}
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
      <ErrorBox error={status.error ?? check.error} />
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
            "Кількість об'єктів",
            data?.statistics.object_count == null ? "Невідомо" : String(data.statistics.object_count),
          ],
          [
            "Обсяг",
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
      {data?.statistics.unavailable_reason ? (
        <p className="muted">Статистика недоступна: {data.statistics.unavailable_reason}</p>
      ) : null}
      <p className="muted">
        Статистика охоплює збережені об'єкти цього підключення; не показує загальний розмір диска чи бази.
      </p>
    </Section>
  );
}
