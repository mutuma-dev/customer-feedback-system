/** Labels for the 1-5 star scale. Index 0 is 1 star. */
export const RATING_LABELS = ["Poor", "Fair", "Good", "Very good", "Excellent"] as const;

/** Text shown under the stars; a prompt when nothing is chosen yet. */
export function labelFor(rating: number | null): string {
  if (rating === null || rating < 1 || rating > 5) return "Select a rating";
  return RATING_LABELS[rating - 1];
}
