// Jest setup file

// Mock React's cache function (used in server-only code)
jest.mock('react', () => ({
  ...jest.requireActual('react'),
  cache: (fn) => fn, // In tests, just return the function unwrapped
}));
