const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
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

  // Take screenshot of Home page with the active Automation Tester panel
  await page.screenshot({ path: path.join(artDir, 'tester_1_home_panel.png') });
  console.log('Captured tester_1_home_panel.png');

  // 3. Click "Run Live Evaluation Suite"
  const runBtn = page.locator('button').filter({ hasText: /Run Live Evaluation Suite/i });
  if (await runBtn.count() > 0) {
    console.log('Triggering live evaluation suite...');
    await runBtn.click();
    // Wait for the full pipeline (health, extraction, ai gen, persistence, sessions, knowledge map)
    await page.waitForSelector('text=Evaluation Complete', { timeout: 60000 }).catch(e => console.log('Timeout waiting for completion:', e.message));
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(artDir, 'tester_2_evaluation_passed.png') });
    console.log('Captured tester_2_evaluation_passed.png');
  }

  await browser.close();
  console.log('Automation Tester navigation complete!');
})();
