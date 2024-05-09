import asyncio, random
from playwright.async_api import Page
from tasks.subtasks.actions import GlobalActionTask
 
class IndeedLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.action_task = GlobalActionTask()  # Create an instance of GlobalActionTask
    
    async def onboarding_redirect1(self, page):
        print("Performing onboarding_redirect 1...")
        # Use hover_and_click to click on the indeed logo to redirect to homepage button during the onboarding page
        indeed_logo_xpath = "//a[contains(@data-gnav-element-name, 'Logo')]"
        indeed_home_job_feed_xpath = "//button[contains(@aria-controls, 'jobfeed-content')]"
        steps = [
            {
                'type': 'hover_and_click',
                'params': {
                    'xpath': indeed_logo_xpath,
                    'element_description': "Indeed Logo",
                    'hover_pause_type': "short",
                    'click_pause_type': "medium"
                }
            },
            {
                'type': 'confirm_navigation',
                'params': {
                    'page_name': "Indeed Home Page - Logged In",
                    'outcomes' : {
                        "https://www.indeed.com/": [f"{indeed_home_job_feed_xpath}"]
                    },
                    'timeout': 15000
                }
            }
        ]
        await self.action_task.perform_steps(page, steps)

    async def onboarding_redirect2(self, page):
        print("Performing onboarding_redirect 2...")
        onboarding_skip_button_xpath = "//button[contains(@data-tn-element,'skip-section')]"
        onboarding_pay_h1_xpath = """//h1[contains(text(),"What's the minimum pay you're looking for?")]"""
        onboarding_job_h1_xpath = """//h1[contains(text(),"What job are you looking for?")]"""
        indeed_home_job_feed_xpath = "//button[contains(@aria-controls, 'jobfeed-content')]"
        steps = [
            {
                'type': 'hover_and_click',
                'params': {
                    'xpath': onboarding_skip_button_xpath,
                    'element_description': "Onboarding Skip Button",
                    'hover_pause_type': "short",
                    'click_pause_type': "medium"
                }
            },
            {
                'type': 'confirm_navigation',
                'params': {
                    'page_name': "Indeed Job Search Onboarding - Pay Amount",
                    'outcomes': {
                        "https://onboarding.indeed.com/onboarding/pay": [f"{onboarding_pay_h1_xpath}"]
                    },
                    'timeout': 15000
                }
            },
            {
                'type': 'hover_and_click',
                'params': {
                    'xpath': onboarding_skip_button_xpath,
                    'element_description': "Onboarding Skip Button",
                    'hover_pause_type': "short",
                    'click_pause_type': "medium"
                }
            },
            {
                'type': 'confirm_navigation',
                'params': {
                    'page_name': "Indeed Job Search Onboarding - Desired Job",
                    'outcomes': {
                        "https://onboarding.indeed.com/onboarding/desired-job": [f"{onboarding_job_h1_xpath}"]
                    },
                    'timeout': 15000
                }
            },
            {
                'type': 'hover_and_click',
                'params': {
                    'xpath': onboarding_skip_button_xpath,
                    'element_description': "Onboarding Skip Button",
                    'hover_pause_type': "short",
                    'click_pause_type': "medium"
                }
            },
            {
                'type': 'confirm_navigation',
                'params': {
                    'page_name': "Indeed Home Page - Logged In",
                    'outcomes': {
                        "https://www.indeed.com/": [f"{indeed_home_job_feed_xpath}"]
                    },
                    'timeout': 15000
                }
            }
        ]
        await self.action_task.perform_steps(page, steps)

    async def onboarding_redirect3(self, page):
        print("Performing onboarding_redirect 3...")
        indeed_home_button_xpath = "//a[contains(@id,'FindJobs')]"
        indeed_home_job_feed_xpath = "//button[contains(@aria-controls, 'jobfeed-content')]"
        steps = [
            {
                'type': 'hover_and_click',
                'params': {
                    'xpath': indeed_home_button_xpath,
                    'element_description': "Indeed Logo",
                    'hover_pause_type': "short",
                    'click_pause_type': "medium"
                }
            },
            {
                'type': 'confirm_navigation',
                'params': {
                    'page_name': "Indeed Home Page - Logged In",
                    'outcomes': {
                        "https://www.indeed.com/": [f"{indeed_home_job_feed_xpath}"]
                    },
                    'timeout': 15000
                }
            }
        ]
        await self.action_task.perform_steps(page, steps)

    async def handle_onboarding(self, page):
        print("Handling onboarding logic...")
        action = random.choice([self.onboarding_redirect1, self.onboarding_redirect2, self.onboarding_redirect1])
        await action(page)  # Execute the chosen action


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
        page_name = "Login Page"
        # Single URL and Element
        outcomes = {
            "https://secure.indeed.com/auth": ["//span[contains(text(),'Create an account or sign in.')]"]
        }

        # Confirms navigation to the intended page
        login_page_navigation = await self.action_task.confirm_navigation(
            page=page,
            page_name=page_name,
            outcomes=outcomes,
            timeout=15000
        )
        if login_page_navigation['url_confirmed']:
            print(f"Successfully navigated to and confirmed elements on: {login_page_navigation['url_confirmed']}")
        else:
            print("Failed to navigate to the login page or confirm the submit button.")

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
        await self.action_task.random_wait("short")
        # Check for CAPTCHA
        captcha_detected = await self.action_task.check_for_captcha_and_pause(page)
        if captcha_detected:
            print("CAPTCHA resolved, proceeding with further actions.")
            await self.action_task.hover_and_click(
            page=page,
            xpath=submit_button_xpath,
            element_description="Continue Button - Login",
            hover_pause_type="short",
            click_pause_type="medium"
        )
        else:
            print("Proceeding without CAPTCHA intervention.")
        
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
        captcha_detected = await self.action_task.check_for_captcha_and_pause(page)
        if captcha_detected:
            print("CAPTCHA resolved, proceeding with further actions.")
            await self.action_task.hover_and_click(
            page=page,
            xpath=sign_in_button_xpath,
            element_description="Sign In Button - Login",
            hover_pause_type="short",
            click_pause_type="medium"
        )
        else:
            print("Proceeding without CAPTCHA intervention.")
        
        # Multiple URLs and Elements
        outcomes = {
            "https://onboarding.indeed.com/onboarding/": ["""//h1[contains(text(),"Let's make sure your preferences are up-to-date.")]"""],
            "https://www.indeed.com/": ["//button[contains(@aria-controls, 'jobfeed')]"]
        }

        navigation_result = await self.action_task.confirm_navigation(
            page=page,
            page_name="Post-Login Page",
            outcomes=outcomes,
            timeout=15000
        )

        if navigation_result['url_confirmed']:
            print(f"Confirmed navigation to: {navigation_result['url_confirmed']}")
            print(f"Confirmed element: {navigation_result['element_confirmed']}")

            if navigation_result['url_confirmed'] == "https://onboarding.indeed.com/onboarding/":
                print(f"Navigated To the onboarding page for indeed")
                await self.handle_onboarding(page)
                print("Fully Logged Into Indeed")
                return True
            
            elif navigation_result['url_confirmed'] == "https://www.indeed.com/":
                print("Fully Logged Into Indeed")
                return True
            
        else:
            print("Navigation check failed for login, returning false.")


        