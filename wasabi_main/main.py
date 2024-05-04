# main.py
import multiprocessing
from gui.main_window import run_gui

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    gui_process = multiprocessing.Process(target=run_gui)
    gui_process.start()
    gui_process.join()
