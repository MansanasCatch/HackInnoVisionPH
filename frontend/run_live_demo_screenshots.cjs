const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1400, height: 950 } });
  const page = await context.newPage();

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  console.log('1. Opening application...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // Dismiss setup modal if displayed
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // Switch to Automation Tester
  console.log('2. Selecting Automation Tester profile...');
  const profileWidgetBtn = page.locator('.profile-btn');
  if (await profileWidgetBtn.count() > 0) {
    await profileWidgetBtn.click();
    await page.waitForTimeout(1000);

    const testerOption = page.locator('.switch-user-btn').filter({ hasText: /Automation Tester/i });
    if (await testerOption.count() > 0) {
      await testerOption.click();
      await page.waitForTimeout(1500);
    }
  }

  // 3. Start Live Demonstration
  console.log('3. Starting Live Demonstration...');
  const demoBtn = page.locator('[data-testid="start-live-demo"]');
  await demoBtn.click();
  await page.waitForTimeout(1500);

  // Pause auto-advance so we can capture each screen cleanly
  const pauseBtn = page.locator('[data-testid="demo-toggle-pause"]');
  if (await pauseBtn.count() > 0 && await pauseBtn.innerText() === '⏸ Pause') {
    await pauseBtn.click();
  }

  const stepNames = [
    'demo_step_1_ingest.png',
    'demo_step_2_resources.png',
    'demo_step_3_quiz.png',
    'demo_step_4_knowledge.png',
    'demo_step_5_report.png',
    'demo_step_6_settings.png',
  ];

  for (let i = 0; i < stepNames.length; i++) {
    const filename = stepNames[i];
    console.log(`Capturing ${filename}...`);
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, filename) });

    if (i < stepNames.length - 1) {
      const nextBtn = page.locator('[data-testid="demo-next"]');
      await nextBtn.click();
      await page.waitForTimeout(1500);
    }
  }

  console.log('Live demonstration capture finished successfully!');
  await browser.close();
})().catch(err => {
  console.error('Error during demo capture:', err);
  process.exit(1);
});
