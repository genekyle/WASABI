import asyncio
from playwright.async_api import Page
from tasks.subtasks.actions import GlobalActionTask
 
class IndeedLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.action_task = GlobalActionTask()  # Create an instance of GlobalActionTask

    async def login(self, page: Page):
        # Navigate to Indeed's main page
        await page.goto("https://www.indeed.com/")
        
        # Wait for the page to fully load and stabilize
        await page.wait_for_load_state('networkidle')
    
        # Find the login link by checking if the href contains the required URL
        login_url = "https://secure.indeed.com/account/login"
        login_button_xpath = f"//a[contains(@href, '{login_url}')]"
        
        # Use hover_and_click from action_task instance to interact with the login link
        await self.action_task.hover_and_click(
            page=page,
            xpath=login_button_xpath,
            element_description="Login Link Button - 'Sign In'",
            hover_pause_type="short",
            click_pause_type="medium"
        )
        
        # Check to see if the redirected page is the login page
        login_page_url = "https://secure.indeed.com/auth"
        login_page_span_xpath = "//span[contains(text(),'Create an account or sign in.')]"
        page_name = "Login Page"

        # Confirms navigation to the intended page
        if await self.action_task.confirm_navigation(
            page=page,
            page_name=page_name,
            expected_url_contains=login_page_url,
            xpath_selector=login_page_span_xpath,
            timeout=15000
        ):
            print(f"Confirmed Navigation to: {page_name}")
        else:
            print(f"Failed to Navigate to: {page_name}")

        await asyncio.sleep(100)  # For demonstration purposes