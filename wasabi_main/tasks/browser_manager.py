# browser_manager.py
from playwright.async_api import async_playwright
import os

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def launch_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            proxy={
                "server": "http://45.203.245.56:7777",
                "username": "lu9118235",
                "password": "dcPbzD"
            }
        )
        self.context = await self.browser.new_context()
        return self.context

    async def close_browser(self):
        if self.context:
            await self.context.close()
            self.context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
