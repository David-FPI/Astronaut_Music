import streamlit as st
import time
from supabase import create_client, Client
import pandas as pd
import streamlit.components.v1 as components  
from supabase import create_client, Client
# Kết nối Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def show_home():
     # Header Animation and Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem; animation: fadeIn 1.5s ease-out;">
        <div style="font-size: 3rem; font-weight: 800; 
                background: linear-gradient(45deg, #ff7e5f, #feb47b, #ff7e5f);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 10px;">
            ASTRONAUT MUSIC
        </div>
        <div style="font-size: 1.5rem; color: rgba(255,255,255,0.8); font-weight: 300">
            Tạo nhạc và lời bài hát bằng công nghệ AI tiên tiến
        </div>
    </div>
    """, unsafe_allow_html=True)
    

    
    # HOT IN APRIL SECTION
    st.markdown("<h2 style='text-align: left; margin-top: 1rem;'>🔥 Bài Hát Hot Trong Tháng 4</h2>", unsafe_allow_html=True)

    public_songs = supabase.table("songs").select("*").eq("is_public", True).order("created_at", desc=True).execute()
    user_profiles = supabase.table("user_profiles").select("id, full_name").execute()
    user_map = {u["id"]: u["full_name"] for u in user_profiles.data}

    public_songs = supabase.table("songs").select("*").eq("is_public", True).order("created_at", desc=True).execute()
    user_profiles = supabase.table("user_profiles").select("id, full_name").execute()
    user_map = {u["id"]: u["full_name"] for u in user_profiles.data}

    if public_songs.data:
        songs = public_songs.data

        slides_html = ""
        for idx, song in enumerate(songs):
            title = song.get("title", "Untitled")
            artist = user_map.get(song["user_id"], "Ẩn danh")
            image = song.get("image_url", "https://via.placeholder.com/300x180.png?text=No+Cover")
            audio = song.get("audio_url")
            duration = song.get("duration", 0)
            mins, secs = int(duration // 60), int(duration % 60)

            slide = f"""
            <div class='swiper-slide'>
                <div style='background:#1e1e1e; padding:10px; border-radius:12px; width:200px; color:white; font-family:sans-serif;'>
                    <div style='position:relative;'>
                        <img src="{image}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 20px; background: #000;" />
                        <div style='position:absolute; top:6px; left:6px; background:#00cc88; color:white; font-size:10px; padding:2px 6px; border-radius:4px;'>v3-5</div>
                        <div style='position:absolute; top:6px; right:6px; background:#333; color:white; font-size:10px; padding:2px 6px; border-radius:4px;'>{mins}:{secs:02}</div>
                        <div onclick='playTrack("{title}", "{artist}", "{audio}", "{image}")' style='position:absolute; bottom:6px; right:6px; background:#ff7e5f; color:white; font-size:11px; padding:6px 10px; border-radius:6px; cursor:pointer;'>▶ Nghe ngay</div>
                    </div>
                    <div style='margin-top:8px; font-size:13px; font-weight:bold;'>{title}</div>
                    <div style='font-size:11px; color:#bbb;'>👤 {artist}</div>
                </div>
            </div>
            """
            slides_html += slide

        # Player style & function
        popup_html = """
        <div id='musicPlayerPopup' style='
            display:none;
            position:fixed;
            bottom:0;
            left:0;
            width:100vw;
            background:#181818;
            border-top:1px solid #333;
            box-shadow:0 -2px 10px rgba(0,0,0,0.5);
            color:white;
            z-index:9999;
            padding: 10px 20px;
            transition: all 0.3s ease-in-out;
        '>
            <div style='
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:20px;
                max-width:100%;
                margin-left: 0;
                margin-right: auto;
                padding-left: 20px;
            '>

                <img id='popupImage' src='' style='width:60px; height:60px; object-fit:cover; border-radius:10px;'>
                <div style="flex-grow:1;">
                    <div id='popupTitle' style='font-size:15px; font-weight:bold;'></div>
                    <div id='popupArtist' style='font-size:13px; color:#ccc;'></div>
                </div>
                <audio id='popupAudio' controls autoplay style='
                    width: 80%;
                    height: 35px;
                    border-radius: 8px;
                    background-color: #222;
                '></audio>

                <button onclick="document.getElementById('musicPlayerPopup').style.display='none'" style="background:none; border:none; color:white; font-size:22px;">×</button>
            </div>
        </div>

        <script>
        function playTrack(title, artist, audioUrl, imageUrl) {{
            document.getElementById('musicPlayerPopup').style.display = 'block';
            document.getElementById('popupTitle').innerText = title;
            document.getElementById('popupArtist').innerText = artist;
            document.getElementById('popupAudio').src = audioUrl;
            document.getElementById('popupImage').src = imageUrl;
        }}
        </script>
        """
        
        # Swiper & Player HTML
        full_html = f"""

        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css'/>
        <script src='https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js'></script>
        <div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:16px; max-height:750px; overflow-y:auto; padding:5px;'>
                {slides_html}
        </div>
  

        {popup_html}

        <script>
        const swiper = new Swiper('.swiper', {{
            slidesPerView: 3,
            spaceBetween: 225,
            freeMode: true,
            grabCursor: true,
            breakpoints: {{
                640: {{ slidesPerView: 2 }},
                768: {{ slidesPerView: 3 }},
                1024: {{ slidesPerView: 5 }},
                1280: {{ slidesPerView: 7 }},
            }}
        }});
        </script>
        """

        components.html(full_html, height=850 )

    else:
        st.info("🙈 Chưa có bài hát nào được chia sẻ.")
    # Thẻ thông tin tính năng
    features_col1, features_col2, features_col3 = st.columns(3)
    
    with features_col1:
        st.markdown("""
        <div class="custom-container" style="height: 100%; text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 15px;">✏️</div>
            <h3 style="margin-bottom: 10px;">Tạo lời bài hát</h3>
            <p style="color: rgba(255,255,255,0.7);">
                Dùng AI để viết lời bài hát theo phong cách và cảm xúc bạn mong muốn
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with features_col2:
        st.markdown("""
        <div class="custom-container" style="height: 100%; text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🎵</div>
            <h3 style="margin-bottom: 10px;">Sáng tạo âm nhạc</h3>
            <p style="color: rgba(255,255,255,0.7);">
                Tạo ra các bản nhạc độc đáo với AI theo phong cách riêng của bạn
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with features_col3:
        st.markdown("""
        <div class="custom-container" style="height: 100%; text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
            <h3 style="margin-bottom: 10px;">Phân tích thể loại</h3>
            <p style="color: rgba(255,255,255,0.7);">
                Phân tích và xác định thể loại nhạc từ file âm thanh của bạn
            </p>
        </div>
        """, unsafe_allow_html=True)




