# main.py
from src.application.gui import SubtitleProcessorGUI

if __name__ == '__main__':
    processor = SubtitleProcessorGUI()
    processor.run(reload=False, port=12537)