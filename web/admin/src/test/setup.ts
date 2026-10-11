import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(cleanup);

// jsdom does not implement the browser dialog API; components themselves remain real.
if (typeof HTMLDialogElement.prototype.showModal !== "function") {
  Object.defineProperty(HTMLDialogElement.prototype, "showModal", {
    configurable: true,
    writable: true,
    value: function (this: HTMLDialogElement) {
      this.open = true;
    },
  });
  Object.defineProperty(HTMLDialogElement.prototype, "close", {
    configurable: true,
    writable: true,
    value: function (this: HTMLDialogElement) {
      this.open = false;
    },
  });
}
