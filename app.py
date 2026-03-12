"""
app.py — Nebula: Kozmik Kahve Falı Uygulaması
Streamlit + Gemini 1.5 Flash
"""
import streamlit as st
from datetime import datetime
from utils.image_utils import validate_and_load, resize_for_api
from utils.gemini_utils import analyze_cup
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    MAX_HISTORY,
    GEMINI_API_KEY,
)

# ── Sayfa Yapılandırması ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nebula — Kahve Falı",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS: Kozmik Dark Tema ────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Lato:wght@300;400;700&display=swap');

/* Arka plan */
.stApp {
    background: radial-gradient(ellipse at top, #1a0030 0%, #0a0015 50%, #000008 100%);
    font-family: 'Lato', sans-serif;
    color: #e8d5ff;
}

/* Başlık */
.nebula-title {
    font-family: 'Cinzel', serif;
    font-size: 3.2rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #f5c842 0%, #e8a5ff 50%, #7b61ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.18em;
    margin-bottom: 0;
    text-shadow: none;
    animation: shimmer 4s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { filter: brightness(1); }
    50% { filter: brightness(1.3); }
}

.nebula-subtitle {
    font-family: 'Lato', sans-serif;
    font-size: 0.95rem;
    text-align: center;
    color: #9b6ec8;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    margin-top: 0.3rem;
    margin-bottom: 2rem;
}

/* Cam efekti kart */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(245, 200, 66, 0.2);
    border-radius: 16px;
    padding: 1.8rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(123, 97, 255, 0.15);
}

/* Fal sonuç kartı */
.fortune-card {
    background: linear-gradient(135deg,
        rgba(26, 0, 48, 0.9) 0%,
        rgba(15, 0, 30, 0.95) 100%);
    border: 1px solid rgba(245, 200, 66, 0.4);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow:
        0 0 40px rgba(123, 97, 255, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.05);
    line-height: 1.9;
    font-size: 1.02rem;
    color: #e8d5ff;
    animation: fadeInUp 0.8s ease;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Yıldız parıltıları */
.star-divider {
    text-align: center;
    color: #f5c842;
    font-size: 1.1rem;
    letter-spacing: 0.8rem;
    margin: 1rem 0;
    opacity: 0.7;
}

/* Upload alanı */
[data-testid="stFileUploader"] {
    background: rgba(123, 97, 255, 0.06) !important;
    border: 2px dashed rgba(245, 200, 66, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* Buton */
.stButton > button {
    background: linear-gradient(135deg, #7b61ff 0%, #9b3bcc 50%, #f5c842 100%);
    color: #0a0015;
    font-family: 'Cinzel', serif;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    border: none;
    border-radius: 50px;
    padding: 0.75rem 2.5rem;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(123, 97, 255, 0.4);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(245, 200, 66, 0.5);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(10, 0, 21, 0.95) !important;
    border-right: 1px solid rgba(123, 97, 255, 0.2) !important;
}

.sidebar-history-item {
    background: rgba(123, 97, 255, 0.08);
    border: 1px solid rgba(123, 97, 255, 0.2);
    border-radius: 10px;
    padding: 0.7rem;
    margin: 0.5rem 0;
    font-size: 0.82rem;
    color: #c0a0e8;
}

/* Spinner */
[data-testid="stSpinner"] { color: #f5c842 !important; }

/* Hata kutuları */
.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid #f5c842 !important;
}

/* Markdown h2/h3 */
.fortune-card h2, .fortune-card h3 {
    font-family: 'Cinzel', serif !important;
    color: #f5c842 !important;
}

/* Genel başlıklar */
h1, h2, h3 { font-family: 'Cinzel', serif !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ── Session State Başlatma ───────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # [{time, preview, result}]
if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ── Sidebar: Geçmiş Okumalar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h3 style='font-family:Cinzel,serif;color:#f5c842;text-align:center;'>✦ Geçmiş Okumalar</h3>",
        unsafe_allow_html=True,
    )
    if not st.session_state.history:
        st.markdown(
            "<p style='color:#6b4a8a;text-align:center;font-size:0.85rem;'>"
            "Henüz okuma yapılmadı...</p>",
            unsafe_allow_html=True,
        )
    else:
        for i, entry in enumerate(reversed(st.session_state.history)):
            st.markdown(
                f"""<div class='sidebar-history-item'>
                    <b style='color:#f5c842;'>#{len(st.session_state.history)-i}</b>
                    &nbsp;·&nbsp; {entry['time']}<br/>
                    <span style='color:#9b6ec8;'>{entry['preview']}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    if st.session_state.history:
        if st.button("🗑 Geçmişi Temizle", key="clear_history"):
            st.session_state.history = []
            st.session_state.last_result = None
            st.rerun()


# ── Ana İçerik ───────────────────────────────────────────────────────────────
st.markdown(f"<div class='nebula-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='nebula-subtitle'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)
st.markdown("<div class='star-divider'>✦ ✦ ✦</div>", unsafe_allow_html=True)

# API Key kontrolü
if not GEMINI_API_KEY:
    st.markdown(
        """<div class='glass-card'>
        <b style='color:#f5c842;'>⚠️ API Anahtarı Eksik</b><br/><br/>
        <code>.env</code> dosyasında <code>GEMINI_API_KEY</code> tanımlı değil.<br/>
        <a href='https://aistudio.google.com/app/apikey'
           style='color:#7b61ff;'>Google AI Studio</a>'dan ücretsiz anahtar alabilirsin.
        </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

# ── Yükleme Alanı ────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center;color:#9b6ec8;margin-bottom:0.5rem;'>"
    "Kahve fincanının fotoğrafını yükle, Nebula sırrını açsın...</p>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    label="Fincan Görseli",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
    help="JPG, PNG veya WebP · Maks 10 MB",
)

if uploaded_file:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(uploaded_file, use_container_width=True, caption="☕ Fincan hazır")

    st.markdown("<br/>", unsafe_allow_html=True)
    analyze_btn = st.button("🔮 Falıma Bak", key="analyze")

    if analyze_btn:
        with st.spinner("Nebula yıldızları okuyor..."):
            try:
                # Görsel doğrula & yeniden boyutlandır
                image = validate_and_load(uploaded_file)
                image = resize_for_api(image)

                # Gemini'ye gönder
                result_text = analyze_cup(image)

                # Geçmişe ekle
                timestamp = datetime.now().strftime("%H:%M")
                preview = (result_text[:80] + "…") if len(result_text) > 80 else result_text
                st.session_state.history = (
                    st.session_state.history + [{"time": timestamp, "preview": preview}]
                )[-MAX_HISTORY:]
                st.session_state.last_result = result_text

            except ValueError as e:
                st.error(f"⚠️ {e}")
                st.stop()
            except RuntimeError as e:
                st.error(f"🌌 {e}")
                st.stop()
            except Exception as e:
                st.error(f"Beklenmeyen bir hata oluştu: {e}")
                st.stop()

# ── Sonuç Gösterimi ──────────────────────────────────────────────────────────
if st.session_state.last_result:
    st.markdown(
        f"<div class='fortune-card'>{st.session_state.last_result.replace(chr(10), '<br/>')}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='star-divider'>✦ &nbsp; Nebula &nbsp; ✦</div>", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#3d2060;font-size:0.75rem;'>"
    "Nebula • Kozmik Kahve Falı · v1.0</p>",
    unsafe_allow_html=True,
)
