import json
import asyncio
from tasks.browser_manager import BrowserManager
from playwright.async_api import async_playwright
from .login import IndeedLogin

class IndeedTask:
    def __init__(self, task_config):
        self.task_config = task_config
        self.browser_manager = BrowserManager()

    @staticmethod
    def load_locations():
        with open(r"D:\code\WASABI\wasabi_main\tasks\indeed_task\locations.json", "r") as f:
            data = json.load(f)
            return data["locations"]    

    @staticmethod
    def load_user_profiles():
        with open(r"D:\code\WASABI\wasabi_main\tasks\indeed_task\user_profiles.json", "r") as f:
            data = json.load(f)
            return data["user_profiles"]

    async def run(self):
        selected_profile = self.task_config["selected_profile"]
        selected_location = self.task_config["selected_location"]

        user_profiles = self.load_user_profiles()
        selected_user = next(profile for profile in user_profiles if profile["profile_name"] == selected_profile)

        login = IndeedLogin(username=selected_user["username"], password=selected_user["password"])
        context = await self.browser_manager.launch_browser()
        page = await context.new_page()
        await login.login(page)

        print(f"Selected location: {selected_location}")

        # Implement other Indeed-specific tasks

        await self.browser_manager.close_browser()

    @staticmethod
    def configuration_spec():
        user_profiles = IndeedTask.load_user_profiles()
        profile_names = [profile["profile_name"] for profile in user_profiles]
        locations = IndeedTask.load_locations()

        return {
            "inputs": [
                {
                    "key": "selected_profile",
                    "label": "Select Profile",
                    "type": "dropdown",
                    "options": profile_names
                },
                {
                    "key": "selected_location",
                    "label": "Select Location",
                    "type": "dropdown",
                    "options": locations
                }
            ]
        }