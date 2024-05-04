from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QWidget
from .task_widget import TaskChooserDialog, TaskConfigDialog
import sys


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
        add_task_button.clicked.connect(self.open_task_chooser_dialog)
        layout.addWidget(add_task_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.task_counter = 0

    def open_task_chooser_dialog(self):
        task_chooser_dialog = TaskChooserDialog(self)
        if task_chooser_dialog.exec_() == QDialog.Accepted:
            selected_task_class = task_chooser_dialog.selected_task_class
            self.open_task_config_dialog(selected_task_class)

    def open_task_config_dialog(self, task_class):
        task_config_dialog = TaskConfigDialog(task_class, self)
        if task_config_dialog.exec_() == QDialog.Accepted:
            self.task_table.insertRow(self.task_counter)
            self.task_table.setItem(self.task_counter, 0, QTableWidgetItem(str(self.task_counter)))
            self.task_table.setItem(self.task_counter, 1, QTableWidgetItem(task_class.__name__))
            self.task_table.setItem(self.task_counter, 2, QTableWidgetItem("Running"))
            self.task_counter += 1

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
