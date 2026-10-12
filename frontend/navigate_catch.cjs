const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';

  console.log('Opening http://localhost:8443...');
  await page.goto('http://localhost:8443');
  await page.waitForTimeout(2000);

  // 1. If Setup or Profile modal is open, click Catch (ID #1) or switch to Catch
  // Let's find profile button at bottom left
  const profileSwitch = page.locator('button').filter({ hasText: /Juan|Catch|Jane|Tasha/i });
  if (await profileSwitch.count() > 0) {
    console.log('Clicking profile switcher...');
    await profileSwitch.first().click();
    await page.waitForTimeout(1000);

    // Look for Catch in profile list
    const catchOption = page.locator('button, div').filter({ hasText: /Catch/i });
    if (await catchOption.count() > 0) {
      console.log('Selecting Catch (ID #1)...');
      await catchOption.first().click();
      await page.waitForTimeout(1500);
    }
  }

  // Dismiss any remaining dialog
  const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
  if (await resumeBtn.count() > 0) {
    await resumeBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 2. Go to Resources
  console.log('Navigating to Resources...');
  const resLink = page.locator('button').filter({ hasText: /^Resources$/i });
  if (await resLink.count() > 0) {
    await resLink.first().click();
    await page.waitForTimeout(2000);
  }
  await page.screenshot({ path: path.join(artDir, 'step1_resources_with_saved_sets.png') });
  console.log('Captured step1_resources_with_saved_sets.png');

  // 3. Click the saved set: "Photosynthesis and Cellular Respiration"
  const savedButton = page.locator('button').filter({ hasText: /Photosynthesis/i });
  if (await savedButton.count() > 0) {
    console.log('Clicking Photosynthesis study set button...');
    await savedButton.first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(artDir, 'step2_photosynthesis_loaded.png') });
    console.log('Captured step2_photosynthesis_loaded.png');
  }

  // 4. Click Key notes to inspect the generated notes
  const notesBtn = page.locator('button').filter({ hasText: /Key notes/i });
  if (await notesBtn.count() > 0) {
    console.log('Opening Key notes...');
    await notesBtn.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step3_key_notes_viewer.png') });
    console.log('Captured step3_key_notes_viewer.png');

    // Return to Resources
    const backBtn = page.locator('button').filter({ hasText: /Learning Resources/i });
    if (await backBtn.count() > 0) await backBtn.first().click();
    await page.waitForTimeout(1000);
  }

  // 5. Open Quiz & Reviewer
  const quizBtn = page.locator('button').filter({ hasText: /Quiz & reviewer/i });
  if (await quizBtn.count() > 0) {
    console.log('Opening Quiz & reviewer...');
    await quizBtn.first().click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(artDir, 'step4_quiz_viewer.png') });
    console.log('Captured step4_quiz_viewer.png');

    // Click an option to see live explanation feedback
    const firstOpt = page.locator('.quiz-options button').first();
    if (await firstOpt.count() > 0) {
      await firstOpt.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(artDir, 'step5_quiz_live_feedback.png') });
      console.log('Captured step5_quiz_live_feedback.png');
    }
  }

  // 6. Navigate to Knowledge Map
  console.log('Opening Knowledge Map...');
  const kmapLink = page.locator('button').filter({ hasText: /Knowledge/i });
  if (await kmapLink.count() > 0) {
    await kmapLink.first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(artDir, 'step6_knowledge_map.png') });
    console.log('Captured step6_knowledge_map.png');
  }

  // 7. Navigate to Reports
  console.log('Opening Reports...');
  const reportsLink = page.locator('button').filter({ hasText: /^Reports$/i });
  if (await reportsLink.count() > 0) {
    await reportsLink.first().click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(artDir, 'step7_reports.png') });
    console.log('Captured step7_reports.png');
  }

  await browser.close();
  console.log('All steps executed successfully!');
})();
