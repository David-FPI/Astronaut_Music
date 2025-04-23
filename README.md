# 🌌 Astronaut Music AI Platform

> Create lyrics and generate music tracks with powerful AI models, integrated user system, payment gateway (MoMo), and genre classification.

## 🎧 Features

### ✨ User Dashboard
- ✉ Email-based registration/login with password encryption (bcrypt).
- ✨ Cookie-based session management.
- 🚀 Auth pages: Login / Register / Forgot Password.

### 🎵 Feel The Beat
- 🎨 Generate AI music using **custom or default modes**.
- 🌌 Choose music styles like: *Jazz*, *Lo-fi*, *Classical*, *Rock*, etc.
- 🎧 Listen in-browser with beautiful player interface.
- 🚀 Built-in idle game (Dino Runner) while music is being generated.

### 🎶 Create Lyrics
- 🎤 Enter genre, mood, and topic prompts.
- 🤖 Generate lyrics using GPT-4o or GPT-3.5.
- 🎓 Copy lyrics directly into the music generator (shared state).

### 🎤 Music Genre Classifier
- 📚 Upload any MP3 file to identify the genre.
- 🌐 Mel Spectrograms via Librosa + CNN prediction.
- 📊 Bar chart visualization of predictions.

### 📆 Personal Music Library
- 💼 Songs saved by user (with metadata).
- ☆ Toggle visibility (Public/Private) + Delete.
- ✔ Manage with simple switches and dynamic rendering.

### 💳 MoMo Payment Integration
- 🌐 Purchase credit packages in VND (auto conversion USD → VND).
- 🏛️ View transaction history (last 90 days).
- 🌟 Handle payment callback via Return URL.

## 🌐 Tech Stack
- **Frontend**: Streamlit + HTML/CSS (custom theme).
- **Backend**: Python (asyncio, Supabase, OpenAI API, MoMo Gateway).
- **Modeling**: TensorFlow/Keras CNN for genre classification.
- **AI APIs**: GPT-4o for lyric generation, Suno/SunoBox for music creation.

## 📑 Directory Overview
```
|- app.py (Main script)
|- auth/ (authentication modules)
|- home.py, classify.py, create_lyrics.py, feel_the_beat.py, payment.py
|- chatbot.py
|- .streamlit/secrets.toml
|- README.md
```

## ⚡ Setup Instructions

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```
2. **Configure environment**:
```bash
cp .env.example .env
```
Update:
```
OPENAI_API_KEY=...
SUNO_API_TOKEN=...
```
3. **Run Streamlit**:
```bash
streamlit run app.py
```

## ✨ Demo
st.image("4.png", use_container_width=True)

## 🚀 Contributors
- 🔹 [@thanhnamm9999](mailto:thanhnamm9999@gmail.com) — Lead Developer, UI/UX

## 🎁 Support & Feedback
Found a bug or need help? Feel free to open an issue or contact via email.

---

> "Where words fail, music speaks." — Hans Christian Andersen

