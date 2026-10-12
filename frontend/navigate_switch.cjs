const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  console.log('1. Opening http://localhost:8443...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // Dismiss setup modal if displayed
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 2. Open Profile menu at bottom left
  console.log('2. Clicking profile dropdown in sidebar...');
  const profileWidgetBtn = page.locator('.profile-btn');
  if (await profileWidgetBtn.count() > 0) {
    await profileWidgetBtn.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(artDir, 'step_switch_1_dropdown.png') });
    console.log('Saved step_switch_1_dropdown.png');

    // Click Catch in the dropdown
    const switchCatch = page.locator('.switch-user-btn').filter({ hasText: /Catch/i });
    if (await switchCatch.count() > 0) {
      console.log('Switching to Catch...');
      await switchCatch.click();
      await page.waitForTimeout(1500);
    }
  }

  // 3. Go to Resources tab
  console.log('3. Navigating to Resources tab...');
  const resNav = page.locator('.nav-item').filter({ hasText: /Resources/i });
  if (await resNav.count() > 0) {
    await resNav.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_2_resources.png') });
    console.log('Saved step_switch_2_resources.png');
  }

  // 4. Click the saved Photosynthesis set
  console.log('4. Selecting Photosynthesis and Cellular Respiration button...');
  const photoBtn = page.locator('button').filter({ hasText: /Photosynthesis/i }).first();
  if (await photoBtn.count() > 0) {
    await photoBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_3_photosynthesis_set.png') });
    console.log('Saved step_switch_3_photosynthesis_set.png');
  }

  // 5. Open Key notes to show generated content
  console.log('5. Opening Key notes...');
  const notesAction = page.locator('.resource-action-grid button').filter({ hasText: /Key notes/i });
  if (await notesAction.count() > 0) {
    await notesAction.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_4_key_notes.png') });
    console.log('Saved step_switch_4_key_notes.png');

    // Return to Resources
    const backBtn = page.locator('.back-link');
    if (await backBtn.count() > 0) await backBtn.click();
    await page.waitForTimeout(1000);
  }

  // 6. Open Quiz & Reviewer
  console.log('6. Opening Quiz & Reviewer...');
  const quizAction = page.locator('.resource-action-grid button').filter({ hasText: /Quiz/i });
  if (await quizAction.count() > 0) {
    await quizAction.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_5_quiz.png') });
    console.log('Saved step_switch_5_quiz.png');

    // Click option A
    const optA = page.locator('.quiz-options button').first();
    if (await optA.count() > 0) {
      await optA.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(artDir, 'step_switch_6_quiz_feedback.png') });
      console.log('Saved step_switch_6_quiz_feedback.png');
    }
  }

  // 7. Open Knowledge Map
  console.log('7. Navigating to Knowledge Map...');
  const kmapNav = page.locator('.nav-item').filter({ hasText: /Knowledge/i });
  if (await kmapNav.count() > 0) {
    await kmapNav.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_7_knowledge_map.png') });
    console.log('Saved step_switch_7_knowledge_map.png');
  }

  // 8. Open Reports
  console.log('8. Navigating to Reports...');
  const reportsNav = page.locator('.nav-item').filter({ hasText: /Reports/i });
  if (await reportsNav.count() > 0) {
    await reportsNav.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step_switch_8_reports.png') });
    console.log('Saved step_switch_8_reports.png');
  }

  await browser.close();
  console.log('Completed autonomous profile switch and navigation!');
})();
