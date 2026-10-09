// Scripted answers of the deterministic fake LLM provider (WP-10 `fake`, a substitute of the external model) for
// the real-mode admin scenarios. They give only the TEXT of the model's answer; everything around it (sampling
// stored RAW, guards, tests in the real handler-runtime, publication in the real registry) runs the real code.
// Format of a script: services/llm/src/jane_llm/providers/fake.py (`when_data_contains` / `when_data_matches`).

/**
 * Improvement of tests/e2e/packages/e2e.improvable-product-extractor (WP-13 fixture: in-stock offers only) by
 * the source assistant: map OutOfStock / PreOrder offers instead of reporting them as unrecognized, and suggest a
 * new expected data type `offer`. The fix is the one of tests/e2e/config/llm-seed.yaml (S-M2-07) plus
 * `suggested_entity_types`; `p1` is the only problem sample of the admin scenario (phone-gamma).
 * The improve step sends the package manifest first (services/assistant/src/jane_assistant/improvement.py).
 */
export const IMPROVE_IMPROVABLE_EXTRACTOR = {
  when_data_matches: '(?s)^\\{\\s*"access": .*"module": "e2e_improvable_products\\.main"',
  output: {
    change_summary:
      "Map schema.org OutOfStock and PreOrder offers to availability out_of_stock and pre_order instead of " +
      "reporting them as unrecognized; the entity schema gains the two values (additive).",
    schema_change: "additive",
    suggested_entity_types: ["offer"],
    expectations: [
      {
        name: "p1",
        expected_status: "success",
        entities: [{ entity_type: "product", fields: { sku: "phone-gamma", availability: "out_of_stock" } }],
      },
    ],
    files: {
      "schemas/product.schema.json": JSON.stringify(
        {
          $schema: "https://json-schema.org/draft/2020-12/schema",
          title: "product",
          type: "object",
          additionalProperties: false,
          required: ["sku"],
          properties: {
            sku: { type: "string", minLength: 1 },
            title: { type: "string", minLength: 1 },
            price: {
              type: "object",
              additionalProperties: false,
              required: ["amount", "currency"],
              properties: {
                amount: { type: "number", minimum: 0 },
                currency: { type: "string", pattern: "^[A-Z]{3}$" },
              },
            },
            availability: { type: "string", enum: ["in_stock", "out_of_stock", "pre_order"] },
          },
        },
        null,
        2,
      ),
      "src/e2e_improvable_products/main.py": [
        '"""E2E fixture extractor as improved by the source assistant (admin real-mode scenario)."""',
        "",
        "import json",
        "import re",
        "",
        "_LD_JSON = re.compile(r'<script type=\"application/ld\\+json\">(.*?)</script>', re.DOTALL)",
        '_AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "pre_order"}',
        "",
        "",
        "def _product(html):",
        "    for block in _LD_JSON.findall(html):",
        "        try:",
        "            doc = json.loads(block)",
        "        except ValueError:",
        "            continue",
        '        if isinstance(doc, dict) and doc.get("@type") == "Product":',
        "            return doc",
        "    return None",
        "",
        "",
        "def extract(material, params, ctx):",
        "    ld = _product(ctx.text())",
        "    if ld is None:",
        '        return {"status": "empty", "entities": []}',
        '    offers = ld.get("offers") or {}',
        '    fields = {"sku": ld.get("sku"), "title": ld.get("name")}',
        "    try:",
        '        fields["price"] = {"amount": float(offers["price"]), "currency": str(offers["priceCurrency"])}',
        "    except (KeyError, TypeError, ValueError):",
        '        fields["price"] = None',
        "    fields = {k: v for k, v in fields.items() if v is not None}",
        '    availability = str(offers.get("availability", "")).rsplit("/", 1)[-1]',
        "    if availability not in _AVAILABILITY:",
        "        return {",
        '            "status": "unrecognized",',
        '            "entities": [{"entity_type": "product", "fields": fields, "completeness": "partial"}],',
        '            "unrecognized": {',
        '                "partial": True,',
        '                "reason": "offer availability is not handled by this extractor",',
        '                "signature": "unknown-availability",',
        "            },",
        "        }",
        '    fields["availability"] = _AVAILABILITY[availability]',
        '    return {"status": "success", "entities": [{"entity_type": "product", "fields": fields, "completeness": "full"}]}',
        "",
      ].join("\n"),
    },
  },
};

/**
 * Page triage (tests/e2e/packages/e2e.llm-page-triage) of the unknown test-site pages: a valid answer for /pages/faq;
 * for /pages/careers an answer that violates the package output schema (`page_type` is not in its enum), so the
 * gateway rejects it and the run has a failed item (as Phone Zeta in S-M2-11).
 */
export const TRIAGE_UNKNOWN_PAGES = [
  {
    when_data_contains: "<h1>FAQ</h1>",
    output: {
      page_triages: [{ page_type: "faq", summary: "Questions and answers about delivery and returns." }],
    },
  },
  {
    when_data_contains: "<h1>Careers</h1>",
    output: { page_triages: [{ page_type: "vacancy", summary: "Job posting for a warehouse operator." }] },
  },
];

/** The testsite as the Compose services (and the static search provider of the assistant) see it. */
const SITE = "http://testsite:8080";

/**
 * Source onboarding of the testsite by the assistant (R26, the admin twin of S-M2-06): the answers of
 * tests/e2e/config/llm-seed.yaml (`e2e-assistant-scripts`, without the improvement step). The steps are told apart
 * by the first data part the assistant sends (services/assistant/src/jane_assistant/prompts.py, onboarding.py):
 * classify `url: <material>` (one material per request - `e2e:real:prepare` sets sample_batch_size=1), analyze
 * JSON `{"hints": …}`, propose JSON `{"discovery_methods": …}`, generate_extractor JSON `{"entity_type": "product"…}`.
 * Sampling through the real Web Collector, tests in the real handler-runtime and publication run the real code.
 */
export const ONBOARD_TESTSITE = [
  // ---- classify: the material type of one test-site page by its <meta name="jane:page-type">
  ...(
    [
      ["product", "product", 0.95],
      ["category", "category", 0.9],
      ["news", "article", 0.9],
      ["news-list", "news_list", 0.9],
    ] as const
  ).map(([pageType, materialType, confidence]) => ({
    when_data_matches: `(?s)^url: ${SITE}/[^\\n]*\\n\\n.*<meta name="jane:page-type" content="${pageType}">`,
    output: { items: [{ name: "m0", material_type: materialType, confidence }] },
  })),
  // home, about, events/jobs/FAQ, loops, archive...: a catch-all type the model is less sure about
  {
    when_data_matches: `^url: ${SITE}/`,
    output: { items: [{ name: "m0", material_type: "other", confidence: 0.6 }] },
  },
  // ---- analyze: the source kind, discovery methods and the entity of product pages
  {
    when_data_matches: '^\\{\\s*"hints": ',
    output: {
      source_kind: "web",
      discovery_methods: ["sitemap", "feed", "listing", "recursive"],
      entities: [
        {
          entity_type: "product",
          material_type: "product",
          fields: [
            { name: "sku", type: "string", coverage: 1, examples: ["phone-alpha"] },
            { name: "title", type: "string", coverage: 1, examples: ["Phone Alpha"] },
            { name: "price", type: "money", coverage: 1, examples: ["299.00 UAH"] },
            { name: "availability", type: "string", coverage: 1, examples: ["in_stock", "out_of_stock"] },
            { name: "url", type: "url", coverage: 1 },
          ],
        },
      ],
    },
  },
  // ---- propose: several collection plans with their risks (sections and limits are left to Jane)
  {
    when_data_matches: '^\\{\\s*"discovery_methods": ',
    output: {
      proposals: [
        {
          title: "Sitemap index with the product extractor",
          summary: "Every page listed in /sitemap.xml; product cards go to the product extractor.",
          recommended: true,
          strategies: [{ type: "sitemap", urls: [`${SITE}/sitemap.xml`] }],
          entity_types: ["product"],
          risks: [
            "Products that are missing from the sitemap (for example API-only items) are not collected.",
          ],
        },
        {
          title: "Recursive crawl from the home page",
          summary: "Follows links from the home page inside the site.",
          recommended: false,
          strategies: [{ type: "recursive", seeds: [`${SITE}/`] }],
          exclude: ["testsite/calendar/**"],
          entity_types: ["product"],
          risks: [
            "More requests per run than the sitemap plan.",
            "The calendar pages link to each other endlessly; the crawl relies on exclusions and depth limits.",
          ],
        },
      ],
    },
  },
  // ---- generate_extractor: a new product extractor for the test site (standard library only)
  {
    when_data_matches: '^\\{\\s*"entity_type": "product"',
    output: {
      summary: "Product cards from the schema.org JSON-LD block; pages without it are empty.",
      key_fields: ["sku"],
      entity_schema: {
        type: "object",
        additionalProperties: false,
        required: ["sku", "title", "price"],
        properties: {
          sku: { type: "string", minLength: 1 },
          title: { type: "string", minLength: 1 },
          price: {
            type: "object",
            additionalProperties: false,
            required: ["amount", "currency"],
            properties: {
              amount: { type: "number", minimum: 0 },
              currency: { type: "string", pattern: "^[A-Z]{3}$" },
            },
          },
          availability: { type: "string", enum: ["in_stock", "out_of_stock", "pre_order"] },
          url: { type: "string" },
        },
      },
      expectations: [
        ...["sample_0", "sample_1", "sample_2"].map((name) => ({
          name,
          expected_status: "success",
          entities: [{ entity_type: "product", fields: { price: { currency: "UAH" } } }],
        })),
        { name: "neg_0", expected_status: "empty" },
      ],
      module_code: String.raw`import json
import re

LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "pre_order"}


def _product(html):
    for block in LD_JSON.findall(html):
        try:
            doc = json.loads(block)
        except ValueError:
            continue
        if isinstance(doc, dict) and doc.get("@type") == "Product":
            return doc
    return None


def extract(material, params, ctx):
    doc = _product(ctx.text())
    if doc is None:
        return {"status": "empty", "entities": []}
    offers = doc.get("offers") or {}
    fields = {}
    if doc.get("sku"):
        fields["sku"] = str(doc["sku"])
    if doc.get("name"):
        fields["title"] = str(doc["name"])
    try:
        fields["price"] = {"amount": float(offers["price"]), "currency": str(offers["priceCurrency"])}
    except (KeyError, TypeError, ValueError):
        pass
    availability = AVAILABILITY.get(str(offers.get("availability", "")).rsplit("/", 1)[-1])
    if availability:
        fields["availability"] = availability
    url = (material.get("locator") or {}).get("url")
    if url:
        fields["url"] = str(url)
    scope = (material.get("source") or {}).get("source_id", "local")
    missing = [name for name in ("sku", "title", "price") if name not in fields]
    if missing:
        entities = []
        if "sku" in fields:
            key = {"scope": scope, "natural": {"sku": fields["sku"]}}
            entities.append(
                {"entity_type": "product", "key": key, "fields": fields, "completeness": "partial"}
            )
        return {
            "status": "unrecognized",
            "entities": entities,
            "unrecognized": {
                "partial": bool(entities),
                "reason": "product card without " + ", ".join(missing),
                "signature": "missing-field:" + ",".join(missing),
            },
        }
    key = {"scope": scope, "natural": {"sku": fields["sku"]}}
    return {
        "status": "success",
        "entities": [{"entity_type": "product", "key": key, "fields": fields, "completeness": "full"}],
    }
`,
    },
  },
];
