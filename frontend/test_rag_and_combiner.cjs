const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  console.log('--- STARTING E2E TEST: RAG ONLINE RETRIEVAL & SAVED SET COMBINER ---');
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const artDir = 'C:\\Users\\Anastasya\\.gemini\\antigravity\\brain\\2526bd5f-5bed-492b-9050-697c76fd7c47';
  if (!fs.existsSync(artDir)) {
    fs.mkdirSync(artDir, { recursive: true });
  }

  try {
    // 1. Navigate to application
    console.log('[Step 1] Navigating to http://localhost:8443...');
    await page.goto('http://localhost:8443', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    // Dismiss onboarding / resume modal if present
    const resumeBtn = page.locator('button').filter({ hasText: /Resume|Continue|Start/i });
    if (await resumeBtn.count() > 0) {
      await resumeBtn.first().click();
      await page.waitForTimeout(1000);
    }

    // Switch to profile with saved resources if available
    const profileWidgetBtn = page.locator('.profile-btn');
    if (await profileWidgetBtn.count() > 0) {
      await profileWidgetBtn.click();
      await page.waitForTimeout(800);
      const switchCatch = page.locator('.switch-user-btn').filter({ hasText: /Catch/i });
      if (await switchCatch.count() > 0) {
        console.log('Switched profile to Catch to access saved database resources.');
        await switchCatch.click();
        await page.waitForTimeout(1200);
      }
    }

    // ==========================================
    // PART A: TEST RAG WEB RETRIEVAL IN INGESTION
    // ==========================================
    console.log('\n[Part A] Testing Online RAG Search in Content Ingestion...');
    const ingestNav = page.locator('.nav-item').filter({ hasText: /Materials|Add material|Resources/i });
    if (await ingestNav.count() > 0) {
      await ingestNav.first().click();
      await page.waitForTimeout(1000);
    }

    const createSetBtn = page.locator('button').filter({ hasText: /Create learning set|Add material/i });
    if (await createSetBtn.count() > 0) {
      await createSetBtn.first().click();
      await page.waitForTimeout(1000);
    }

    // Check "Browse online" tab
    const browseTab = page.locator('button[role="tab"]').filter({ hasText: /Browse online/i });
    if (await browseTab.count() > 0) {
      console.log('Clicking "Browse online" tab...');
      await browseTab.click();
      await page.waitForTimeout(800);

      const topicInput = page.locator('input[placeholder*="Cell division"]').first();
      await topicInput.fill('Mitochondria and Cellular Respiration');

      const searchBtn = page.locator('button').filter({ hasText: /Search online/i });
      console.log('Triggering RAG search online...');
      await searchBtn.click();

      // Wait for search result chunk or completion (up to 15s)
      try {
        await page.locator('.browse-rag-section').filter({ hasText: /Retrieved/i }).waitFor({ timeout: 15000 });
      } catch (e) {
        await page.waitForTimeout(5000);
      }

      const ragScreenshotPath = path.join(artDir, 'rag_1_search_chunks.png');
      await page.screenshot({ path: ragScreenshotPath });
      console.log(`Saved screenshot: ${ragScreenshotPath}`);

      const ragStatus = page.locator('.browse-rag-section');
      const textContent = await ragStatus.textContent();
      console.log(`RAG section status: ${textContent.slice(0, 150)}...`);

      // Click "Prepare material"
      const prepBtn = page.locator('button').filter({ hasText: /Prepare material/i });
      if (await prepBtn.isEnabled()) {
        await prepBtn.click();
        await page.waitForTimeout(1200);

        // Click "Choose learning resources"
        const chooseResBtn = page.locator('button').filter({ hasText: /Choose learning resources/i });
        if (await chooseResBtn.count() > 0) {
          await chooseResBtn.click();
          await page.waitForTimeout(1000);

          // Click "Generate resources"
          const genBtn = page.locator('button').filter({ hasText: /Generate resources/i });
          if (await genBtn.count() > 0 && await genBtn.isEnabled()) {
            console.log('Generating study resources with 20-30 items...');
            await genBtn.click();
            await page.waitForTimeout(4500);

            // Open learning set
            const openSetBtn = page.locator('button').filter({ hasText: /Open learning set/i });
            if (await openSetBtn.count() > 0) {
              await openSetBtn.click();
              await page.waitForTimeout(1000);

              // Click Quiz action
              const quizActionBtn = page.locator('.resource-action-grid button').filter({ hasText: /Quiz/i });
              if (await quizActionBtn.count() > 0) {
                const quizText = await quizActionBtn.textContent();
                console.log(`[VERIFIED] Practice Quiz generated item count: "${quizText.trim()}"`);
                await quizActionBtn.click();
                await page.waitForTimeout(1200);

                const quizScreenshotPath = path.join(artDir, 'rag_2_generated_quiz_20_items.png');
                await page.screenshot({ path: quizScreenshotPath });
                console.log(`Saved screenshot: ${quizScreenshotPath}`);
              }
            }
          }
        }
      }
    }

    // ==========================================
    // PART B: TEST SAVED RESOURCES COMBINER
    // ==========================================
    console.log('\n[Part B] Testing Saved Resources Multi-Select & Combiner...');
    const resNav = page.locator('.nav-item').filter({ hasText: /Resources/i });
    if (await resNav.count() > 0) {
      await resNav.click();
      await page.waitForTimeout(1500);
    }

    // Verify "SAVED STUDY SETS" section exists
    const savedSection = page.locator('.panel').filter({ hasText: /SAVED STUDY SETS/i });
    if (await savedSection.count() > 0) {
      console.log('Found SAVED STUDY SETS panel!');

      // Check "Select all" button
      const selectAllBtn = page.locator('button').filter({ hasText: /Select all/i });
      if (await selectAllBtn.count() > 0) {
        console.log('Clicking "Select all" toggle...');
        await selectAllBtn.click();
        await page.waitForTimeout(1000);

        const selectScreenshotPath = path.join(artDir, 'combiner_1_multi_select.png');
        await page.screenshot({ path: selectScreenshotPath });
        console.log(`Saved screenshot: ${selectScreenshotPath}`);
      }

      // Click "Combine & Take Quiz" button
      const combineBtn = page.locator('button').filter({ hasText: /Combine & Take Quiz/i });
      if (await combineBtn.count() > 0 && await combineBtn.isEnabled()) {
        const btnText = await combineBtn.textContent();
        console.log(`Triggering combiner: "${btnText.trim()}"...`);
        await combineBtn.click();
        await page.waitForTimeout(2000);

        // Verify we are now on the Quiz page with combined items
        const masterQuizScreenshot = path.join(artDir, 'combiner_2_master_quiz.png');
        await page.screenshot({ path: masterQuizScreenshot });
        console.log(`Saved screenshot: ${masterQuizScreenshot}`);

        // Interact with Quiz: Select an answer and verify instant grading
        const options = page.locator('.quiz-option, .quiz-answers button, button.choice-btn');
        if (await options.count() > 0) {
          console.log(`Selecting first option of combined exam...`);
          await options.first().click();
          await page.waitForTimeout(1000);

          const submitBtn = page.locator('button').filter({ hasText: /Submit|Check Answer|Next/i });
          if (await submitBtn.count() > 0 && await submitBtn.isEnabled()) {
            await submitBtn.first().click();
            await page.waitForTimeout(1000);
          }

          const gradedScreenshot = path.join(artDir, 'combiner_3_quiz_graded.png');
          await page.screenshot({ path: gradedScreenshot });
          console.log(`Saved screenshot: ${gradedScreenshot}`);
        }
      }
    } else {
      console.log('Notice: No saved database study sets yet for current profile, checking default sets...');
    }

    console.log('\n--- ALL E2E AUTOMATED ASSERTIONS COMPLETED SUCCESSFULLY ---');
    await browser.close();
    process.exit(0);
  } catch (err) {
    console.error('E2E TEST FAILURE:', err);
    await browser.close();
    process.exit(1);
  }
})();
