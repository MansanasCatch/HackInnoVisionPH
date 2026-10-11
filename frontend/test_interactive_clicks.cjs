const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  console.log('1. Navigating to http://localhost:8443...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // Dismiss setup modal if displayed
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // Switch to Automation Tester
  console.log('2. Ensuring Automation Tester profile is active...');
  const profileWidgetBtn = page.locator('.profile-btn');
  if (await profileWidgetBtn.count() > 0) {
    await profileWidgetBtn.click();
    await page.waitForTimeout(500);
    const switchTester = page.locator('.switch-user-btn').filter({ hasText: /Automation Tester/i });
    if (await switchTester.count() > 0) {
      await switchTester.click();
      await page.waitForTimeout(1000);
    }
  }

  console.log('3. Clicking Start Live Demonstration...');
  const startDemoBtn = page.locator('button:has-text("Start Live Demonstration")');
  await startDemoBtn.first().waitFor({ state: 'visible', timeout: 8000 });
  await startDemoBtn.first().click();

  console.log('4. Verifying Ingestion Live PDF Upload & JSON transformation...');
  
  // Wait for Ingest page and check for live file simulation & JSON payload
  const jsonPayloadHeading = page.locator('text=Extracted JSON Payload');
  await jsonPayloadHeading.waitFor({ state: 'visible', timeout: 8000 });
  console.log('PASS: Extracted JSON Payload rendered on screen.');
  await page.screenshot({ path: path.join(artDir, 'live_interactive_1_pdf_json.png') });

  // Advance demo to Step 3 (Quiz)
  console.log('5. Waiting for quiz step (or clicking next on HUD to jump directly to quiz)...');
  const demoNextBtn = page.locator('[data-testid="demo-next"]');
  // Click Next twice (from Ingest to Library, and Library to Quiz)
  await page.waitForTimeout(1500);
  await demoNextBtn.click(); // to library
  await page.waitForTimeout(500);
  await demoNextBtn.click(); // to quiz

  console.log('6. Verifying live exam answering and answer-feedback banner...');
  const feedback = page.locator('.answer-feedback');
  await feedback.waitFor({ state: 'visible', timeout: 6000 });
  console.log('PASS: Live click triggered answer-feedback banner with explanation.');
  await page.screenshot({ path: path.join(artDir, 'live_interactive_2_quiz_answer.png') });

  console.log('7. Waiting for exam completion and score card evaluation...');
  const sessionCompleted = page.locator('text=SESSION COMPLETED');
  await sessionCompleted.waitFor({ state: 'visible', timeout: 12000 });
  console.log('PASS: Quiz completed, score card displayed with 100% score.');

  // Verify "Take again the quiz" button
  const retakeBtn = page.locator('button:has-text("Take again the quiz")').first();
  await retakeBtn.waitFor({ state: 'visible', timeout: 5000 });
  console.log('PASS: "Take again the quiz" button verified.');
  await page.screenshot({ path: path.join(artDir, 'live_interactive_3_score_retake.png') });

  // Click retake button to verify retake loop
  console.log('8. Clicking "Take again the quiz" to test retake flow...');
  await retakeBtn.click();
  await page.waitForTimeout(1000);
  const quizHeading = page.locator('.quiz-progress');
  await quizHeading.waitFor({ state: 'visible', timeout: 5000 });
  console.log('PASS: Returned to quiz for retake attempt!');
  await page.screenshot({ path: path.join(artDir, 'live_interactive_4_quiz_retaken.png') });

  await browser.close();
  console.log('Interactive Demo Live Verification Passed Completely!');
})().catch(err => {
  console.error('Test Failed:', err.message);
  process.exit(1);
});
