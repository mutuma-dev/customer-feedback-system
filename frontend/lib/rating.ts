/** Words shown under the stars. Index 0 is 1 star, index 4 is 5 stars. */
export const RATING_LABELS = ["Poor", "Fair", "Good", "Very good", "Excellent"] as const;

/** The word for a rating, or a prompt when nothing (or something invalid) is chosen. */
export function labelFor(rating: number | null): string {
  if (rating === null || rating < 1 || rating > 5) return "Select a rating";
  return RATING_LABELS[rating - 1];
}
