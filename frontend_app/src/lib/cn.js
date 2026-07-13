/** Tiny className joiner — keeps JSX readable without extra dependencies. */
export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}
