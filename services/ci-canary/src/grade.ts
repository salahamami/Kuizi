/** A Bac average of at least 10 out of 20 passes. */
export function passes(average: number): boolean {
  return average >= 10;
}

// NEGATIVE TEST: untested code pushes line coverage under the 80 % gate.
export function mention(average: number): string {
  if (average >= 16) return "Très bien";
  if (average >= 14) return "Bien";
  if (average >= 12) return "Assez bien";
  return "Passable";
}
