import json
import asyncio
from tasks.browser_manager import BrowserManager
from playwright.async_api import async_playwright
from .login import IndeedLogin
from .jobsearch import IndeedJobSearch

class IndeedTask:
    def __init__(self, task_config):
        self.task_config = task_config
        self.browser_manager = BrowserManager(keep_open=True)

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
        job_search_input = self.task_config["job_search_input"]

        user_profiles = self.load_user_profiles()
        selected_user = next(profile for profile in user_profiles if profile["profile_name"] == selected_profile)

        login = IndeedLogin(username=selected_user["username"], password=selected_user["password"])
        context = await self.browser_manager.launch_browser()
        page = await context.new_page()
        login_success = await login.login(page)
        if login_success:
            print("Login successful, initiating job search.")
            job_search = IndeedJobSearch(page, self.task_config)
            try:
                search_successful = await job_search.initiate_job_search()
            except Exception as e:
                    print(f"Error on trying to initiate job search: ", e)
            if search_successful:
                print("Job search initiated successfully.")
                await asyncio.sleep(1500)  # For demonstration purposes
            
            else:
                print("Failed to initiate job search.")
        else:
            print("Login failed, not proceeding with job search.")


        print(f"Selected location: {selected_location}")
        print(f"Job search input: {job_search_input}")


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
                },
                {
                    "key": "job_search_input",
                    "label": "Job Search Input",
                    "type": "line_edit"
                }
            ]
        }