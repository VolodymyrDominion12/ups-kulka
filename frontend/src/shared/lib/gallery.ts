/** Pure helpers for the product photo gallery and admin photo ordering. */

/** Move forward/back through a list of length `length` cyclically. */
export function cycleIndex(current: number, length: number, delta: 1 | -1): number {
  if (length <= 1) return 0;
  return (current + delta + length) % length;
}

/** Move the item at `from` to `to`, keeping the relative order of the rest. */
export function reorderMediaIds(ids: readonly string[], from: number, to: number): string[] {
  if (from === to) return [...ids];
  if (from < 0 || from >= ids.length || to < 0 || to >= ids.length) return [...ids];
  const next = [...ids];
  const [moved] = next.splice(from, 1);
  next.splice(to, 0, moved);
  return next;
}

/** Make the photo at `index` the cover (position 0). */
export function moveMediaToFront(ids: readonly string[], index: number): string[] {
  return reorderMediaIds(ids, index, 0);
}

/** Remove the photo at `index`. */
export function removeMediaId(ids: readonly string[], index: number): string[] {
  return ids.filter((_, i) => i !== index);
}

/** Append newly uploaded media ids (dedup, cap at `max`, default 10). */
export function appendMediaIds(
  current: readonly string[],
  added: readonly string[],
  max = 10,
): string[] {
  const merged = [...current, ...added.filter((id) => !current.includes(id))];
  return merged.slice(0, max);
}

/** Largest available pre-generated variant for full-screen viewing. */
export function largestImageSrc(variants: Record<string, string>): string | null {
  for (const key of ["1280w", "original", "960w", "640w", "320w"]) {
    if (variants[key]) return variants[key];
  }
  return null;
}
