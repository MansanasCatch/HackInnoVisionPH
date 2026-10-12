const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  console.log('Navigating to http://localhost:8443...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  // 1. Check if Setup Modal is open; if so, dismiss or pick profile
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start studying|Ready/i });
  if (await resumeBtn.count() > 0) {
    console.log('Dismissing setup screen...');
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 2. Click Resources tab in sidebar
  console.log('Navigating to Resources tab...');
  const resLink = page.locator('button').filter({ hasText: /^Resources$/i });
  if (await resLink.count() > 0) {
    await resLink.first().click();
    await page.waitForTimeout(1500);
  }
  await page.screenshot({ path: path.join(artDir, 'nav_1_resources.png') });
  console.log('Saved nav_1_resources.png');

  // 3. Switch to the saved study set "Photosynthesis and Cellular Respiration"
  const savedBtn = page.locator('button').filter({ hasText: /Photosynthesis/i });
  if (await savedBtn.count() > 0) {
    console.log('Selecting saved study set...');
    await savedBtn.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'nav_2_saved_selected.png') });
    console.log('Saved nav_2_saved_selected.png');
  }

  // 4. Click Quiz & Reviewer
  const quizAction = page.locator('button').filter({ hasText: /Quiz/i });
  if (await quizAction.count() > 0) {
    console.log('Navigating to Quiz...');
    await quizAction.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'nav_3_quiz_question.png') });
    console.log('Saved nav_3_quiz_question.png');

    // Click first answer option
    const opt = page.locator('.quiz-options button').first();
    if (await opt.count() > 0) {
      console.log('Selecting answer...');
      await opt.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(artDir, 'nav_4_quiz_feedback.png') });
      console.log('Saved nav_4_quiz_feedback.png');
    }
  }

  // 5. Navigate to Knowledge Map
  console.log('Navigating to Knowledge Map...');
  const kmapLink = page.locator('button').filter({ hasText: /Knowledge Map/i });
  if (await kmapLink.count() > 0) {
    await kmapLink.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'nav_5_knowledge_map.png') });
    console.log('Saved nav_5_knowledge_map.png');
  }

  // 6. Navigate to Reports
  console.log('Navigating to Reports...');
  const reportLink = page.locator('button').filter({ hasText: /^Reports$/i });
  if (await reportLink.count() > 0) {
    await reportLink.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'nav_6_reports.png') });
    console.log('Saved nav_6_reports.png');
  }

  await browser.close();
  console.log('Navigation complete!');
})();
