const { chromium } = require('playwright');
const assert = require('assert');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  console.log('1. Navigating to app...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // Dismiss setup modal if displayed
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 2. Select Automation Tester profile
  const profileWidgetBtn = page.locator('.profile-btn');
  if (await profileWidgetBtn.count() > 0) {
    await profileWidgetBtn.click();
    await page.waitForTimeout(800);
    const testerOption = page.locator('.switch-user-btn').filter({ hasText: /Automation Tester/i });
    if (await testerOption.count() > 0) {
      await testerOption.click();
      await page.waitForTimeout(1500);
    }
  }

  console.log('2. Checking for 7 scenarios and live console...');
  const consoleElem = page.locator('[data-testid="qa-console"]');
  const consoleVisible = await consoleElem.isVisible().catch(() => false);
  assert.strictEqual(consoleVisible, true, 'QA live console should be visible');

  const autopilotToggle = page.locator('[data-testid="autopilot-toggle"]');
  const toggleVisible = await autopilotToggle.isVisible().catch(() => false);
  assert.strictEqual(toggleVisible, true, 'Autopilot walkthrough toggle should be visible');

  const runAllBtn = page.locator('[data-testid="run-all-scenarios"]');
  const runAllVisible = await runAllBtn.isVisible().catch(() => false);
  assert.strictEqual(runAllVisible, true, 'Run All Scenarios button should be visible');

  // Verify all 7 scenarios exist
  for (let i = 1; i <= 7; i++) {
    const scenarioBtn = page.locator(`[data-testid="run-scenario-${i}"]`);
    const exists = await scenarioBtn.isVisible().catch(() => false);
    assert.strictEqual(exists, true, `Scenario ${i} run button should be visible`);
  }

  console.log('All assertions passed!');
  await browser.close();
})().catch(err => {
  console.error('TEST FAILED as expected:', err.message);
  process.exit(1);
});
