# application/services/translation_service.py
from deep_translator import GoogleTranslator
from typing import Callable, Optional


class TranslationService:
    def translate_text(self, text: str, target_language: str,
                       progress_callback: Optional[Callable] = None) -> str:
        translator = GoogleTranslator(source="auto", target=target_language)
        translated_text = translator.translate(text)

        if progress_callback:
            progress_callback('translation', translated_text)

        return translated_text