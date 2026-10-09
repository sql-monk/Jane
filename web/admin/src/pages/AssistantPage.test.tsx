import "@testing-library/jest-dom/vitest";
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import { AssistantPage } from "./AssistantPage";

// Keep neighbour calls pending: validation does not need any fabricated API responses.
function renderOnboarding() {
  const requests: Request[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn((request: Request) => {
      requests.push(request.clone());
      return new Promise<Response>(() => {});
    }),
  );
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={["/assistant"]}>
          <AssistantPage />
        </MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
  return requests;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("onboarding confidence (assistant.v1 exclusiveMinimum: 0, maximum: 1)", () => {
  it("blocks zero, negative and above-one confidence before sending a request", async () => {
    const requests = renderOnboarding();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Назва або посилання"), "testsite");
    const confidence = screen.getByLabelText(/^Поріг впевненості вибірки/);
    const start = screen.getByRole("button", { name: "Почати підключення" });
    for (const value of ["0", "-0.1", "1.1"]) {
      await user.clear(confidence);
      await user.type(confidence, value);
      expect(start).toBeDisabled();
      expect(screen.getByRole("alert")).toHaveTextContent("більшим за 0 і не більшим за 1");
      await user.click(start);
    }
    expect(requests.filter((r) => r.method === "POST")).toHaveLength(0);
  });

  it.each(["0.005", "1", ""])(
    "sends contract-valid confidence %s, with empty meaning the default",
    async (value) => {
      const requests = renderOnboarding();
      const user = userEvent.setup();
      await user.type(screen.getByLabelText("Назва або посилання"), "testsite");
      if (value) await user.type(screen.getByLabelText(/^Поріг впевненості вибірки/), value);
      const start = screen.getByRole("button", { name: "Почати підключення" });
      expect(start).toBeEnabled();
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
      await user.click(start);
      await waitFor(() => expect(requests.filter((r) => r.method === "POST")).toHaveLength(1));
      const body = await requests.find((r) => r.method === "POST")?.json();
      if (value) expect(body.limits).toEqual({ min_onboarding_confidence: Number(value) });
      else expect(body).not.toHaveProperty("limits");
    },
  );
});
