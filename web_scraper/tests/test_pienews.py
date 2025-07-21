import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://thepienews.com/london-mayor-slams-proposed-international-tuition-fee-levy/"

async def test_playwright_bs4_article_content(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set False if you want to see the browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="en-US",
            java_script_enabled=True,
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        try:
            print(f"Navigating to {url}")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # Optional: wait a bit for JS to render content fully
            await page.wait_for_timeout(3000)

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            article_div = soup.find("div", class_="single-content")
            if article_div:
                text = article_div.get_text(separator="\n", strip=True)
                print(f"Extracted article content (first 1000 chars):\n{text[:1000]}")
            else:
                print("Could not find the article div (.single-content) in the page")

        except Exception as e:
            print(f"Error during fetching/parsing: {e}")
        finally:
            await browser.close()

asyncio.run(test_playwright_bs4_article_content(URL))

