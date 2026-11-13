// ESLint = a tool that reads the code and reports likely mistakes (run with `npm run lint`).
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals"; // Next.js + React recommended rules

export default defineConfig([
  ...nextVitals,
  // Folders that are generated, so they are not checked:
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);
