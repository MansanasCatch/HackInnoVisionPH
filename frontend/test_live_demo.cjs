const { chromium } = require('playwright');
const assert = require('assert');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1300, height: 900 } });
  const page = await context.newPage();

  console.log('1. Opening app...');
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

  console.log('2. Checking for Start Live Demonstration button...');
  const demoBtn = page.locator('[data-testid="start-live-demo"]');
  const demoBtnVisible = await demoBtn.isVisible().catch(() => false);
  assert.strictEqual(demoBtnVisible, true, 'Start Live Demonstration button must be visible');

  console.log('3. Clicking Start Live Demonstration...');
  await demoBtn.click();
  await page.waitForTimeout(1000);

  const hud = page.locator('[data-testid="live-demo-hud"]');
  const hudVisible = await hud.isVisible().catch(() => false);
  assert.strictEqual(hudVisible, true, 'Live Demo HUD must be visible when demonstration is active');

  console.log('4. Checking Next Step navigation...');
  const nextBtn = page.locator('[data-testid="demo-next"]');
  await nextBtn.click();
  await page.waitForTimeout(1000);

  console.log('5. Exiting demo...');
  const exitBtn = page.locator('[data-testid="demo-exit"]');
  await exitBtn.click();
  await page.waitForTimeout(1000);

  const hudAfterExit = await hud.isVisible().catch(() => false);
  assert.strictEqual(hudAfterExit, false, 'Live Demo HUD should be dismissed after exit');

  console.log('All Live Demonstration test assertions passed!');
  await browser.close();
})().catch(err => {
  console.error('TEST FAILED as expected (RED):', err.message);
  process.exit(1);
});
