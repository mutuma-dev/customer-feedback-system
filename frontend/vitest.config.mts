// Vitest = the test runner (like JUnit). This file tells it how to run our tests.
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  // Lets tests understand React/JSX files.
  plugins: [react()],
  resolve: {
    // "@/lib/api" means "<project folder>/lib/api" (same shortcut the app code uses).
    alias: { "@": fileURLToPath(new URL(".", import.meta.url)) },
  },
  test: {
    // "jsdom" is a pretend browser, so React components can be rendered inside tests.
    environment: "jsdom",
    // Runs before the tests (see vitest.setup.ts).
    setupFiles: ["./vitest.setup.ts"],
    // Every file ending in .test.ts or .test.tsx is a test. They sit next to the code they test.
    include: ["**/*.test.{ts,tsx}"],
    exclude: ["node_modules", ".next"],
  },
});
