/**
 * Small functions that turn raw backend values into text people understand.
 * They are "pure" (same input = same output, no side effects), so they are easy to test.
 */
import type { Category } from "./api";

/**
 * "5 min ago" style text for an ISO date.
 * `now` can be passed in by tests so the result does not depend on the real clock.
 */
export function timeAgo(iso: string, now: Date = new Date()): string {
  // Difference in whole seconds (never negative, in case clocks differ slightly).
  const seconds = Math.max(0, Math.round((now.getTime() - new Date(iso).getTime()) / 1000));
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} d ago`;
  return iso.slice(0, 10); // older than a month: show the date, e.g. 2026-09-30
}

/** Where a response came from: the website form or an SMS reply. */
export function sourceLabel(source: string): string {
  return source === "sms" ? "SMS reply" : "Web form";
}

/** buyer / painter in plain words. */
export function kindLabel(kind: string): string {
  return kind === "painter" ? "Painter" : "Paint buyer";
}

/**
 * Friendly names for the three verdicts (the brief calls them detractor / passive / promoter).
 * Unhappy = mean below 3, Neutral = exactly 3, Happy = above 3.
 */
export function categoryLabel(category: Category): string {
  if (category === "detractor") return "Unhappy";
  if (category === "passive") return "Neutral";
  return "Happy";
}
