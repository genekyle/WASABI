# indeed_task/login.py
import asyncio
from playwright.async_api import Page
from tasks.subtasks.actions import hover_and_click

 
class IndeedLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def login(self, page: Page):
        # Navigate to Indeed's main page
        await page.goto("https://www.indeed.com/")
        
        # Wait for the page to fully load and stabilize
        await page.wait_for_load_state('networkidle')
    

        # Find the login link by checking if the href contains the required URL
        login_url = "https://secure.indeed.com/account/login"
        login_xpath = f"//a[contains(@href, '{login_url}')]"
        
        # Use hover_and_click from actions module to interact with the login link
        await hover_and_click(page, login_xpath, "login link button","short","medium")
        await asyncio.sleep(100)  # For demonstration
