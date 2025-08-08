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
        
        progress_callback('info', "Reading and parsing file...")

        processed_content = self._clean_content(content)
        subtitle_blocks = self._extract_blocks(processed_content, progress_callback)
        
        if not subtitle_blocks:
             progress_callback('error', "Could not find any valid subtitle blocks in the file.")
             return ""
        
        progress_callback('info', f"Total subtitles found: {len(subtitle_blocks)}")

        if translate:
            subtitle_blocks = self._translate_blocks(subtitle_blocks, target_language, progress_callback)

        subtitle_blocks = self._optimize_blocks(subtitle_blocks, progress_callback)
        return self._format_output(subtitle_blocks, progress_callback)

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding='UTF-8') as file:
            return file.read()

    def _clean_content(self, content: str) -> str:
        cleaned = content
        for pattern in self.spam_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def _extract_blocks(self, content: str, progress_callback: Callable) -> List[List[str]]:
        parsed_blocks = []
        # Primero, eliminar la cabecera VTT si existe, para no interferir con el parseo
        if content.strip().startswith('WEBVTT'):
            content = re.sub(r'WEBVTT.*?\n\s*\n', '', content, 1, flags=re.DOTALL | re.IGNORECASE)

        raw_blocks = re.split(r'\n\s*\n', content.strip())
        
        for raw_block in raw_blocks:
            lines = [line.strip() for line in raw_block.split('\n') if line.strip()]
            if not lines:
                continue

            # Un bloque válido necesita al menos una línea de tiempo y una de texto.
            if len(lines) >= 2:
                if lines[0].isdigit():
                    parsed_blocks.append(lines)
                # Asumimos que si no es un dígito, es la línea de tiempo.
                elif '-->' in lines[0] or ' - ' in lines[0]:
                    new_block = [str(len(parsed_blocks) + 1)] + lines
                    parsed_blocks.append(new_block)
            
        return parsed_blocks

    def _translate_blocks(self, blocks: List[List[str]], target_language: str,
                          progress_callback: Callable) -> List[List[str]]:
        translated_blocks = []
        total_blocks = len(blocks)
        progress_callback('status', 'Translating subtitles...')

        for i, block in enumerate(blocks):
            if len(block) < 3:
                translated_blocks.append(block)
                continue

            original_text = "\n".join(block[2:])
            if not original_text.strip():
                translated_blocks.append(block)
                continue

            try:
                translated_text = self.translation_service.translate_text(original_text, target_language)
                translated_lines = translated_text.split("\n")
                new_block = [block[0], block[1]] + translated_lines
                translated_blocks.append(new_block)
            except Exception as e:
                error_message = f"Failed to translate block #{block[0]} (time: {block[1]}): {e}"
                progress_callback('error', error_message)
                raise RuntimeError(error_message)

            progress = (i + 1) / total_blocks * 0.8
            progress_callback('progress', progress)
        return translated_blocks


    def _optimize_blocks(self, blocks: List[List[str]], progress_callback: Callable) -> List[List[str]]:
        optimized = []
        current_index = 1

        for i, block in enumerate(blocks):
            if len(block) < 2:
                continue
            
            # --- LA CORRECCIÓN ESTÁ AQUÍ ---
            # Hacemos la comprobación más flexible para aceptar "-->" o "-"
            timestamp_line = block[1]
            if "-->" not in timestamp_line and "-" not in timestamp_line:
                continue
            # --- FIN DE LA CORRECCIÓN ---

            # Asegurarse de que el bloque tiene texto antes de procesarlo
            if len(block) < 3:
                continue
                
            block[0] = str(current_index)
            
            # Reemplazar el separador no estándar por el estándar SRT
            timestamp_line = re.sub(r'\s+-\s+', ' --> ', timestamp_line)
            block[1] = timestamp_line

            if optimized:
                previous_block = optimized[-1]
                if len(previous_block) > 1 and "-->" in previous_block[1]:
                    previous_parts = previous_block[1].split('-->')
                    previous_end_time = previous_parts[1].strip() if len(previous_parts) >= 2 else None
                else:
                    previous_end_time = None

                if previous_end_time:
                    current_parts = block[1].split('-->')
                    current_start_time = current_parts[0].strip() if len(current_parts) >= 2 else None
                    if current_start_time and previous_end_time != current_start_time:
                        block[1] = f"{previous_end_time} --> {current_parts[1].strip()}"
            
            optimized.append(block)
            current_index += 1

        return optimized

    def _format_output(self, blocks: List[List[str]], progress_callback: Callable) -> str:
        formatted_content = []
        total_blocks = len(blocks)
        if total_blocks == 0:
            return ""
            
        for i, block in enumerate(blocks):
            formatted_content.extend(block)
            formatted_content.append('')
            progress = 0.8 + (i + 1) / total_blocks * 0.2
            progress_callback('progress', progress)
        return '\n'.join(formatted_content)