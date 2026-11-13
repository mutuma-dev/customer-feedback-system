import "@testing-library/jest-dom/vitest"; // adds matchers like toBeInTheDocument()
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Remove rendered components after every test so tests cannot affect each other.
afterEach(cleanup);
