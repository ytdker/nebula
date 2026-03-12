"""
utils/image_utils.py
Görsel doğrulama ve ön işleme — Nebula
"""
from PIL import Image
import io

from config import MAX_IMAGE_SIZE_MB, SUPPORTED_FORMATS

MAX_DIMENSION = 1024  # Gemini API önerilen limit


def validate_and_load(uploaded_file) -> Image.Image:
    """
    Streamlit'ten gelen yüklü dosyayı doğrular ve PIL Image olarak döndürür.

    Args:
        uploaded_file: st.file_uploader'dan gelen nesne

    Returns:
        PIL Image (RGB modunda)

    Raises:
        ValueError: Dosya geçersizse
    """
    if uploaded_file is None:
        raise ValueError("Dosya yüklenmedi.")

    # Format kontrolü
    filename = uploaded_file.name.lower()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Desteklenmeyen format: .{ext}\n"
            f"Kabul edilen formatlar: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Boyut kontrolü (MB)
    file_bytes = uploaded_file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(
            f"Dosya çok büyük: {size_mb:.1f} MB\n"
            f"Maksimum izin verilen boyut: {MAX_IMAGE_SIZE_MB} MB"
        )

    # PIL'e yükle
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image = image.convert("RGB")  # RGBA / pallete modlarını normalize et
    except Exception:
        raise ValueError("Görsel açılamadı. Dosya bozuk olabilir.")

    return image


def resize_for_api(image: Image.Image) -> Image.Image:
    """
    Görseli API limitlerine uygun boyuta küçültür.
    En uzun kenar MAX_DIMENSION'ı aşmıyorsa dokunmaz.
    """
    w, h = image.size
    if max(w, h) <= MAX_DIMENSION:
        return image

    if w >= h:
        new_w = MAX_DIMENSION
        new_h = int(h * MAX_DIMENSION / w)
    else:
        new_h = MAX_DIMENSION
        new_w = int(w * MAX_DIMENSION / h)

    return image.resize((new_w, new_h), Image.LANCZOS)
