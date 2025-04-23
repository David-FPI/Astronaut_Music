# file: create_lyrics.py

import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client

def create_lyrics():
    # Load biến môi trường nếu đang chạy local
    load_dotenv()

    # Lấy OpenAI API key từ secrets hoặc env
    def get_openai_client():
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("❌ Không tìm thấy OPENAI_API_KEY trong secrets hoặc .env.")
            raise ValueError("Thiếu OPENAI_API_KEY")
        return OpenAI(api_key=api_key)

    # Lấy Supabase client
    def get_supabase_client():
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except KeyError:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            st.warning("⚠️ Thiếu thông tin kết nối Supabase.")
        return create_client(url, key)

    # Khởi tạo client
    client = get_openai_client()
    supabase = get_supabase_client()

    # Gọi API để tạo lời bài hát
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

    # Giao diện
    st.markdown("<h1>🎶 AI Lyric Generator 🎵</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 5])

    with col1:
        genre = st.text_area("🎼 Thể loại nhạc", placeholder="Pop, Rock, Ballad, EDM...")
        mood = st.text_area("🎭 Cảm xúc", placeholder="Vui, Buồn, Hào hứng, Lãng mạn...")
        theme = st.text_area("✍️ Chủ đề", placeholder="Tình yêu, Tuổi trẻ, Mùa đông,...")

        lyrics = st.session_state.get("lyrics_input", "")

        if st.button("🎤 Sáng tác ngay!"):
            if theme.strip():
                with st.spinner("🎶 AI đang sáng tác lời bài hát cho bạn..."):
                    prompt = f"Hãy viết lời bài hát thể loại {genre}, chủ đề '{theme}', với cảm xúc {mood}."
                    lyrics = generate_lyrics(prompt)
                    st.session_state.lyrics_input = lyrics
            else:
                st.warning("⚠️ Bạn chưa nhập chủ đề bài hát!")

    with col2:
        lyrics_input = st.text_area("🎼 Lời bài hát AI tạo:", value=lyrics, height=370)
        st.session_state.lyrics_input = lyrics_input

        if st.button("📋 Copy Lyrics"):
            st.session_state.lyrics = lyrics_input
            st.success("✅ Lyrics đã được sao chép (trong session)")

    # Cập nhật nếu người dùng chỉnh sửa lyrics
    if lyrics_input != lyrics:
        st.session_state.lyrics_input = lyrics_input
