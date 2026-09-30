import { expect, expectNoSecretLeak, test } from "./fixtures";

// Runs in both mock and real mode. The route returns a valid problem+json response whose
// human-readable fields intentionally contain a fake credential.
test("problem+json error fields never reach the admin UI", async ({ admin }) => {
  const secret = ["pg-password", "LEAK-1"].join("-");
  await admin.route(
    (url) => url.pathname === "/api/orchestrator/v1/connections",
    (route) =>
      route.fulfill({
        status: 422,
        contentType: "application/problem+json",
        body: JSON.stringify({
          type: "urn:jane:problem:validation_failed",
          title: `Validation failed: ${secret}`,
          status: 422,
          code: "validation_failed",
          detail: `Connection rejected: ${secret}`,
          trace_id: `trace-${secret}`,
          errors: [{ pointer: `/params/${secret}`, code: "bad_request", message: secret }],
          details: { message: secret },
        }),
      }),
  );

  await admin.goto("/connections");
  const alert = admin.getByRole("alert");
  await expect(alert).toBeVisible();
  await expect(alert).toContainText("validation_failed");
  await expect(alert).toContainText("HTTP 422");
  await expectNoSecretLeak(admin, [secret]);
});
