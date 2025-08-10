# main.py
"""
This script is the main entry point for the SRT4U Subtitle Processor application.
It initializes the PyQt6 application and displays the main GUI.
"""
import sys
from PyQt6.QtWidgets import QApplication
from application.gui import SubtitleProcessorGUI

if __name__ == '__main__':
    """
    Main execution block.
    Initializes the QApplication, creates an instance of the SubtitleProcessorGUI,
    shows the GUI, and starts the application's event loop.
    """
    app = QApplication(sys.argv)
    processor = SubtitleProcessorGUI()
    processor.show()
    sys.exit(app.exec())