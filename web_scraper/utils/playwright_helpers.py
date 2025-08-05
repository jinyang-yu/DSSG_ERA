
async def scroll_page_to_bottom(page):
  """
  Scrolls the page to the bottom by increments to trigger dynamic content loading.

  Args:
    page (playwright.async_api.Page): Playwright page object.
  """
  try:
    await page.evaluate("""async () => {
        await new Promise(resolve => {
            let totalHeight = 0;
            const distance = 300;
            const timer = setInterval(() => {
                window.scrollBy(0, distance);
                totalHeight += distance;
                if (totalHeight >= document.body.scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 200);
        });
    }""")
    await page.wait_for_timeout(1000)
  except Exception as e:
    print("Scroll failed:", e)

async def handle_cookie_banner(page):
  """
  Attempts to accept cookie banner if present by clicking the accept button.

  Args:
      page (playwright.async_api.Page): Playwright page object.
  """
  try:
    await page.locator("#onetrust-accept-btn-handler").click(timeout=5000)
    await page.wait_for_timeout(1000)
    print("Accepted cookies.")
  except Exception:
    print("No cookie banner found or failed to click.")