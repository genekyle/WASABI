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

        # Look for, click on and type in the username input
        email_address_input_xpath = "//input[contains(@type, 'email')]"
        await self.action_task.human_type(
            page=page,
            xpath=email_address_input_xpath,
            element_description="Email Input - Login",
            text=self.username
        )
        
        # Submit email to open password input
        submit_button_xpath = "//button[contains(@type,'submit')]"
        await self.action_task.hover_and_click(
            page=page,
            xpath=submit_button_xpath,
            element_description="Continue Button - Login",
            hover_pause_type="short",
            click_pause_type="medium"
        )
        self.action_task.random_wait("short")
        
        # Confirm that the password field has appeared
        password_input_xpath = "//input[contains(@type,'password')]"
        if await self.action_task.confirm_dynamic_update(page, "Password field appearance", password_input_xpath, timeout=15000):
            print("Password field appeared successfully.")
        else:
            print("Failed to observe the appearance of the password field.")

        # Look for, click on and type in the password input
        await self.action_task.human_type(
            page=page,
            xpath=password_input_xpath,
            element_description="Password Input - Login",
            text=self.password
        )
        await self.action_task.random_wait("short")
        
        # Sign in
        sign_in_button_xpath = "//button[contains(@data-tn-element,'submit')]"
        await self.action_task.hover_and_click(
            page=page,
            xpath=sign_in_button_xpath,
            element_description="Sign In Button - Login",
            hover_pause_type="short",
            click_pause_type="medium"
        )
        await self.action_task.random_wait("long")

        await asyncio.sleep(120)  # For demonstration purposes