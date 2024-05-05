import asyncio
import random
from typing import Optional, Callable, Any
from playwright.async_api import Page, TimeoutError
from functools import wraps

def handle_element_errors(func):
    """Decorator to handle errors for actions performed on page elements, capturing all arguments flexibly."""
    @wraps(func)  # Use wraps to preserve metadata like the function's name and docstring
    async def wrapper(*args, **kwargs):
        # Attempt to extract element_description intelligently based on args or kwargs
        element_description = kwargs.get('element_description', args[2] if len(args) > 2 else 'Unknown element')
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            print(f"Timeout error while interacting with {element_description}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while interacting with {element_description}: {e}")
    return wrapper

def random_pause_type() -> str:
    """Randomly select a pause type: 'short', 'medium', or 'long'."""
    return random.choice(["short", "medium", "long"])

def random_wait_duration(pause_type: str) -> float:
    """Return a random wait duration based on the specified pause type."""
    pause_durations = {
        "short": (0.5, 1.5),
        "medium": (3, 8),
        "long": (5, 10)
    }
    min_time, max_time = pause_durations[pause_type]
    return random.uniform(min_time, max_time)

async def random_wait(pause_type: Optional[str] = None):
    """Wait for a random amount of time based on the specified or random pause type."""
    if pause_type is None:
        pause_type = random_pause_type()
    wait_time = random_wait_duration(pause_type)
    await asyncio.sleep(wait_time)

@handle_element_errors
async def hover_and_click(page: Page, xpath: str, element_description: str, 
                          hover_pause_type: Optional[str] = None, 
                          click_pause_type: Optional[str] = None):
    """
    Perform a hover and click action on a specified element, with optional random waits before each action.

    Args:
        page (Page): The Playwright page object where actions will be performed.
        xpath (str): The XPath of the element to interact with.
        element_description (str): A brief description of the element for enhanced error messages.
        hover_pause_type (Optional[str], optional): The type of pause before the hover action. Accepts 'short', 'medium', or 'long'. If None, a random pause type is chosen.
        click_pause_type (Optional[str], optional): The type of pause before the click action. Similar to hover_pause_type. If None, a random pause type is chosen.

    This function first performs a hover action on the specified element, optionally waiting for a randomized time 
    before hovering. After hovering, the function waits again (optionally with a specified pause duration) and then 
    performs a click action. Both actions incorporate dynamic error handling to catch and report any issues related 
    to element interaction, enhancing debugging and reliability of the automation script.

    Example usage:
        await hover_and_click(page, "//button[@id='submit']", "Submit Button", "short", "medium")

    Raises:
        TimeoutError: If the element is not found within the specified time or the page times out.
        ElementHandleError: If there are issues with the element handle, such as the element not being interactable.
        Exception: For any other unforeseen issues that may occur during the hover or click actions.
    """

    # Random wait before hovering
    await random_wait(hover_pause_type)

    # Hover over the element
    await page.hover(xpath)

    # Random wait after hovering and before clicking
    await random_wait(click_pause_type)

    # Click the element
    await page.click(xpath)

    # Random wait after clicking
    await random_wait(click_pause_type)

    # Debugger Print Statement
    print(f"Successfully hover and clicked on {element_description}, using click pause type: {click_pause_type} and hover pause type:{hover_pause_type}.")
