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
    product_food: "Товари: продукти й напої",
    product_beauty: "Товари: краса й догляд",
    product_household: "Товари: побутова хімія",
    product_book: "Товари: книжки",
    product_kids: "Товари: дитячі товари й іграшки",
    product_electronics: "Товари: електроніка",
    product_appliance: "Товари: побутова техніка",
    product_tools: "Товари: інструменти й ремонт",
    product_garden: "Товари: сад і город",
    product_home: "Товари: дім та інтер'єр",
    product_clothing: "Товари: одяг і взуття",
    product_auto: "Товари: автотовари",
    product_pet: "Товари: зоотовари",
    product_sport: "Товари: спорт і туризм",
    product_office: "Товари: канцтовари",
    product_health: "Товари: медичні товари",
    product_other: "Товари: інше",
    ad_car: "Оголошення: авто",
    ad_realty: "Оголошення: нерухомість",
    ad_goods: "Оголошення: речі",
    ad_other: "Оголошення: інше",
  };
  return labels[type] ?? type;
}
