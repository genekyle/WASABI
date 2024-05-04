from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QComboBox, QLabel, QDialogButtonBox, QLineEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import importlib
import os
import glob
import asyncio

class TaskChooserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_classes = self.get_task_classes()
        self.selected_task_class = None

        layout = QVBoxLayout()

        self.task_dropdown = QComboBox()
        self.task_dropdown.addItems(list(self.task_classes.keys()))
        layout.addWidget(QLabel("Choose a task:"))
        layout.addWidget(self.task_dropdown)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.submit_task)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_task_classes(self):
        task_classes = {}
        task_dirs = [d for d in os.listdir("tasks") if os.path.isdir(os.path.join("tasks", d))]

        for task_dir in task_dirs:
            # Look for the task file in each directory
            task_files = glob.glob(os.path.join("tasks", task_dir, "*_task.py"))
            for task_file in task_files:
                module_name = os.path.basename(task_file)[:-3]
                module_path = f"tasks.{task_dir}.{module_name}"
                module = importlib.import_module(module_path)
                class_name = ''.join([word.capitalize() for word in module_name.split('_')])
                task_classes[module_name] = getattr(module, class_name)
        
        return task_classes

    def submit_task(self):
        selected_task_name = self.task_dropdown.currentText()
        self.selected_task_class = self.task_classes[selected_task_name]
        self.accept()


class TaskThread(QThread):
    task_complete = pyqtSignal()

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        asyncio.run(self.task.run())
        self.task_complete.emit()


class TaskConfigDialog(QDialog):
    def __init__(self, task_class, parent=None):
        super().__init__(parent)
        self.task_class = task_class
        self.task_thread = None
        self.input_fields = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        spec = None
        if hasattr(self.task_class, "configuration_spec"):
            spec = self.task_class.configuration_spec()

        if spec:
            self.configure_inputs(layout, spec)

        self.submit_button = QPushButton("Go")
        self.submit_button.clicked.connect(self.start_task)
        layout.addWidget(self.submit_button)

    def configure_inputs(self, layout, spec):
        for input_spec in spec.get("inputs", []):
            input_type = input_spec.get("type", "line_edit")
            label = input_spec["label"]

            layout.addWidget(QLabel(label))

            if input_type == "line_edit":
                input_field = QLineEdit(self)
                layout.addWidget(input_field)
                self.input_fields[label] = input_field
            elif input_type == "dropdown":
                dropdown = QComboBox(self)
                dropdown.addItems(input_spec.get("options", []))
                layout.addWidget(dropdown)
                self.input_fields[label] = dropdown

    def start_task(self):
        config = {}
        for label, field in self.input_fields.items():
            if isinstance(field, QLineEdit):
                config[label] = field.text()
            elif isinstance(field, QComboBox):
                config[label] = field.currentText()

        task = self.task_class(config)
        self.task_thread = TaskThread(task)
        self.task_thread.task_complete.connect(self.task_complete)
        self.task_thread.start()

    def task_complete(self):
        print("Task Complete")
        self.accept()

