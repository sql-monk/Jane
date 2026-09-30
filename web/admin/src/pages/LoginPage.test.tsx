import { afterEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import { LoginPage } from "./LoginPage";

afterEach(() => {
  sessionStorage.clear();
  localStorage.clear();
});

describe("LoginPage (api_key mode)", () => {
  it("keeps the key only in sessionStorage and never renders it", async () => {
    const secret = "dev-admin-key-DO-NOT-SHOW";
    const { container } = render(
      <QueryClientProvider client={new QueryClient()}>
        <AppProvider config={DEFAULT_CONFIG}>
          <MemoryRouter initialEntries={["/login"]}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={<p>home</p>} />
            </Routes>
          </MemoryRouter>
        </AppProvider>
      </QueryClientProvider>,
    );
    const input = screen.getByLabelText("Ключ API");
    expect(input).toHaveAttribute("type", "password");
    await userEvent.type(input, secret);
    await userEvent.click(screen.getByRole("button", { name: "Увійти" }));
    expect(await screen.findByText("home")).toBeInTheDocument();
    expect(sessionStorage.getItem("jane.admin.api_key")).toBe(secret);
    expect(JSON.stringify({ ...localStorage })).not.toContain(secret);
    expect(container.innerHTML).not.toContain(secret);
  });
});
