import asyncio
from playwright.async_api import async_playwright

class TestTask:
    def __init__(self, task_config):
        self.task_config = task_config

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto("https://www.google.com")
            await asyncio.sleep(5)  # For demonstration
            await browser.close()