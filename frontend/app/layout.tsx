// The "shell" that wraps EVERY page: the <html> and <body> tags, the title and the global CSS.
import type { Metadata, Viewport } from "next";
import "./globals.css"; // the stylesheet for the whole app

// Shown in the browser tab and in search results.
export const metadata: Metadata = {
  title: "Company X · Feedback",
  description: "Tell us how we did. It takes under a minute.",
};

// Makes the page fit phone screens instead of being shown zoomed-out.
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      {/* `children` is the page being shown: the survey or the dashboard. */}
      <body>{children}</body>
    </html>
  );
}
