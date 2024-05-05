import asyncio
import random
from typing import Optional, Callable, Any
from playwright.async_api import Page, TimeoutError, ElementHandleError

def handle_element_errors(func: Callable) -> Callable:
    """Decorator to handle element-related errors with dynamic messages."""
    async def wrapper(page: Page, xpath: str, element_description: str, *args, **kwargs) -> Any:
        try:
            return await func(page, xpath, *args, **kwargs)
        except TimeoutError as e:
            print(f"Timeout error while interacting with {element_description}: {e}")
        except ElementHandleError as e:
            print(f"Handle error while interacting with {element_description}: {e}")
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
async def hover_and_click(page: Page, xpath: str, element_description: str, hover_pause_type: Optional[str] = None, click_pause_type: Optional[str] = None):
    """Random wait, hover over an element, random wait, then click it, with dynamic error messages."""
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
