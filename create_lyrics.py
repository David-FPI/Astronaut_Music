import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client

# Tải biến môi trường từ .env (nếu chạy local)
load_dotenv()

# Lấy API key từ Streamlit secrets hoặc .env
def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.getenv("OPENAI_API_KEY")

# Khởi tạo client OpenAI
client = OpenAI(api_key=get_openai_key())

# Kết nối Supabase
def get_supabase_client():
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except KeyError:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = get_supabase_client()

# Hàm tạo lời bài hát
def create_lyrics():
    
    def generate_lyrics(prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Bạn là một nhạc sĩ sáng tác lời bài hát chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=900
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Lỗi khi tạo lời bài hát: {str(e)}"

    st.markdown("<h1>🎶 AI Lyric Generator 🎵</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 5])
    with col1:
        genre = st.text_area("🎼 Thể loại nhạc:", placeholder="Pop, Rock, Ballad...")
        mood = st.text_area("🎭 Cảm xúc:", placeholder="Buồn, Hạnh phúc, Hào hứng...")
        theme = st.text_area("✍️ Chủ đề bài hát:", placeholder="Tình yêu, Mùa thu, Tuổi trẻ...")

        lyrics = st.session_state.get("lyrics_input", "")

        if st.button("🎤 Sáng tác ngay!"):
            if theme.strip():
                with st.spinner("🎶 AI đang sáng tác lời bài hát cho bạn..."):
                    prompt = f"Hãy viết lời bài hát thể loại {genre}, chủ đề '{theme}', với cảm xúc {mood}."
                    lyrics = generate_lyrics(prompt)
                    st.session_state.lyrics_input = lyrics
            else:
                st.warning("⚠️ Vui lòng nhập chủ đề bài hát trước khi tạo!")

    with col2:
        lyrics_input = st.text_area("🎼 Lời bài hát AI tạo:", value=lyrics, height=370)
        st.session_state.lyrics_input = lyrics_input

        if st.button("📋 Copy Lyrics"):
            st.session_state.lyrics = lyrics_input
            st.success("✅ Lời bài hát đã được sao chép (tạm thời trong session)!")

    if lyrics_input != lyrics:
        st.session_state.lyrics_input = lyrics_input
