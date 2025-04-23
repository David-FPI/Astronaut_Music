from openai import OpenAI
import streamlit as st
import pyperclip
from supabase import create_client, Client
from dotenv import load_dotenv
import os
# Load API key từ file .env
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")
# Sử dụng OpenAI API Key từ secrets của Streamlit
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Khởi tạo client OpenAI với API key (sử dụng client như yêu cầu)
# Khai báo client cho OpenAI
openai.api_key = OPENAI_API_KEY
client = openai  # đồng bộ đặt tên

# Kết nối Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



def create_lyrics():
    
    def generate_lyrics(prompt):
        """Gửi prompt đến OpenAI API để tạo lời bài hát"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Hoặc "gpt-3.5-turbo" nếu tài khoản không có quyền truy cập GPT-4
                messages=[
                    {"role": "system", "content": "Bạn là một nhạc sĩ sáng tác lời bài hát chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=900
            )

            # ✅ Lấy nội dung phản hồi đúng cách
            return response.choices[0].message.content  

        except Exception as e:
            return f"⚠️ Lỗi khi tạo lời bài hát: {str(e)}"

    st.markdown("<h1>🎶 AI Lyric Generator 🎵</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 5])
    with col1:
        # Người dùng nhập thể loại nhạc và chủ đề
        genre = st.text_area("🎼 Chọn thể loại nhạc: ",
                            placeholder="Pop, Rock, Hip-Hop, Jazz, Ballad, EDM,....")
        mood = st.text_area("🎭 Chọn cảm xúc: ",
                            placeholder="Vui vẻ, Buồn, Hào hứng, Thư giãn, Kịch ,....")
        theme = st.text_area("✍️ Mô tả bản nhạc bạn muốn tạo:",
                            placeholder="Tình yêu, Mùa thu, Tuổi trẻ, ...")
        if "lyrics_input" in st.session_state:
            lyrics = st.session_state.lyrics_input
        else:
            lyrics = ""
        if st.button("🎤 Sáng tác ngay!"):
            if theme.strip():
                with st.spinner("🎶 AI đang sáng tác lời bài hát cho bạn..."):
                    prompt = f"Hãy viết lời bài hát thể loại {genre} về chủ đề '{theme}', với cảm xúc {mood}."
                    lyrics = generate_lyrics(prompt)
            else:
                st.warning("⚠️ Vui lòng nhập chủ đề bài hát trước khi tạo!")
    with col2:
    # Hiển thị text_area và lưu giá trị trực tiếp vào lyrics    
        lyrics_input = st.text_area("🎼 Lời bài hát AI tạo:", lyrics, height=370)
    # Kiểm tra nếu nội dung text_area thay đổi và tự động sao chép vào clipboard
        st.session_state.lyrics_input = lyrics
    
        if st.button("Copy Lyrics"):
                # pyperclip.copy(lyrics_input)  # Sao chép lyrics vào clipboard
                lyrics = lyrics_input
                st.session_state.lyrics = lyrics
                st.success("Lyrics have been copied to clipboard and Feel The Beat")  # Hiển thị thông báo thành công

    if lyrics_input != lyrics:
        lyrics = lyrics_input
        st.session_state.lyrics_input = lyrics
