import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import { AppProvider } from "./app/context";
import { loadConfig } from "./config";
import "./styles.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 5_000 },
    mutations: { retry: 0 },
  },
});

const root = createRoot(document.getElementById("root") as HTMLElement);

loadConfig()
  .then((config) => {
    root.render(
      <StrictMode>
        <QueryClientProvider client={queryClient}>
          <AppProvider config={config}>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </AppProvider>
        </QueryClientProvider>
      </StrictMode>,
    );
  })
  .catch((error: unknown) => {
    root.render(<pre role="alert">Не вдалося завантажити config.json: {String(error)}</pre>);
  });
