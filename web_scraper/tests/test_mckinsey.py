import aiohttp
import asyncio
from bs4 import BeautifulSoup

async def fetch_raw_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            return html

html = asyncio.run(fetch_raw_html("https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights"))
soup = BeautifulSoup(html, "html.parser")
print(soup.prettify()[:5000])  # Preview only
