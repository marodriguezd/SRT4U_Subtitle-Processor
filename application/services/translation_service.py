# application/services/translation_service.py
"""
This module provides a service for translating text using the deep-translator library.
"""
from typing import Callable, Optional
from deep_translator import GoogleTranslator


class TranslationService:
    """
    A service class for handling text translation.
    """
    def translate_text(self, text: str, target_language: str,
                       progress_callback: Optional[Callable] = None) -> str:
        """
        Translates a given text to a target language using Google Translate.

        Args:
            text (str): The text to be translated.
            target_language (str): The language code of the target language (e.g., 'en', 'es').
            progress_callback (Optional[Callable]): An optional callback function to
                                                     be called with the translation result.

        Returns:
            str: The translated text.
        """
        translator = GoogleTranslator(source="auto", target=target_language)
        translated_text = translator.translate(text)

        if progress_callback:
            progress_callback('translation', translated_text)

        return translated_text