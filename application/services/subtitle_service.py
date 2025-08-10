# application/services/subtitle_service.py
import re
from typing import Optional, Callable, List
from .translation_service import TranslationService


class SubtitleService:
    """
    Service for processing subtitle files, including cleaning, translating,
    and optimizing subtitle blocks.
    """

    def __init__(self, batch_size: int = 50):
        """
        Initializes the SubtitleService.

        Args:
            batch_size (int): The number of subtitle blocks to process in a batch
                              for operations like translation.
        """
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
        """
        Main method to process a subtitle file. It reads, cleans, translates (optional),
        optimizes, and formats the subtitles.

        Args:
            file_path (str): The path to the subtitle file.
            translate (bool): Whether to translate the subtitles.
            target_language (Optional[str]): The target language for translation.
            progress_callback (Callable): A function to call for progress updates.

        Returns:
            str: The processed subtitle content as a single string.
        """
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
        """
        Reads the content of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The content of the file.
        """
        with open(file_path, "r", encoding='UTF-8') as file:
            return file.read()

    def _clean_content(self, content: str) -> str:
        """
        Removes spam and unwanted patterns from the subtitle content.

        Args:
            content (str): The original subtitle content.

        Returns:
            str: The cleaned content.
        """
        cleaned = content
        for pattern in self.spam_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def _extract_blocks(self, content: str, progress_callback: Callable) -> List[List[str]]:
        """
        Extracts subtitle blocks from the content.

        Args:
            content (str): The subtitle content.
            progress_callback (Callable): A function to call for progress updates.

        Returns:
            List[List[str]]: A list of subtitle blocks, where each block is a list of lines.
        """
        parsed_blocks = []
        # First, remove the VTT header if it exists, so it doesn't interfere with parsing.
        if content.strip().startswith('WEBVTT'):
            content = re.sub(r'WEBVTT.*?\n\s*\n', '', content, 1, flags=re.DOTALL | re.IGNORECASE)

        raw_blocks = re.split(r'\n\s*\n', content.strip())
        
        for raw_block in raw_blocks:
            lines = [line.strip() for line in raw_block.split('\n') if line.strip()]
            if not lines:
                continue

            # A valid block needs at least a timeline and a text line.
            if len(lines) >= 2:
                if lines[0].isdigit():
                    parsed_blocks.append(lines)
                # We assume that if it's not a digit, it's the timeline.
                elif '-->' in lines[0] or ' - ' in lines[0]:
                    new_block = [str(len(parsed_blocks) + 1)] + lines
                    parsed_blocks.append(new_block)
            
        return parsed_blocks

    def _translate_blocks(self, blocks: List[List[str]], target_language: str,
                          progress_callback: Callable) -> List[List[str]]:
        """
        Translates the text in each subtitle block.

        Args:
            blocks (List[List[str]]): The list of subtitle blocks.
            target_language (str): The target language for translation.
            progress_callback (Callable): A function to call for progress updates.

        Returns:
            List[List[str]]: The list of subtitle blocks with translated text.
        """
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
        """
        Optimizes subtitle blocks by fixing timestamps and re-indexing.

        Args:
            blocks (List[List[str]]): The list of subtitle blocks.
            progress_callback (Callable): A function to call for progress updates.

        Returns:
            List[List[str]]: The optimized list of subtitle blocks.
        """
        optimized = []
        current_index = 1

        for i, block in enumerate(blocks):
            if len(block) < 2:
                continue
            
            # --- START OF CORRECTION ---
            # We make the check more flexible to accept "-->" or "-".
            timestamp_line = block[1]
            if "-->" not in timestamp_line and "-" not in timestamp_line:
                continue
            # --- END OF CORRECTION ---

            # Make sure the block has text before processing it.
            if len(block) < 3:
                continue
                
            block[0] = str(current_index)
            
            # Replace the non-standard separator with the standard SRT separator.
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
        """
        Formats the final list of subtitle blocks into a single string.

        Args:
            blocks (List[List[str]]): The list of subtitle blocks.
            progress_callback (Callable): A function to call for progress updates.

        Returns:
            str: The formatted subtitle content.
        """
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
