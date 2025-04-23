import streamlit as st
import os
from openai import OpenAI
import numpy as np
import os
from pydub import AudioSegment
import tensorflow as tf
from statistics import mode
from tensorflow import keras
from streamlit_option_menu import option_menu
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import requests  # Dùng để gửi yêu cầu API
import asyncio 
import streamlit.components.v1 as components    
from auth import register_user
from streamlit_cookies_manager import CookieManager
import base64
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
from create_lyrics import create_lyrics

# Load API key từ file .env
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
api_token = os.getenv("SUNO_API_TOKEN")

# Kết nối Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(os.path.exists("D:/test/Music-Genre-Recognition-main/.streamlit/secrets.toml"))





async def Feel_The_Beat():
    st.title("🎵 Feel The Beat - AI Music Generator")
    api_token = "2d551602f3a39d8f3e219db2c94d7659"

    custom_mode = st.toggle("Custom Mode", value=True)
    # Kiểm tra nếu custom_mode tắt
    if custom_mode == False:
        col1, col2 = st.columns([6, 4])
        with col1:
            if "lyrics" in st.session_state:
                lyrics = st.session_state.lyrics
                prompt = st.text_area("💡 Enter a description of the track you want to create:", 
                    value=lyrics, placeholder="A relaxing piano piece with a gentle melody...", height=300)
            else:
                prompt = st.text_area("💡 Enter a description of the track you want to create:", 
                    placeholder="A relaxing piano piece with a gentle melody...", height=300)
            style = "Classical"  # Gán giá trị mặc định nếu custom_mode tắt
            title = "My AI Music"  # Gán title mặc định nếu custom_mode tắt
            instrumental = st.checkbox("🎻 Instrumental", value=False)
        with col2:
            if "music_data" in st.session_state:
                music_data = st.session_state["music_data"]
                st.success(f"🎵 Your music is ready: [{title}]")
                for audio_url, title, image_url in music_data:
                    render_music_player(title, audio_url, image_url)
    else:
        col1, col2 = st.columns([6, 4])
        with col1:
            if "lyrics" in st.session_state:
                lyrics = st.session_state.lyrics
                prompt = st.text_area("💡 Enter a description of the track you want to create:", 
                    value=lyrics, placeholder="A relaxing piano piece with a gentle melody...", height=300)
            else:
                prompt = st.text_area("💡 Enter a description of the track you want to create:", 
                    placeholder="A relaxing piano piece with a gentle melody...", height=300)
            # Danh sách gợi ý phong cách nhạc
            music_styles = ["Classical", "Jazz", "Lo-fi", "Ambient", "Rock"]

            # Nếu chưa có session_state cho style_list, đặt giá trị mặc định
            if "style_list" not in st.session_state:
                st.session_state["style_list"] = []

            # Hộp nhập phong cách nhạc (hiển thị danh sách dưới dạng chuỗi)
            style = st.text_input("🎼 Enter music style:", ", ".join(st.session_state["style_list"]))

            # Đảm bảo style được sử dụng khi gửi yêu cầu
            style = style if style else "Classical"  # Nếu người dùng không nhập, sử dụng mặc định "Classical"

            # Hiển thị các nút theo hàng ngang
            cols = st.columns(len(music_styles))

            for i, music in enumerate(music_styles):
                with cols[i]:
                    if st.button(music, use_container_width=True):
                        if music in st.session_state["style_list"]:
                            # Nếu đã có trong danh sách thì xóa đi (bỏ chọn)
                            st.session_state["style_list"].remove(music)
                        else:
                            # Nếu chưa có thì thêm vào danh sách
                            st.session_state["style_list"].append(music)
                        
                        # Cập nhật text box với danh sách mới
                        st.rerun()  # Cập nhật giao diện ngay lập tức
        
            title = st.text_input("🎶 Name the song:", "My AI Music")
        with col2:
            if "music_data" in st.session_state:
                music_data = st.session_state["music_data"]
                st.success(f"🎵 Your music is ready: [{title}]")
                for audio_url, title, image_url in music_data:
                    render_music_player(title, audio_url, image_url)
        instrumental = st.checkbox("🎻 Instrumental", value=False)

    feel_the_beat = st.button(f"🎧 Feel The Beat", key=f"feel_the_beat")
    if feel_the_beat:
        # ✅ Kiểm tra user đã đăng nhập
        if "user" not in st.session_state:
            st.warning("🔐 You need to log in to use this feature.")
            st.stop()

        user_id = st.session_state["user"]["id"]

        # ✅ Kiểm tra số dư
        credit_data = supabase.table("user_credits").select("credits").eq("id", user_id).execute()
        current_credits = credit_data.data[0]["credits"] if credit_data.data else 0

        if current_credits < 25:
            st.error("❌ You do not have enough credits (25) to use this feature. Please top up.")
            st.stop()

        # ✅ Xóa nhạc cũ nếu có
        if "music_data" in st.session_state:
            del st.session_state["music_data"]

        if not api_token or not prompt:
            st.warning("⚠️ Please enter music description!")
        else:
            task_id = await generate_music(api_token, prompt, custom_mode, style, title, instrumental)
            if task_id:
                render_game_html()

                music_data = await check_music_status(api_token, task_id)

                if music_data:
                    # ✅ Trừ tín dụng nếu nhạc tạo thành công
                    new_credits = current_credits - 25
                    supabase.table("user_credits").update({"credits": new_credits}).eq("id", user_id).execute()
                    #st.session_state["music_data"] = music_data
                    for audio_url, title, image_url in music_data:
                        st.session_state["music_data"] = music_data
                # Tải lại trang để hiển thị nhạc mới
                else:
                    st.warning("⏳ Music not ready after 5 minutes, please try again later!")
                st.rerun()
            else:
                st.error("🚨 Error in music generation!")

    # Hàm tạo nhạc từ API
    async def generate_music(api_token, prompt, custom_mode, style, title, instrumental):
        api_url = "https://apibox.erweima.ai/api/v1/generate"
        headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
        
        if custom_mode == True:
            data = {
                "prompt": prompt,
                "style": style,
                "title": title,
                "customMode": custom_mode,
                "instrumental": instrumental,
                "model": "V4",
                "callBackUrl": "https://api.example.com/callback"
            }
        else:
            data = {
                "prompt": prompt,
                "customMode": custom_mode,
                "instrumental": instrumental,
                "model": "V4",
                "callBackUrl": "https://api.example.com/callback"
            }

        with st.spinner("🎼 Đang tạo nhạc..."):  # Đang tạo nhạc...
            response = await asyncio.to_thread(requests.post, api_url, json=data, headers=headers)
        
        # Kiểm tra mã trạng thái của phản hồi từ API
        if response.status_code == 200:
            try:
                response_json = response.json()  # Cố gắng phân tích dữ liệu JSON từ phản hồi

                # Kiểm tra nếu 'data' có tồn tại trong phản hồi
                data = response_json.get("data")  # Sử dụng .get() để tránh lỗi nếu 'data' không tồn tại

                if data is not None:
                    task_id = data.get("taskId")  # Lấy taskId từ 'data'
                    if task_id:
                        return task_id
                    else:
                        st.error("🚨 Không tìm thấy taskId trong phản hồi!")
                else:
                    st.error("🚨 Không có dữ liệu 'data' trong phản hồi API!")
                    st.write("📄 Nội dung API trả về:", response.text)
            except ValueError as e:
                st.error(f"🚨 Lỗi khi phân tích JSON từ API: {e}")
                st.write("📄 Nội dung API trả về:", response.text)
        else:
            st.error(f"🚨 API trả về lỗi: {response.status_code}")
            st.write("📄 Nội dung lỗi:", response.text)
        return None

    # Function to check and display music
    async def check_music_status(api_token, task_id):
        check_url = f"https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"
        headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
        # Truy vấn user_id từ bảng user_profiles bằng email
        if "user" in st.session_state and "email" in st.session_state["user"]:
            user_email = st.session_state["user"]["email"]  # Lấy email từ session

            # Query user_id from user_profiles table
            user_profile = supabase.table("user_profiles").select("id").eq("email", user_email).execute()

            if user_profile.data:
                user_id = user_profile.data[0]["id"]  # Lấy user_id từ profile
        else:
            st.error("❌ Không tìm thấy thông tin người dùng.")
            return None
            
        for _ in range(60):  # Lặp tối đa 60 lần (5 phút)
            check_response = await asyncio.to_thread(requests.get, check_url, headers=headers)

            if check_response.status_code == 200:
                try:
                    music_info = check_response.json()
                    data = music_info.get("data", {})
                    status = data.get("status", "PENDING")
                    # st.write("🛠️ Trạng thái từ API:", status)
                    # st.write("📄 Full dữ liệu API trả về:", data)
                    if status == "SUCCESS":
                        suno_data = data.get("response", {}).get("sunoData", [])
                        if suno_data:

                            # Save songs into the database (songs table)
                            for song in suno_data:
                                song_data = {
                                    #"user_id": st.session_state["user"]["id"],  # Liên kết với user_id
                                    "user_id": user_id,  # Liên kết với user_id từ bảng user_profiles
                                    "title": song.get("title"),
                                    "audio_url": song.get("audioUrl"),
                                    "image_url": song.get("imageUrl"),
                                    "prompt": song.get("prompt"),
                                    "model_name": song.get("modelName"),
                                    "duration": song.get("duration")
                                }
                                # Save into songs table in Supabase
                                supabase.table("songs").insert(song_data).execute()

                            return [(item.get("audioUrl"), item.get("title"), item.get("imageUrl")) for item in suno_data]
                except ValueError as e:
                    st.error(f"🚨 Lỗi khi phân tích JSON từ API: {e}")
                    st.write("📄 Nội dung API trả về:", check_response.text)
                    break
            else:
                st.error(f"🚨 Lỗi khi kiểm tra nhạc: {check_response.status_code}")
                break
            time.sleep(5)  # Chờ 5 giây trước khi kiểm tra lại
        return None


    def render_music_player(title, audio_url, image_url):
        """
        Displays the music player interface with title, cover art and music player.
        """
        st.markdown(
            """
            <style>
                .audio-container {
                    text-align: left;
                    padding: 20px;
                    position: relative;
                }
                audio {
                    width: 100%;
                    border: 4px solid #ff7e5f;
                    border-radius: 30px;
                    box-shadow: 0px 0px 15px #feb47b;
                }
                audio::-webkit-media-controls-timeline {
                    background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
                    border-radius: 30px;
                    height: 6px;
                    box-shadow: 0px 0px 10px rgba(255, 126, 95, 0.8);
                    transition: all 0.3s ease-in-out;
                    padding: 1px;
                }
                audio::-webkit-media-controls-play-button {
                    background-color: #ff7e5f !important;
                    box-shadow: 0px 0px 10px rgba(255, 126, 95, 0.8);
                    border-radius: 50%;
                }
                audio::-webkit-media-controls-volume-slider {
                    background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
                    border-radius: 30px;
                    height: 6px;
                    box-shadow: 0px 0px 10px rgba(255, 126, 95, 0.8);
                    transition: all 0.3s ease-in-out;
                    margin-top: 11px;
                    padding-top:1px;
                    padding-bottom:1px;
                }
                .song-title {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    text-align: left;
                    margin-top: 10px;
                    text-shadow: 0px 0px 10px rgba(255, 126, 95, 0.8);
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns([2, 5])
        with col1:
            st.image(image_url, width=250)
        with col2:
            st.markdown(f'<div class="song-title">{title}</div>', unsafe_allow_html=True)
            st.audio(audio_url, format="audio/mp3")


    # Hàm hiển thị trò chơi chờ nhạc
    def render_game_html():
        game_html = """
        <iframe src="https://chromedino.com/color/" frameborder="0" scrolling="no" width="100%" height="100%" loading="lazy"></iframe>
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #0E1117; /* Màu nền */
            color: #FFA500; /* Màu chữ cam */
            font-size: 24px; /* Kích thước chữ */
            font-weight: bold; /* Đậm chữ */
            z-index: 102;
            display: flex; /* Căn giữa */
            align-items: center; /* Căn giữa theo chiều dọc */
            justify-content: center; /* Căn giữa theo chiều ngang */
            white-space: pre-line; /* Giữ nguyên xuống dòng */
            flex-direction: column; /* Xếp nội dung theo chiều dọc */
            text-align: center; /* Căn giữa chữ */
        ">
            <div>
            🔥 Survive until the music is over 🔥
            </div>
            <p style="font-size: 16px; font-weight: normal;">
                You can play Running Dinosaur while waiting for the music (up to 5 minutes).  
                Press Space to start the game online and jump your Dino, use down arrow (↓) to duck.
            </p>
        </div>
        
        <style type="text/css">
        iframe { 
            margin-top: 20px;
            position: absolute; 
            width: 100%; 
            height: 100%; 
            z-index: 100; 
        }
        </style>
        """
        st.components.v1.html(game_html, height=320)








