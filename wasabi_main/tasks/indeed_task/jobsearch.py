import asyncio, random
from playwright.async_api import Page
from tasks.subtasks.actions import GlobalActionTask
 
class IndeedJobSearch:
    def __init__(self, page, task_config):
        self.page = page
        self.task_config = task_config
        self.action_task = GlobalActionTask()  # Create an instance of GlobalActionTask

    async def initiate_job_search(self, page):
        job_searchbar_xpath = "//input[contains(@aria-label,'search: Job title, keywords, or company')]"
        job_search_text = self.task_config["job_search_input"]
        steps = [
            {
                'type': 'human_type',
                'params': {
                    'xpath': job_searchbar_xpath,
                    'element_description': "Job Serach Input",
                    'text': job_search_text
                }
            },
            {
                'type': 'check_input_value',
                'params': {
                    'expected_value': job_search_text,
                    'xpath': job_searchbar_xpath,
                    'input_description': "Job Search Input"
                }
            }
        ]

        await self.action_task.perform_steps(self.page, steps)
       