# Nebula 🔮 — Kozmik Kahve Falı

Nebula, Google Gemini 2.0 Flash modelini kullanarak kahve fincanı fotoğraflarını analiz eden ve geleneksel Türk kahvesi sembolojisiyle mistik fallar üreten bir Streamlit uygulamasıdır.

## ✨ Özellikler

- **Kozmik Tema:** Derin uzay estetiği ve mistik arayüz.
- **Yapay Zeka Destekli Analiz:** Gemini 2.0 Flash ile hızlı ve tutarlı şekil tespiti.
- **Mistik Dil:** Kadim bilgilerle donatılmış, şiirsel fal yorumları.
- **Geçmiş Yönetimi:** Oturum boyunca yapılan falları sidebar'da saklama.

## 🚀 Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/ytdker/nebula.git
   cd nebula
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. API anahtarını ekleyin:
   - `.env.example` dosyasını `.env` olarak kopyalayın.
   - [Google AI Studio](https://aistudio.google.com/app/apikey) üzerinden aldığınız API key'i `.env` içine yapıştırın.
   ```bash
   GEMINI_API_KEY=AIzaSy...
   ```

4. Uygulamayı çalıştırın:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Teknoloji Yığını

- **Dil:** Python 3.10+
- **Arayüz:** Streamlit
- **AI Model:** Google Gemini 2.0 Flash
- **Kütüphaneler:** Pillow, python-dotenv, google-generativeai

---
*Nebula'nın ışığı yolunu aydınlatsın...* 🌌
