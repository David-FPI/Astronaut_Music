# file: create_lyrics.p
import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

def create_lyrics():
    # ✅ Lấy API key từ Streamlit secrets (Cloud chuẩn)
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("❌ Không tìm thấy OPENAI_API_KEY trong `Secrets`. Vào App → Settings → Secrets để thêm.")
        return

    # ✅ Kết nối Supabase
    try:
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception:
        st.warning("⚠️ Supabase credentials chưa được cấu hình đầy đủ trong `Secrets`.")

    # 🧠 Hàm gọi API để tạo lyrics
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

    # 🎨 Giao diện người dùng
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
            st.success("✅ Lyrics đã được sao chép vào session!")

    # Đồng bộ nếu có chỉnh sửa thủ công
    if lyrics_input != lyrics:
        st.session_state.lyrics_input = lyrics_input
