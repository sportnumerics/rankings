// Mock for ../app/shared.tsx to avoid JSX parsing issues in tests

export function by<T>(fn: (item: T) => any) {
  return (a: T, b: T) => {
    const aVal = fn(a);
    const bVal = fn(b);
    if (aVal < bVal) return -1;
    if (aVal > bVal) return 1;
    return 0;
  };
}

// Mock ExternalLink component (not needed for server-side tests)
export const ExternalLink = () => null;
