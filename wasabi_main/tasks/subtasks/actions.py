import asyncio
import random
import logging
from typing import Optional, Callable, Any, List, Dict
from playwright.async_api import Page, TimeoutError
from functools import wraps
from asyncio import Event

logging.basicConfig(level=logging.INFO)

class GlobalActionTask:
    def __init__(self):
        # Dictionary to store mosue coordinates/position
        self.mouse_tracker = {'x': None, 'y': None}
        self.interaction_allowed = Event()
        self.interaction_allowed.set()  # Initially allow interaction
        self.action_registry = {
            'hover_and_click': self.hover_and_click,
            'confirm_navigation': self.confirm_navigation,
            'check_input_value': self.check_input_value  # Adding the new method
        }

    def handle_element_errors(func):
        """Decorator to handle errors for actions performed on page elements, capturing all arguments flexibly."""
        @wraps(func)  # Use wraps to preserve metadata like the function's name and docstring
        async def wrapper(self, *args, **kwargs):
            # Extract element_description intelligently based on args or kwargs
            element_description = kwargs.get('element_descripti on', args[1] if len(args) > 1 else 'Unknown element')
            try:
                return await func(self, *args, **kwargs)
            except TimeoutError as e:
                logging.error(f"Timeout error while interacting with {element_description}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while interacting with {element_description}: {e}")
        return wrapper
    
    async def check_for_captcha_and_pause(self, page: Page):
        """
        Check for the presence of a CAPTCHA challenge based on a known selector and pause automation for manual resolution.
        Wait for a 'success' message to ensure CAPTCHA was correctly solved.

        Args:
            page (Page): The Playwright page object to check for CAPTCHA.

        Returns:
            bool: True if CAPTCHA was detected and resolved, False otherwise.
        """
        try:
            # Specific CAPTCHA container with a descendant link containing 'cloudflare'
            await page.wait_for_selector("//div[@id='content'][.//a[contains(@href, 'cloudflare')]]", state="visible", timeout=10000)
            print("CAPTCHA detected. Please solve the CAPTCHA manually.")
            self.interaction_allowed.clear()  # Block further interactions

            # Wait for the success div to become visible, indicating CAPTCHA has been solved
            await page.wait_for_selector("//div[@id='success'][contains(@style, 'visible')]", state="visible", timeout=30000)
            print("CAPTCHA solved. Resuming automation.")
            self.interaction_allowed.set()  # Allow interactions again
            return True
        except TimeoutError:
            print("Timeout occurred: CAPTCHA was not solved in time or did not appear.")
            self.interaction_allowed.set()  # Ensure interactions are allowed if an error occurs
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            self.interaction_allowed.set()  # Ensure interactions are allowed if an error occurs
            return False


    def random_pause_type(self) -> str:
        """Randomly select a pause type: 'short', 'medium', or 'long'."""
        return random.choice(["short", "medium", "long"])

    def random_wait_duration(self, pause_type: str) -> float:
        """Return a random wait duration based on the specified pause type."""
        pause_durations = {
            "short": (0.5, 1.5),
            "medium": (3, 8),
            "long": (5, 10)
        }
        min_time, max_time = pause_durations[pause_type]
        return random.uniform(min_time, max_time)

    async def random_wait(self, pause_type: Optional[str] = None):
        """Wait for a random amount of time based on the specified or random pause type."""
        if pause_type is None:
            pause_type = self.random_pause_type()
        wait_time = self.random_wait_duration(pause_type)
        await asyncio.sleep(wait_time)

    async def get_target_coordinates(self, page, selector):
        """
        Calculate the center coordinates of an element given its selector.
        
        Args:
            page (Page): The Playwright page object.
            selector (str): The selector of the element to find the center of.

        Returns:
            tuple: A tuple containing the x and y coordinates of the element's center.
        """
        element = await page.wait_for_selector(selector)
        box = await element.bounding_box()
        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2
        return center_x, center_y


    def calculate_bezier_point(self, t, start, control1, control2, end):
        """Calculate a point in a cubic Bezier curve."""
        return (1 - t)**3 * start + 3 * (1 - t)**2 * t * control1 + 3 * (1 - t) * t**2 * control2 + t**3 * end

    async def smooth_mouse_move(self, page: Page, start_x, start_y, end_x, end_y):
        """Smoothly moves the mouse from start to end coordinates using a Bezier curve."""
        logging.info(f"Starting mouse movement from ({start_x}, {start_y})")
        
        # Control points could be randomized slightly to make the curve less predictable
        control1_x = start_x + (end_x - start_x) * 0.3 + random.randint(-10, 10)
        control1_y = start_y + (end_y - start_y) * 0.3 + random.randint(-10, 10)
        control2_x = start_x + (end_x - start_x) * 0.6 + random.randint(-10, 10)
        control2_y = start_y + (end_y - start_y) * 0.6 + random.randint(-10, 10)

        steps = 30  # More steps for smoother motion
        for step in range(steps):
            t = step / float(steps)
            x = self.calculate_bezier_point(t, start_x, control1_x, control2_x, end_x)
            y = self.calculate_bezier_point(t, start_y, control1_y, control2_y, end_y)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.02, 0.05))  # Short delay to mimic human speed

        logging.info(f"Ending mouse movement at ({end_x}, {end_y})")

    @handle_element_errors
    async def hover_and_click(self, page: Page, xpath: str, element_description: str,
                              hover_pause_type: Optional[str] = None,
                              click_pause_type: Optional[str] = None):
        element = await page.wait_for_selector(xpath, state='visible')
        if not await element.is_visible():
            raise Exception(f"The element {element_description} is not visible.")

        target_x, target_y = await self.get_target_coordinates(page, xpath)

        # Move from the last known mouse position to the new element
        if self.mouse_tracker['x'] is not None and self.mouse_tracker['y'] is not None:
            await self.smooth_mouse_move(page, self.mouse_tracker['x'], self.mouse_tracker['y'], target_x, target_y)
        else:
            await page.mouse.move(target_x, target_y)

        # Update the mouse tracker with the new position
        self.mouse_tracker['x'], self.mouse_tracker['y'] = target_x, target_y

        # Random wait before hovering
        await self.random_wait(hover_pause_type)
        
        # Hover using precise coordinates
        await page.mouse.move(target_x, target_y)
        
        # Random wait after hovering and before clicking
        await self.random_wait(click_pause_type)
        
        # Click using precise coordinates
        await page.mouse.click(target_x, target_y)
        
        # Random wait after clicking
        await self.random_wait(click_pause_type)

        print(f"Successfully hovered over and clicked on {element_description}, using click pause type: {click_pause_type} and hover pause type: {hover_pause_type}.")
    
    @handle_element_errors
    async def confirm_dynamic_update(self, page: Page, update_description: str, expected_xpath: str, 
                                    timeout: int = 10000, state: str = "visible"):
        """
        Confirm that a dynamic update has occurred on the page by checking for the presence or absence of an element.

        Args:
            page (Page): The Playwright page object on which the check is performed.
            update_description (str): A description of the update expected, used for logging and error messages.
            expected_xpath (str): The XPath of the element that should appear or disappear as confirmation of the update.
            timeout (int): The maximum time, in milliseconds, to wait for the element to reach the desired state.
            state (str): The state to wait for, 'visible' for element appearance, 'hidden' for disappearance.

        Returns:
            bool: True if the update is confirmed by the element's state change, False otherwise.

        Raises:
            TimeoutError: If the element does not reach the desired state within the timeout.
        """
        try:
            if state == "visible":
                await page.wait_for_selector(f'xpath={expected_xpath}', state="attached", timeout=timeout)
                print(f"Update confirmed: {update_description}, {expected_xpath} is now visible.")
            elif state == "hidden":
                await page.wait_for_selector(f'xpath={expected_xpath}', state="detached", timeout=timeout)
                print(f"Update confirmed: {update_description}, {expected_xpath} is now hidden.")
            return True
        except TimeoutError as e:
            print(f"Failed to confirm dynamic update for {update_description}. Error: {e}")
            return False
    
    @handle_element_errors
    async def check_input_value(self, page: Page, input_description: str, expected_value: str, xpath: str):
        """
        Checks if the input field contains the expected value.

        Args:
            page (Page): The Playwright page object where actions are performed.
            expected_value (str): The value that is expected to be in the input field.
            xpath (str): The XPath to the input field.

        Returns:
            bool: True if the input field contains the expected value, False otherwise.
        """
        # Retrieve the current value from the input field
        current_value = await page.input_value(xpath)

        # Compare the current value with the expected value
        if current_value == expected_value:
            print(f"Input check passed: {input_description} contains the expected value.")
            return True
        else:
            print(f"Input check failed: {input_description} does not contain the expected value. Found: {current_value}")
            return False

    
    @handle_element_errors
    async def confirm_navigation(self, page: Page, page_name: str, outcomes: Dict[str, List[str]], timeout: int = 10000):
        """
        Confirms navigation by checking a dictionary of URLs and their associated XPath selectors.
        
        Args:
            page (Page): The Playwright page object on which actions are performed.
            page_name (str): Descriptive name for the page, used for logging.
            outcomes (Dict[str, List[str]]): Dictionary where keys are URLs and values are lists of XPath selectors associated with those URLs.
            timeout (int): Timeout in milliseconds for each check.
        
        Returns:
            tuple: (bool, dict) where bool indicates if navigation was successful, and dict provides details of the navigation result.
        """
        result = {
            'url_confirmed': None,
            'element_confirmed': None
        }
        current_url = page.url

        for url, selectors in outcomes.items():
            if url in current_url:
                result['url_confirmed'] = url
                for selector in selectors:
                    try:
                        await page.wait_for_selector(f'xpath={selector}', state="attached", timeout=timeout)
                        result['element_confirmed'] = selector
                        return True, result
                    except TimeoutError:
                        continue
                break

        logging.error(f"Failed to confirm navigation for {page_name}. Current URL: {current_url}")
        return False, result

    async def handle_additional_checks(self, page: Page):
        """
        Placeholder for additional checks, such as bot detection handling.
        """
        # Implementation of additional security or bot detection measures.
        logging.info("Implement additional checks here.")
    
    async def perform_steps(self, page: Page, steps):
        """
        Performs a sequence of specified actions and checks on a given page.

        Args:
            page (Page): Playwright page object where actions are performed.
            steps (list): Each item in the list defines an action or a check.
        """
        for step in steps:
            action_type = step['type']
            params = step['params']
            action_func = self.action_registry.get(action_type)

            if not action_func:
                print(f"Action type '{action_type}' is not supported.")
                continue

            # Execute the function corresponding to the action type
            result = await action_func(page, **params)

            # Handle the result based on the action type
            if action_type == 'confirm_navigation' and not result['url_confirmed']:
                print(f"Failed to confirm navigation to: {params['page_name']}")
                return False
            elif action_type in ['hover_and_click', 'check_input_value'] and not result:
                print(f"Action '{action_type}' failed at step with description: {params.get('description', 'No description provided')}")
                return False

            print(f"Action '{action_type}' successful.")
            await asyncio.sleep(random.uniform(1, 2))  # Random short pause for realism

        return True

    async def human_type(self, page, xpath, element_description: str, text, min_delay=0.05, max_delay=0.15):
        target_x, target_y = await self.get_target_coordinates(page, xpath)

        # Move mouse to the element and click to focus
        if self.mouse_tracker['x'] is not None and self.mouse_tracker['y'] is not None:
            await self.smooth_mouse_move(page, self.mouse_tracker['x'], self.mouse_tracker['y'], target_x, target_y)
        else:
            await page.mouse.move(target_x, target_y)

        await page.mouse.click(target_x, target_y)  # Click to focus the input field
        self.mouse_tracker['x'], self.mouse_tracker['y'] = target_x, target_y  # Update the mouse position tracker
        await self.random_wait('short')
        for char in text:
            # Simulate pressing the key
            await page.keyboard.down(char)
            # Wait for a human-like delay before releasing the key
            await asyncio.sleep(random.uniform(min_delay, max_delay))
            # Simulate releasing the key
            await page.keyboard.up(char)
            # Wait for a human-like delay before the next key press
            await asyncio.sleep(random.uniform(min_delay, max_delay))

        print(f"Finished typing '{text}' into {element_description} with human-like delays.")

    async def handle_additional_checks(self, page: Page):
        """
        Placeholder function for handling unexpected page conditions such as bot detection or other security measures.
        """
        # Placeholder for additional checks
        # Example: await page.wait_for_selector("selector_for_bot_check", timeout=500)
        logging.info("Additional check needed here! Implement detection and handling for bot security measures.")