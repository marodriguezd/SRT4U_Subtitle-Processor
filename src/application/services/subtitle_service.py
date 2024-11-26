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
            r"/[a-zA-Z0-9]{12}",  # Matches Telegram IDs like /ailxpXoW3JVjYzQ1
            r"(?:^|\s)[A-Z][a-zA-Z0-9]{3,}Q[0-9](?:\s|$)",  # Matches ID fragments like YzQ1 more specifically
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
        total_batches = (len(blocks) + self.batch_size - 1) // self.batch_size

        for batch_index in range(total_batches):
            start = batch_index * self.batch_size
            end = min(start + self.batch_size, len(blocks))
            batch = blocks[start:end]
            batch_text = "\n\n".join("\n".join(block) for block in batch)

            try:
                translated_text = self.translation_service.translate_text(batch_text, target_language)
                translated_batch = translated_text.split("\n\n")
                translated_blocks.extend([translated_block.split('\n') for translated_block in translated_batch])
                progress = (batch_index + 1) / total_batches * 0.5
                progress_callback('progress', progress)
            except Exception as error:
                progress_callback('error', f"Translation error: {str(error)}")
                translated_blocks.extend(batch)

        return translated_blocks

    def _optimize_blocks(self, blocks: List[List[str]], progress_callback: Callable) -> List[List[str]]:
        optimized = []
        for i, block in enumerate(blocks):
            if len(block) >= 3:
                optimized.append(block)
            progress = 0.5 + (i + 1) / len(blocks) * 0.3
            progress_callback('progress', progress)
        return optimized

    def _format_output(self, blocks: List[List[str]], progress_callback: Callable) -> str:
        formatted_content = []
        for i, block in enumerate(blocks):
            formatted_content.extend(block)
            formatted_content.append('')
            progress = 0.8 + (i + 1) / len(blocks) * 0.2
            progress_callback('progress', progress)
        return '\n'.join(formatted_content)
