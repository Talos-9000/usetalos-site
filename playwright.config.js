const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { outputFolder: 'qa-artifacts/playwright-report', open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:4173',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium-mobile',
      use: { ...devices['iPhone 14'], browserName: 'chromium' },
    },
    {
      name: 'webkit-mobile',
      use: { ...devices['iPhone 14'], browserName: 'webkit' },
    },
  ],
});
