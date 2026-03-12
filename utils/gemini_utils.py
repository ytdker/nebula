"""
utils/gemini_utils.py
Gemini 1.5 Flash API sarmalayıcısı — Nebula
"""
import io
import google.generativeai as genai
from PIL import Image

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_INSTRUCTION, MASTER_PROMPT


def get_gemini_client() -> genai.GenerativeModel:
    """API istemcisini sistem talimatıyla başlatır."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY bulunamadı. Lütfen .env dosyanı kontrol et.")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
    )
    return model


def analyze_cup(image: Image.Image) -> str:
    """
    Kahve fincanı görselini Gemini'ye gönderir ve ham fal metnini döndürür.

    Args:
        image: PIL Image nesnesi

    Returns:
        Gemini'den gelen ham metin yanıtı

    Raises:
        ValueError: API key eksikse
        RuntimeError: API çağrısı başarısız olursa
    """
    try:
        model = get_gemini_client()

        # Görseli byte buffer'a dönüştür
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        image_data = buffer.read()

        # Gemini multimodal çağrısı
        response = model.generate_content(
            [
                MASTER_PROMPT,
                {
                    "mime_type": "image/jpeg",
                    "data": image_data,
                },
            ]
        )

        if not response.text:
            raise RuntimeError("Nebula şu an sessiz... Lütfen tekrar dene.")

        return response.text

    except ValueError:
        raise
    except Exception as e:
        error_msg = str(e)
        # Hata ayıklama için terminale yazdır
        print(f"DEBUG - Gemini Error: {error_msg}")
        
        if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
            raise ValueError(f"Geçersiz API anahtarı: {error_msg}")
        elif "QUOTA" in error_msg.upper() or "EXHAUSTED" in error_msg.upper() or "429" in error_msg:
            raise RuntimeError(f"API kotası doldu veya çok fazla istek (429). Detay: {error_msg}")
        elif "SAFETY" in error_msg.upper():
            raise RuntimeError(f"Görsel güvenlik filtresine takıldı (Safety). Detay: {error_msg}")
        else:
            raise RuntimeError(f"Nebula'ya ulaşılamadı. Teknik detay: {error_msg}")
