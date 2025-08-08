# application/services/subtitle_service.py
import re
from typing import Optional, Callable, List
from .translation_service import TranslationService


class SubtitleService:
    def __init__(self, batch_size: int = 50):
        self.translation_service = TranslationService()
        self.spam_patterns = [
            r"Subtitled by",
            r'-♪.*?♪-',
            r"We compress knowledge for you!",
            r"https://t.me/.*?",
            r"Subtitled\s*by",
            r"https?://[^\s]+",
            r"♪",
            r"We\s*compress\s*knowledge\s*for\s*you!",
            r"online|courses|club",
            r"<font.*?>.*?</font>",
            r"\bjoinchat\b",
            r".*?/[a-zA-Z0-9]{12}.*",  # Matches any line containing a Telegram ID
        ]
        self.batch_size = batch_size

    def process_subtitles(self, file_path: str, translate: bool, target_language: Optional[str],
                          progress_callback: Callable) -> str:
        content = self._read_file(file_path)
        total_subtitles = self._count_subtitles(content)
        progress_callback('info', f"Total subtitles: {total_subtitles}")

        processed_content = self._clean_content(content)
        subtitle_blocks = self._extract_blocks(processed_content, progress_callback)

        if translate:
            subtitle_blocks = self._translate_blocks(subtitle_blocks, target_language, progress_callback)

        subtitle_blocks = self._optimize_blocks(subtitle_blocks, progress_callback)
        return self._format_output(subtitle_blocks, progress_callback)

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding='UTF-8') as file:
            return file.read()

    def _count_subtitles(self, content: str) -> int:
        return len([line for line in content.split('\n') if line.strip().isdigit()])

    def _clean_content(self, content: str) -> str:
        cleaned = content
        for pattern in self.spam_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def _extract_blocks(self, content: str, progress_callback: Callable) -> List[List[str]]:
        blocks = []
        current_block = []
        for line in content.split('\n'):
            line = line.strip()
            if line.isdigit() and current_block:
                blocks.append(current_block)
                current_block = [line]
            elif line:
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        return blocks

    def _translate_blocks(self, blocks: List[List[str]], target_language: str,
                          progress_callback: Callable) -> List[List[str]]:
        translated_blocks = []
        current_batch_texts = []
        current_batch_blocks = []  # Almacena el bloque original para reensamblarlo
        current_length = 0
        max_length = 5000  # Límite de caracteres por solicitud a la API
        total_blocks = len(blocks)
        processed_blocks = 0

        for block in blocks:
            if len(block) < 3:
                # Si el bloque no tiene línea de texto, lo dejamos intacto
                translated_blocks.append(block)
                processed_blocks += 1
                continue

            # Solo traducimos la parte textual (a partir de la tercera línea)
            block_text = "\n".join(block[2:])
            additional_length = len(block_text) + 2  # +2 para los separadores "\n\n"
            if current_length + additional_length <= max_length:
                current_batch_texts.append(block_text)
                current_batch_blocks.append(block)
                current_length += additional_length
            else:
                # Traducimos el batch acumulado
                batch_text = "\n\n".join(current_batch_texts)
                try:
                    translated_text = self.translation_service.translate_text(batch_text, target_language)
                    translated_batch = translated_text.split("\n\n")
                    for orig_block, translated in zip(current_batch_blocks, translated_batch):
                        translated_lines = translated.split("\n")
                        new_block = [orig_block[0], orig_block[1]] + translated_lines
                        translated_blocks.append(new_block)
                except Exception as error:
                    progress_callback('error', f"Translation error: {str(error)}")
                    translated_blocks.extend(current_batch_blocks)
                processed_blocks += len(current_batch_blocks)
                progress_callback('progress', processed_blocks / total_blocks * 0.5)
                # Reiniciamos el batch y añadimos el bloque actual
                current_batch_texts = [block_text]
                current_batch_blocks = [block]
                current_length = additional_length

        # Procesamos el último batch
        if current_batch_texts:
            batch_text = "\n\n".join(current_batch_texts)
            try:
                translated_text = self.translation_service.translate_text(batch_text, target_language)
                translated_batch = translated_text.split("\n\n")
                for orig_block, translated in zip(current_batch_blocks, translated_batch):
                    translated_lines = translated.split("\n")
                    new_block = [orig_block[0], orig_block[1]] + translated_lines
                    translated_blocks.append(new_block)
            except Exception as error:
                progress_callback('error', f"Translation error: {str(error)}")
                translated_blocks.extend(current_batch_blocks)
            processed_blocks += len(current_batch_blocks)
            progress_callback('progress', processed_blocks / total_blocks * 0.5)

        return translated_blocks

    def _optimize_blocks(self, blocks: List[List[str]], progress_callback: Callable) -> List[List[str]]:
        optimized = []
        current_index = 1

        for i, block in enumerate(blocks):
            # Verifica que el bloque tenga al menos la numeración, la línea de tiempo y alguna línea de texto.
            if len(block) < 3:
                continue
            # Verifica que la línea de tiempo contenga el separador esperado.
            if " --> " not in block[1]:
                continue

            block[0] = str(current_index)

            if optimized:
                previous_block = optimized[-1]
                if len(previous_block) > 1 and " --> " in previous_block[1]:
                    previous_parts = previous_block[1].split(' --> ')
                    if len(previous_parts) >= 2:
                        previous_end_time = previous_parts[1]
                    else:
                        previous_end_time = None
                else:
                    previous_end_time = None

                if previous_end_time and " --> " in block[1]:
                    current_parts = block[1].split(' --> ')
                    if len(current_parts) >= 2:
                        current_start_time = current_parts[0]
                        if previous_end_time != current_start_time:
                            block[1] = f"{previous_end_time} --> {current_parts[1]}"
            optimized.append(block)
            current_index += 1

        return optimized

    def _format_output(self, blocks: List[List[str]], progress_callback: Callable) -> str:
        formatted_content = []
        for i, block in enumerate(blocks):
            formatted_content.extend(block)
            formatted_content.append('')
            progress = 0.8 + (i + 1) / len(blocks) * 0.2
            progress_callback('progress', progress)
        return '\n'.join(formatted_content)