from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, QThread
from tasks.linkedin_task import LinkedInTask
from tasks.indeed_task import IndeedTask
import sys
import asyncio


class TaskThread(QThread):
    task_complete = pyqtSignal(int)

    def __init__(self, task, task_id):
        super().__init__()
        self.task = task
        self.task_id = task_id

    def run(self):
        asyncio.run(self.task.run())
        self.task_complete.emit(self.task_id)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Task Manager')
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.task_table = QTableWidget(0, 3)
        self.task_table.setHorizontalHeaderLabels(['Task ID', 'Task Type', 'Status'])
        layout.addWidget(self.task_table)

        add_task_button = QPushButton('Add Task')
        add_task_button.clicked.connect(self.add_task)
        layout.addWidget(add_task_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.task_threads = {}
        self.task_counter = 0

    def add_task(self):
        task_id = self.task_counter
        task_type = 'LinkedIn' if self.task_counter % 2 == 0 else 'Indeed'
        url = 'https://www.linkedin.com' if task_type == 'LinkedIn' else 'https://www.indeed.com'
        task_config = {"url": url}

        if task_type == 'LinkedIn':
            task = LinkedInTask(task_config)
        else:
            task = IndeedTask(task_config)

        task_thread = TaskThread(task, task_id)
        task_thread.task_complete.connect(self.task_complete)

        self.task_table.insertRow(task_id)
        self.task_table.setItem(task_id, 0, QTableWidgetItem(str(task_id)))
        self.task_table.setItem(task_id, 1, QTableWidgetItem(task_type))
        self.task_table.setItem(task_id, 2, QTableWidgetItem("Running"))

        self.task_threads[task_id] = task_thread
        task_thread.start()

        self.task_counter += 1

    def task_complete(self, task_id):
        self.task_table.setItem(task_id, 2, QTableWidgetItem("Complete"))


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
