# application/gui.py
import asyncio
import os
from queue import Queue
from threading import Thread
from typing import Optional
from nicegui import ui

from .services.file_service import FileService
from .services.subtitle_service import SubtitleService
from .services.translation_service import TranslationService


class SubtitleProcessorGUI:
    def __init__(self):
        self.input_file_path: Optional[str] = None
        self.output_directory: Optional[str] = None
        self.output_format: str = 'srt'
        self.file_service = FileService()
        self.subtitle_service = SubtitleService()
        self.translation_service = TranslationService()
        self.setup_ui()

    def setup_ui(self):
        with ui.card().classes('w-full max-w-3xl mx-auto p-4'):
            ui.label('SRT4U - Subtitle Processor').classes('text-xl mb-4')
            ui.label('Translate and clean subtitles while preserving original timing').classes(
                'text-sm text-gray-600 mb-4')

            with ui.column().classes('w-full gap-2'):
                ui.upload(
                    label='Select SRT/VTT file',
                    max_files=1,
                    auto_upload=True,
                    on_upload=self.handle_file_upload
                ).props('accept=.srt,.vtt')
                self.file_status = ui.label('No file selected').classes('text-sm text-gray-600')

            with ui.column().classes('w-full gap-2 mt-4'):
                ui.button('Select output directory', on_click=self.select_output_directory).classes('w-fit')
                self.directory_status = ui.label('No directory selected').classes('text-sm text-gray-600')

            with ui.row().classes('w-full items-center mt-4'):
                self.translation_toggle = ui.checkbox('Enable translation')

            with ui.row().classes('w-full items-center mt-2'):
                self.target_language = ui.input(
                    label='Target language',
                    placeholder='es, en, fr, etc.'
                ).props('outlined dense')

            with ui.row().classes('w-full items-center mt-2'):
                ui.label('Output format: ').classes('mr-2')
                self.format_selector = ui.select(
                    options=['srt', 'vtt'],
                    value='srt',
                    on_change=self.update_output_format
                ).props('outlined dense')

            self.progress_bar = ui.linear_progress(value=0).classes('w-full mt-4')
            self.progress_bar.visible = False
            self.processing_status = ui.label('').classes('text-sm text-gray-600 mt-2')

            self.process_button = ui.button('Process', on_click=self.process_subtitle_file).classes('mt-4')
            self.result_status = ui.label('').classes('mt-4 text-sm')

    async def handle_file_upload(self, event):
        self.file_status.text = 'Uploading file...'
        try:
            self.input_file_path = self.file_service.save_uploaded_file(event)
            self.file_status.text = f'File selected: {event.name}'
            ui.notify('File uploaded successfully', type='positive')
        except Exception as error:
            self.file_status.text = 'Upload failed'
            ui.notify(f'Upload error: {str(error)}', type='negative')

    def select_output_directory(self):
        self.directory_status.text = 'Selecting directory...'
        try:
            self.output_directory = self.file_service.get_output_directory()
            self.directory_status.text = f'Output directory: {self.output_directory}'
            ui.notify('Directory selected', type='positive')
        except Exception as error:
            self.directory_status.text = 'No directory selected'
            ui.notify(f'Directory selection error: {str(error)}', type='negative')

    def update_output_format(self, event):
        self.output_format = event.value

    async def process_subtitle_file(self):
        if not self._validate_inputs():
            return

        try:
            self._prepare_processing()
            progress_queue = Queue()

            processing_thread = Thread(
                target=self._run_processing,
                args=(progress_queue,)
            )
            processing_thread.start()

            result_type, result_data = await self._monitor_progress(progress_queue)

            if result_type == 'error':
                raise Exception(result_data)

            output_path = self._save_processed_file(result_data)
            self._handle_success(output_path)

        except Exception as error:
            self._handle_error(error)
        finally:
            await self._cleanup()

    def _validate_inputs(self) -> bool:
        if not self.input_file_path:
            ui.notify('Please select a file', type='warning')
            return False
        if not self.output_directory:
            ui.notify('Please select output directory', type='warning')
            return False
        if self.translation_toggle.value and not self.target_language.value:
            ui.notify('Please enter target language', type='warning')
            return False
        return True

    def _prepare_processing(self):
        self.process_button.disable()
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.processing_status.text = 'Starting process...'

    def _run_processing(self, queue: Queue):
        try:
            processed_text = self.subtitle_service.process_subtitles(
                self.input_file_path,
                self.translation_toggle.value,
                self.target_language.value if self.translation_toggle.value else None,
                lambda t, d: queue.put((t, d))
            )
            queue.put(('success', processed_text))
        except Exception as error:
            queue.put(('error', str(error)))

    async def _monitor_progress(self, queue: Queue):
        while True:
            try:
                msg_type, data = queue.get_nowait()
                if msg_type == 'progress':
                    self.progress_bar.value = data
                elif msg_type == 'status':
                    self.processing_status.text = f'Processing: {data}'
                elif msg_type in ['success', 'error']:
                    return msg_type, data
            except:
                await asyncio.sleep(0.1)

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

    def _handle_success(self, output_path: str):
        self.processing_status.text = 'Process completed'
        ui.notify('File processed successfully', type='positive')
        self.result_status.text = f'File saved to: {output_path}'

    def _handle_error(self, error: Exception):
        self.processing_status.text = 'Processing failed'
        ui.notify(f'Processing error: {str(error)}', type='negative')
        self.result_status.text = f'Error: {str(error)}'

    async def _cleanup(self):
        await asyncio.sleep(2)
        self.process_button.enable()
        self.progress_bar.visible = False
        if self.processing_status.text == 'Process completed':
            self.processing_status.text = ''

    def run(self, *args, **kwargs):
        ui.run(*args, **kwargs)