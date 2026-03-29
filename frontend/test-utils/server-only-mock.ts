// Mock for 'server-only' package in test environment
// The real package throws when imported from client components
// In tests, we just no-op it since we're testing server code
export default {};
