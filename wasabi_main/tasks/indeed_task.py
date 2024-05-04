from .base_task import BaseTask

class IndeedTask(BaseTask):
    def __init__(self, task_config):
        super().__init__(task_config)

    async def run(self):
        await super().run()