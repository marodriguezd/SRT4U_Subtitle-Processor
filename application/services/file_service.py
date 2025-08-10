# application/services/file_service.py
"""
This module provides a service for handling file-related operations,
such as creating temporary directories and managing file dialogs.
"""
import os
import shutil
import tempfile
from typing import Any


class FileService:
    """
    A service class for managing file operations.
    """
    def __init__(self):
        """
        Initializes the FileService and creates a temporary directory for use by the application.
        """
        self.temp_directory = self._create_temp_directory()

    def _create_temp_directory(self) -> str:
        """
        Creates a dedicated temporary directory for the application.

        Returns:
            str: The absolute path to the created temporary directory.
        """
        temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def save_uploaded_file(self, upload_event: Any) -> str:
        """
        Saves an uploaded file to the temporary directory.
        Note: This method is kept for compatibility and is not used in the PyQt version.

        Args:
            upload_event (Any): An object representing the uploaded file, expected
                                to have 'name' and 'content' attributes.

        Returns:
            str: The path to the saved temporary file.
        """
        temp_path = os.path.join(self.temp_directory, upload_event.name)
        with open(temp_path, 'wb') as file:
            shutil.copyfileobj(upload_event.content, file)
        return temp_path

    def get_output_directory(self) -> str:
        """
        Opens a system dialog to ask the user to select a directory.
        Note: This method uses tkinter and is kept for compatibility, but the PyQt
        version uses QFileDialog instead.

        Returns:
            str: The path to the selected directory.

        Raises:
            ValueError: If no directory is selected by the user.
        """
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