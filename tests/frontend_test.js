import { test, expect } from '@playwright/test';

test.describe('Frontend E2E Test with FastAPI Backend', () => {
  
  test('should fetch and display data from the backend successfully', async ({ page }) => {
    // 1. Navigate to your local JavaScript application server
    await page.goto('http://localhost:5173');

    // 2. Interact with the UI (e.g., clicking a button that triggers a fetch request)
    const fetchButton = page.locator('#load-data-btn');
    await fetchButton.click();

    // 3. Assert that the DOM updated with information provided by FastAPI
    const dataContainer = page.locator('#data-list');
    await expect(dataContainer).toBeVisible();
    await expect(dataContainer).toContainText('success');
  });

});
