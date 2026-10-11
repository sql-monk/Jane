export interface ResultsContext {
  connectionId?: string;
  entityType?: string;
  scope?: string;
  key?: string;
}

/** Only storage API filters are accepted. A source/task/run identifier never implies key.scope. */
export function resultsHref(context: ResultsContext = {}): string {
  const params = new URLSearchParams();
  for (const [name, value] of Object.entries({
    connection_id: context.connectionId,
    entity_type: context.entityType,
    scope: context.scope,
    key: context.key,
  })) {
    if (value) params.set(name, value);
  }
  return "/results" + (params.size ? "?" + params.toString() : "");
}

export function entityTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    offer: "Пропозиції магазинів",
    product: "Товари",
    article: "Статті",
    post: "Публікації",
    car_ad: "Оголошення про авто",
    classified_ad: "Оголошення",
  };
  return labels[type] ?? type;
}
