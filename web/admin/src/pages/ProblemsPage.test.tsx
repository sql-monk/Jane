import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { ProblemGroup } from "../api/types";
import { openapiExample } from "../test/contracts";
import { ProblemsPage } from "./ProblemsPage";

const input = openapiExample<{
  material_id: string;
  observation_id: string;
  source: { source_id: string };
  fetched_at: string;
}>("material-web");
const material = {
  material_id: input.material_id,
  observation_id: input.observation_id,
  source_id: input.source.source_id,
  fetched_at: input.fetched_at,
};
// ProblemGroup and StoredObject shapes follow the orchestrator/storage OpenAPI response examples.
const group: ProblemGroup = {
  group_id: "pg_01J9ZW0000000000000000001",
  source_id: material.source_id,
  package: { package_id: "shop-example.product-extractor", version: "1.2.0" },
  problem: "failed",
  signature: "missing-selector:.price",
  count: 1,
  status: "open",
  first_seen_at: material.fetched_at,
  last_seen_at: material.fetched_at,
};

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function openSample(observationId: string | undefined, pages: string[][]) {
  const submitted: unknown[] = [];
  const storageRequests: URL[] = [];
  const sample = { material_id: material.material_id, observation_id: observationId };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (request: Request) => {
      const url = new URL(request.url);
      if (url.pathname.endsWith("/v1/objects")) {
        storageRequests.push(url);
        const index = Number(url.searchParams.get("cursor") ?? "0");
        return Response.json({
          items: (pages[index] ?? []).map((objectId) => ({
            object: {
              object_id: objectId,
              adapter: "filesystem",
              connection_id: "raw-files",
              locator: { path: `raw/${objectId}.html` },
              media_type: "text/html",
              size_bytes: 160,
            },
            material,
            stored_at: material.fetched_at,
          })),
          next_cursor: index + 1 < pages.length ? String(index + 1) : null,
        });
      }
      if (url.pathname.endsWith("/v1/improvement-runs")) {
        submitted.push(await request.json());
        return Response.json({
          job_id: "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
          kind: "improvement",
          status: "queued",
          created_at: material.fetched_at,
        });
      }
      if (url.pathname.endsWith("/v1/problem-groups")) {
        return Response.json({ items: [{ ...group, samples: [sample] }], next_cursor: null });
      }
      if (request.method === "PATCH") return Response.json({ ...group, samples: [sample] });
      if (url.pathname.includes("/v1/jobs/")) {
        return Response.json({
          job_id: "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
          kind: "improvement",
          status: "queued",
          created_at: material.fetched_at,
        });
      }
      return Response.json({ items: [], next_cursor: null });
    }),
  );
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={DEFAULT_CONFIG}>
        <MemoryRouter>
          <ProblemsPage />
        </MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
  const table = await screen.findByRole("table", { name: "Групи проблем" });
  await userEvent.click(await within(table).findByRole("button", { name: "Відкрити" }));
  await userEvent.type(screen.getByLabelText("Сховище RAW прикладів"), "raw-files");
  await userEvent.click(screen.getByRole("button", { name: "Запустити вдосконалення" }));
  return { submitted, storageRequests };
}

describe("problem sample RAW fallback", () => {
  it("does not search or submit a RAW when observation_id is absent", async () => {
    const { submitted, storageRequests } = await openSample(undefined, [["obj_first"]]);
    expect(await screen.findByText(/RAW прикладу недоступний/)).toBeInTheDocument();
    expect(storageRequests).toHaveLength(0);
    expect(submitted).toHaveLength(0);
  });

  it.each([[["obj_first", "obj_second"]], [["obj_first"], ["obj_second"]]])(
    "does not submit an ambiguous RAW across all pages: %j",
    async (...pages) => {
      const { submitted } = await openSample(material.observation_id, pages);
      expect(await screen.findByText(/RAW прикладу недоступний/)).toBeInTheDocument();
      expect(submitted).toHaveLength(0);
    },
  );

  it("submits the unique RAW only after checking the final page", async () => {
    const { submitted, storageRequests } = await openSample(material.observation_id, [["obj_unique"], []]);
    expect(await screen.findByLabelText("Вдосконалення")).toBeInTheDocument();
    expect(storageRequests).toHaveLength(2);
    expect(storageRequests[0]?.searchParams.get("source_id")).toBe(material.source_id);
    expect(storageRequests[0]?.searchParams.get("material_id")).toBe(material.material_id);
    expect(submitted).toHaveLength(1);
    expect(submitted[0]).toMatchObject({
      problem_samples: [{ material_ref: { storage_connection_id: "raw-files", object_id: "obj_unique" } }],
    });
  });
});
