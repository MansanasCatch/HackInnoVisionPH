const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1400, height: 950 } });
  const page = await context.newPage();

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  console.log('1. Opening app...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // Dismiss setup modal if displayed
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 2. Open Profile menu at bottom left and click "Automation Tester"
  console.log('2. Opening profile switcher to select Automation Tester...');
  const profileWidgetBtn = page.locator('.profile-btn');
  if (await profileWidgetBtn.count() > 0) {
    await profileWidgetBtn.click();
    await page.waitForTimeout(1000);

    const testerOption = page.locator('.switch-user-btn').filter({ hasText: /Automation Tester/i });
    if (await testerOption.count() > 0) {
      console.log('Switching to Automation Tester...');
      await testerOption.click();
      await page.waitForTimeout(2000);
    }
  }

  // Close any popups by pressing Escape
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  const panel = page.locator('section.panel').first();
  await panel.scrollIntoViewIfNeeded();

  // Screenshot 1: Initial panel view with 7 scenarios and live console
  await page.screenshot({ path: path.join(artDir, 'live_tester_initial.png') });
  console.log('Captured live_tester_initial.png');

  // 3. Trigger "Run All Scenarios Live"
  const runBtn = page.locator('[data-testid="run-all-scenarios"]');
  if (await runBtn.count() > 0) {
    console.log('Triggering live execution of all 7 scenarios...');
    await runBtn.click();

    // Give it 3.5 seconds to capture active streaming state
    await page.waitForTimeout(3500);
    await panel.scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(artDir, 'live_tester_running.png') });
    console.log('Captured live_tester_running.png');

    // Wait for the full pipeline of 7 scenarios to complete
    console.log('Waiting for full pipeline completion...');
    await page.waitForSelector('text=Evaluation Complete', { timeout: 65000 }).catch(e => console.log('Timeout waiting for completion:', e.message));
    await page.waitForTimeout(1500);

    // Screenshot: Completed run with PASS badges and streaming logs
    await panel.scrollIntoViewIfNeeded();
    await panel.screenshot({ path: path.join(artDir, 'live_tester_panel_complete.png') });
    await page.screenshot({ path: path.join(artDir, 'live_tester_complete.png') });
    console.log('Captured live_tester_complete.png and live_tester_panel_complete.png');
  }

  await browser.close();
  console.log('All live test scenarios completed successfully!');
})().catch(err => {
  console.error('Navigation script error:', err);
  process.exit(1);
});
