# indeed_task/login.py
import asyncio
from playwright.async_api import Page
from tasks.subtasks.actions import hover_and_click, confirm_navigation
 
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
        login_button_xpath = f"//a[contains(@href, '{login_url}')]"
        
        # Use hover_and_click from actions module to interact with the login link
        await hover_and_click(
            page=page,
            xpath=login_button_xpath,   # XPath of the element
            element_description="Login Link Button - 'Sign In'",  # Description of the element
            hover_pause_type="short",  # Pause type before hover
            click_pause_type="medium"  # Pause type before click
        )
        # Check to see if the redirected page is the login page
        login_page_url = "https://secure.indeed.com/auth"
        
        # Check to see if the header appears, looking for the text "Create an account or sign in"
        login_page_span_xpath = "//span[contains(text(),'Create an account or sign in.')]"
        page_name = "Login Page"

        # Confirms navigation to the intended page
        if await confirm_navigation(
            page=page,
            page_name=page_name,
            expected_url_contains=login_page_url,
            xpath_selector=login_page_span_xpath,
            timeout=15000
        ):
            print(f"Confirmed Navigation to: {page_name}")
        else:
            print(f"Failed to Navigate to: {page_name}")

        await asyncio.sleep(100)  # For demonstration
