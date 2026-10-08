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

/** Page triage (tests/e2e/packages/e2e.llm-page-triage) of the unknown test-site pages /pages/faq, /pages/careers. */
export const TRIAGE_UNKNOWN_PAGES = [
  {
    when_data_contains: "<h1>FAQ</h1>",
    output: {
      page_triages: [{ page_type: "faq", summary: "Questions and answers about delivery and returns." }],
    },
  },
  {
    when_data_contains: "<h1>Careers</h1>",
    output: { page_triages: [{ page_type: "job", summary: "Job posting for a warehouse operator." }] },
  },
];
