const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-node',
  testPathIgnorePatterns: [
    '/node_modules/',
    '/e2e/',
    '/.next/'
  ],
}

module.exports = createJestConfig(customJestConfig)
