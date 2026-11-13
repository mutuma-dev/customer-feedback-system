// Runs once before the tests start.

// Adds extra checks such as expect(element).toBeInTheDocument().
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// After every test, remove what it rendered so tests cannot affect each other.
afterEach(cleanup);
