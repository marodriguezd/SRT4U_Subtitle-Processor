# main.py
from application.gui import SubtitleProcessorGUI
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    processor = SubtitleProcessorGUI()
    processor.show()
    sys.exit(app.exec())