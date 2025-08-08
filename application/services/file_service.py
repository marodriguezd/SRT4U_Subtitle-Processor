# application/services/file_service.py
import os
import shutil
import tempfile
from typing import Any


class FileService:
    def __init__(self):
        self.temp_directory = self._create_temp_directory()

    def _create_temp_directory(self) -> str:
        temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def save_uploaded_file(self, upload_event: Any) -> str:
        """This method is not used in PyQt version but kept for compatibility"""
        temp_path = os.path.join(self.temp_directory, upload_event.name)
        with open(temp_path, 'wb') as file:
            shutil.copyfileobj(upload_event.content, file)
        return temp_path

    def get_output_directory(self) -> str:
        """This method is not used in PyQt version but kept for compatibility"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.attributes('-topmost', True)
        root.focus_force()

        selected_dir = filedialog.askdirectory()
        root.destroy()

        if not selected_dir:
            raise ValueError('No directory selected')

        return selected_dir