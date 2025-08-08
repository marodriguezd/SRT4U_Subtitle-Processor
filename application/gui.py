# application/gui.py
import os
import sys
from queue import Queue
from threading import Thread
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QPushButton, QFileDialog, QCheckBox, 
                             QLineEdit, QComboBox, QProgressBar, QTextEdit,
                             QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QIcon

from .services.file_service import FileService
from .services.subtitle_service import SubtitleService
from .services.translation_service import TranslationService


class ProgressSignal(QObject):
    """Signal emitter for progress updates from worker thread"""
    progress_updated = pyqtSignal(str, object)


class SubtitleProcessorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file_path: Optional[str] = None
        self.output_directory: Optional[str] = None
        self.output_format: str = 'srt'
        self.file_service = FileService()
        self.subtitle_service = SubtitleService()
        self.translation_service = TranslationService()
        self.progress_queue = Queue()
        self.timer = QTimer()
        self.progress_signal = ProgressSignal()
        
        # Connect signals
        self.progress_signal.progress_updated.connect(self.handle_progress_update)
        self.timer.timeout.connect(self.check_progress_queue)
        
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle('SRT4U - Subtitle Processor')
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(500, 450)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Add some padding
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel('SRT4U - Subtitle Processor')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        description_label = QLabel('Translate and clean subtitles while preserving original timing')
        description_label.setStyleSheet("color: #AAA; font-size: 11px;")
        main_layout.addWidget(description_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # File selection section
        file_layout = QVBoxLayout()
        self.select_file_button = QPushButton('Select SRT/VTT file')
        self.select_file_button.clicked.connect(self.handle_file_selection)
        file_layout.addWidget(self.select_file_button)
        
        self.file_status = QLabel('No file selected')
        self.file_status.setStyleSheet("color: #AAA; font-size: 11px;")
        file_layout.addWidget(self.file_status)
        
        main_layout.addLayout(file_layout)
        
        # Output directory section
        dir_layout = QVBoxLayout()
        self.select_dir_button = QPushButton('Select output directory')
        self.select_dir_button.clicked.connect(self.select_output_directory)
        dir_layout.addWidget(self.select_dir_button)
        
        self.directory_status = QLabel('No directory selected')
        self.directory_status.setStyleSheet("color: #AAA; font-size: 11px;")
        dir_layout.addWidget(self.directory_status)
        
        main_layout.addLayout(dir_layout)
        
        # Translation section
        translation_layout = QVBoxLayout()
        
        self.translation_toggle = QCheckBox('Enable translation')
        translation_layout.addWidget(self.translation_toggle)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel('Target language:'))
        self.target_language = QLineEdit()
        self.target_language.setPlaceholderText('es, en, fr, etc.')
        lang_layout.addWidget(self.target_language)
        translation_layout.addLayout(lang_layout)
        
        main_layout.addLayout(translation_layout)
        
        # Output format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Output format:'))
        self.format_selector = QComboBox()
        self.format_selector.addItems(['srt', 'vtt'])
        self.format_selector.currentTextChanged.connect(self.update_output_format)
        format_layout.addWidget(self.format_selector)
        format_layout.addStretch()
        main_layout.addLayout(format_layout)
        
        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.processing_status = QLabel('')
        self.processing_status.setStyleSheet("color: #AAA; font-size: 11px;")
        main_layout.addWidget(self.processing_status)
        
        # Process button
        self.process_button = QPushButton('Process')
        self.process_button.setMinimumHeight(40)
        self.process_button.clicked.connect(self.process_subtitle_file)
        main_layout.addWidget(self.process_button)
        
        # Result status
        self.result_status = QLabel('')
        self.result_status.setStyleSheet("font-size: 11px;")
        self.result_status.setWordWrap(True)
        main_layout.addWidget(self.result_status)
        
        # Add stretch to push everything up
        main_layout.addStretch()

    def handle_file_selection(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select SRT/VTT file',
            '',
            'Subtitle files (*.srt *.vtt);;All files (*.*)'
        )
        
        if file_path:
            self.input_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_status.setText(f'File selected: {filename}')
            self.show_notification('File selected successfully', 'positive')
        else:
            self.file_status.setText('No file selected')

    def select_output_directory(self):
        self.directory_status.setText('Selecting directory...')
        try:
            directory = QFileDialog.getExistingDirectory(
                self,
                'Select output directory',
                ''
            )
            
            if directory:
                self.output_directory = directory
                self.directory_status.setText(f'Output directory: {directory}')
                self.show_notification('Directory selected', 'positive')
            else:
                self.directory_status.setText('No directory selected')
                
        except Exception as error:
            self.directory_status.setText('No directory selected')
            self.show_notification(f'Directory selection error: {str(error)}', 'negative')

    def update_output_format(self, value):
        self.output_format = value

    def process_subtitle_file(self):
        if not self._validate_inputs():
            return

        try:
            self._prepare_processing()
            
            processing_thread = Thread(
                target=self._run_processing,
                args=(self.progress_queue,)
            )
            processing_thread.start()
            
            # Start timer to check progress
            self.timer.start(100)  # Check every 100ms

        except Exception as error:
            self._handle_error(error)

    def _validate_inputs(self) -> bool:
        if not self.input_file_path:
            self.show_notification('Please select a file', 'warning')
            return False
        if not self.output_directory:
            self.show_notification('Please select output directory', 'warning')
            return False
        if self.translation_toggle.isChecked() and not self.target_language.text().strip():
            self.show_notification('Please enter target language', 'warning')
            return False
        return True

    def _prepare_processing(self):
        self.process_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.processing_status.setText('Starting process...')
        self.result_status.setText('')

    def _run_processing(self, queue: Queue):
        try:
            processed_text = self.subtitle_service.process_subtitles(
                self.input_file_path,
                self.translation_toggle.isChecked(),
                self.target_language.text().strip() if self.translation_toggle.isChecked() else None,
                lambda t, d: queue.put((t, d))
            )
            queue.put(('success', processed_text))
        except Exception as error:
            queue.put(('error', str(error)))

    def check_progress_queue(self):
        """Check for progress updates from worker thread"""
        try:
            while True:
                msg_type, data = self.progress_queue.get_nowait()
                self.progress_signal.progress_updated.emit(msg_type, data)
        except:
            pass  # Queue is empty

    def handle_progress_update(self, msg_type: str, data):
        """Handle progress updates in main thread"""
        if msg_type == 'progress':
            progress_value = int(data * 100)
            self.progress_bar.setValue(progress_value)
        elif msg_type == 'status':
            self.processing_status.setText(f'Processing: {data}')
        elif msg_type == 'info':
            self.processing_status.setText(data)
        elif msg_type == 'success':
            self.timer.stop()
            self._handle_success(data)
        elif msg_type == 'error':
            self.timer.stop()
            self._handle_error(Exception(data))

    def _save_processed_file(self, content: str) -> str:
        base_name = os.path.basename(self.input_file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_filename = f"{name_without_ext}_processed.{self.output_format}"
        output_path = os.path.join(self.output_directory, output_filename)

        # Add headline if the format is vtt
        if self.output_format == "vtt":
            content = f"WEBVTT\n\n{content}"

        with open(output_path, "w", encoding='UTF-8') as file:
            file.write(content)

        return output_path

    def _handle_success(self, processed_text: str):
        try:
            output_path = self._save_processed_file(processed_text)
            self.processing_status.setText('Process completed')
            self.show_notification('File processed successfully', 'positive')
            self.result_status.setText(f'File saved to: {output_path}')
            self.result_status.setStyleSheet("color: #2E7D32; font-size: 11px;")
        except Exception as error:
            self._handle_error(error)
        finally:
            self._cleanup()

    def _handle_error(self, error: Exception):
        self.processing_status.setText('Processing failed')
        self.show_notification(f'Processing error: {str(error)}', 'negative')
        self.result_status.setText(f'Error: {str(error)}')
        self.result_status.setStyleSheet("color: #D32F2F; font-size: 11px;")
        self._cleanup()

    def _cleanup(self):
        QTimer.singleShot(2000, self._reset_ui)  # Reset UI after 2 seconds

    def _reset_ui(self):
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.processing_status.text() == 'Process completed':
            self.processing_status.setText('')

    def show_notification(self, message: str, notification_type: str):
        """Show notification using QMessageBox"""
        msg = QMessageBox()
        
        if notification_type == 'positive':
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('Success')
        elif notification_type == 'negative':
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle('Error')
        elif notification_type == 'warning':
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle('Warning')
        else:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('Information')
            
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()