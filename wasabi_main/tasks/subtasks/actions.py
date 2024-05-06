import asyncio
import random
import logging
from typing import Optional, Callable, Any
from playwright.async_api import Page, TimeoutError
from functools import wraps

logging.basicConfig(level=logging.INFO)

class GlobalActionTask:
    def __init__(self):
        # Dictionary to store mosue coordinates/position
        self.mouse_tracker = {'x': None, 'y': None}

    def handle_element_errors(func):
        """Decorator to handle errors for actions performed on page elements, capturing all arguments flexibly."""
        @wraps(func)  # Use wraps to preserve metadata like the function's name and docstring
        async def wrapper(self, *args, **kwargs):
            # Extract element_description intelligently based on args or kwargs
            element_description = kwargs.get('element_description', args[1] if len(args) > 1 else 'Unknown element')
            try:
                return await func(self, *args, **kwargs)
            except TimeoutError as e:
                logging.error(f"Timeout error while interacting with {element_description}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while interacting with {element_description}: {e}")
        return wrapper

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
    async def confirm_navigation(self, page: Page, page_name: str, expected_url_contains: Optional[str] = None, 
                                xpath_selector: Optional[str] = None, timeout: int = 10000):
        """
        Confirms that the current page's URL contains a specified substring or that a specific element is present using XPath.
        This function is designed to ensure that navigation has reached the correct destination and can handle dynamic URL structures.

        Args:
            page (Page): The Playwright page object on which actions are performed.
            page_name (str): A descriptive name for the page, used for logging and error messages.
            expected_url_contains (Optional[str]): A substring that should be present in the current page's URL. This parameter 
                                                is useful for situations where the exact URL is not known ahead of time or can vary.
            xpath_selector (Optional[str]): An XPath selector specifying an element that should be present on the page. This is used
                                            to confirm that the expected content has loaded.
            timeout (int): The maximum time, in milliseconds, to wait for the URL or element to be confirmed.

        Raises:
            TimeoutError: If the URL does not contain the expected substring or the element does not appear within the specified timeout.
            ValueError: If neither `expected_url_contains` nor `xpath_selector` is provided, indicating that there are no criteria specified for confirmation.

        Returns:
            bool: True if the navigation is confirmed by either URL or element presence, False otherwise.
        """
        try:
            if expected_url_contains:
                # Wait until the URL contains the specified substring
                await page.wait_for_function(
                    f"window.location.href.includes('{expected_url_contains}')", timeout=timeout)
                current_url = page.url
                if expected_url_contains not in current_url:
                    raise TimeoutError(f"Expected URL part '{expected_url_contains}' not found in {current_url}")
                logging.info(f"Navigation to {page_name} confirmed, URL contains: {expected_url_contains}")

            if xpath_selector:
                await page.wait_for_selector(f'xpath={xpath_selector}', state="attached", timeout=timeout)
                logging.info(f"Element confirmed on {page_name} using XPath: {xpath_selector}")

        except TimeoutError as e:
            logging.error(f"Failed to confirm {page_name}. Error: {e}")
            # Optional: Handle additional checks for bot detection or other issues
            await self.handle_additional_checks(page)

        if not expected_url_contains and not xpath_selector:
            raise ValueError(f"Either expected_url_contains or xpath_selector must be provided for {page_name}.")

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