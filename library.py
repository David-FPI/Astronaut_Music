import streamlit as st
import os
import bcrypt
import re  # Thêm thư viện kiểm tra email hợp lệ
import numpy as np
import base64
import pytube
import os
import subprocess 
import librosa
import tempfile 
from pydub import AudioSegment
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import tensorflow as tf
from statistics import mode
from tensorflow import keras
from keras import regularizers
from keras.preprocessing.image import load_img, img_to_array
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
import hmac
import hashlib
import uuid
import pandas as pd
from datetime import datetime, timedelta


# Load API key từ file .env
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")
api_token = os.getenv("SUNO_API_TOKEN")

# Kết nối Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(os.path.exists("D:/test/Music-Genre-Recognition-main/.streamlit/secrets.toml"))

def show_library():
    
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
        
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(image_url, width=150)
        with col2:
            st.markdown(f'<div class="song-title">{title}</div>', unsafe_allow_html=True)
            st.audio(audio_url, format="audio/mp3")



    def st_toggle_switch(
        label,
        key,
        default_value=False,
        label_after=False,
        active_color="#4CAF50",      # Màu bật
        inactive_color="#888",       # Màu tắt
        track_color="#ccc"           # Màu nền
    ):
        _ = active_color, inactive_color, track_color  # Đánh dấu là đã dùng
        toggle_value = st.toggle(
            label if not label_after else "",
            value=default_value,
            key=key,
        )

        if label_after:
            st.write(f"**{label}**")

        return toggle_value
   
    if "user" in st.session_state and "email" in st.session_state["user"]:
        user_email = st.session_state["user"]["email"]
        user_profile = supabase.table("user_profiles").select("id").eq("email", user_email).execute()

        if user_profile.data:
            user_id = user_profile.data[0]["id"]
            songs = supabase.table("songs").select("*").eq("user_id", user_id).execute()

            if songs.data:
                st.subheader("🎶 Your Music Library")

                # ✅ Sắp xếp bài public lên đầu
                sorted_songs = sorted(songs.data, key=lambda x: not x.get("is_public", False))

                for song in sorted_songs:
                    # Tạo 2 cột: 1 bên ảnh + switch, 1 bên audio + info
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        render_music_player(song['title'], song['audio_url'], song['image_url'])
                        st.write(f"📝 Prompt: {song['prompt']}")
                        col3, col4 = st.columns([1, 7])
                        with col3:
                            is_public = song.get("is_public", False)
                            new_status = st_toggle_switch(
                                label="Public",  # Label chữ Public
                                key=f"toggle_{song['id']}",
                                default_value=is_public,
                                label_after=False,
                                active_color="#FF69B4",
                                inactive_color="#444",
                                track_color="#fce4ec" if is_public else "#999",
                            )
                            if new_status != is_public:
                                supabase.table("songs").update({"is_public": new_status}).eq("id", song["id"]).execute()
                        with col4:
                         # Thêm nút xóa bài hát dưới phần switch public
                            delete_button = st.button(f"🗑️ Xóa", key=f"delete_{song['id']}")

                            if delete_button:
                                # Hiển thị hộp chọn xác nhận trước khi xóa
                                confirm_delete = st.selectbox(
                                    "Bạn có chắc chắn muốn xóa bài hát này?",
                                    ["Chắc chắn", "Không"]
                                )

                                if confirm_delete == "Chắc chắn":
                                    # Xóa bài hát khỏi Supabase (cả cơ sở dữ liệu SQL)
                                    supabase.table("songs").delete().eq("id", song["id"]).execute()

                                    # Thông báo thành công
                                    st.success(f"Bài hát '{song['title']}' đã được xóa thành công.")
                                    
                                    # Làm mới lại danh sách bài hát sau khi xóa
                                    songs = supabase.table("songs").select("*").eq("user_id", user_id).execute()
                                    st.rerun()  # Tải lại trang để làm mới danh sách

                    with col2:

                        #render_music_player(song['title'], song['audio_url'], song['image_url'])
                        
                        # Giả sử song['prompt'] là một chuỗi dà

                        st.write(f"⏱ Duration: {song['duration']} seconds")
                        st.write(f"🎧 Model: {song['model_name']}")
                        st.write(f"🗓 Created at: {song['created_at']}")
                    st.markdown("---")
            else:
                st.info("🎵 Bạn chưa có bài hát nào.")
        else:
            st.error("❌ Không tìm thấy thông tin người dùng.")
    else:
        st.warning("🔒 Vui lòng đăng nhập để xem thư viện của bạn.")
