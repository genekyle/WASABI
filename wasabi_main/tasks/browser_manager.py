# browser_manager.py
from playwright.async_api import async_playwright
import os, random

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def launch_browser(self):
        def get_random_viewport():
            viewports = [
                {'width': 1920, 'height': 1080},  # Typical desktop
                {'width': 1366, 'height': 768}    # Common laptop
            ]
            weights = [75, 25]  # 75% chance for desktop, 25% for laptop
            chosen_viewport = random.choices(viewports, weights, k=1)[0]
            return chosen_viewport

        def get_random_geolocation():
        # Central geolocation coordinates for Chicago
            base_lat, base_lon = 41.8781, -87.6298
            geolocations = [
                {'latitude': base_lat, 'longitude': base_lon},  # Main address
                {'latitude': base_lat + 0.05, 'longitude': base_lon + 0.05},  # Some miles north-east
                {'latitude': base_lat - 0.05, 'longitude': base_lon - 0.05},  # Some miles south-west
                {'latitude': base_lat + 0.08, 'longitude': base_lon - 0.08},  # Some miles north-west
            ]
            weights = [66, 11, 11, 12]  # Weights as per your description
            chosen_geolocation = random.choices(geolocations, weights, k=1)[0]
            return chosen_geolocation
        
        if not self.playwright:
            self.playwright = await async_playwright().start()

        viewport = get_random_viewport()
        geolocation = get_random_geolocation()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[f'--user-agent={user_agent}'],
            proxy={
                "server": "http://45.203.245.56:7777",
                "username": "lu9118235",
                "password": "dcPbzD"
            }
        )
        self.context = await self.browser.new_context(
            viewport=viewport,
            geolocation=geolocation,
            permissions=['geolocation']
        )
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
