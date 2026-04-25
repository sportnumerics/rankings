// Vitest setup file
import { vi } from 'vitest';

// Mock environment variables for tests
process.env.DATA_BUCKET = 'test-bucket';
process.env.DATA_BUCKET_PREFIX = 'data';

// Mock React/JSX modules to avoid JSX compilation issues in tests
vi.mock('./app/shared.tsx', () => ({
  ExternalLink: vi.fn(),
  Card: vi.fn(),
  Table: vi.fn(),
  H2: vi.fn(),
  H3: vi.fn()
}));
