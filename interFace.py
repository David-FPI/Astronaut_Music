import streamlit as st
st.set_page_config(page_title="Music AI Website", layout="wide")
import os
import bcrypt
import re  # Thêm thư viện kiểm tra email hợp lệ
from openai import OpenAI
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
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Flatten, Dropout, Dense, Activation)
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
from home import show_home
from create_lyrics import create_lyrics
from feel_the_beat import Feel_The_Beat
from classify import classify_music
from library import show_library
from payment import manage_payment

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

# Cấu hình logging - Lưu các lỗi vào file 'app.log'
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(message)s')
# # Mô phỏng toggle switch bằng checkbox
# toggle_state = st.checkbox("Enable feature")
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

# Hàm ghi lỗi vào log
def log_error(message):
    """Ghi lỗi vào file log và hiển thị thông báo lỗi cho người dùng."""
    logging.error(message)  # Ghi lỗi vào file log
    st.error(f"🚨 Lỗi xảy ra: {message}")  # Hiển thị lỗi cho người dùng

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

# CSS nâng cao cho giao diện
st.markdown(
    """
    <style>
        /* Thiết lập nền và font chữ chung */
        body, .stApp {
            # background: linear-gradient(135deg, #0E0808 0%, #1A1A1A 100%) !important;
            background: url("https://i.imgur.com/vzl5Tex.png") no-repeat center center fixed;
            background-size: cover !important;
            font-family: 'Roboto', sans-serif;
            color: #FFFFFF;
        }

        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            background: rgba(0, 0, 0, 0.1);
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #ff7e5f, #feb47b);
            border-radius: 10px;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: rgba(10, 10, 10, 0.8) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 5px 0 15px rgba(0, 0, 0, 0.2);
        }
        [data-testid="stSidebar"] .css-1d391kg {
            padding-top: 2rem;
        }
        
        /* Header styles */
        h1, h2, h3 {
            background: linear-gradient(90deg, #ff7e5f, #feb47b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        h2 {
            font-size: 1.8rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            
        }
        h3 {
            font-size: 1.4rem;
            color: white !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #ff7e5f, #feb47b);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 126, 95, 0.4);
        }
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 15px rgba(255, 126, 95, 0.6);
            background: linear-gradient(90deg, #feb47b, #ff7e5f);
        }
        .stButton > button:active {
            transform: translateY(1px);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: rgba(30, 30, 30, 0.6) !important;
            border: 1px solid rgba(255, 126, 95, 0.3) !important;
            border-radius: 8px !important;
            color: white !important;
            padding: 12px !important;
            transition: all 0.3s ease;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #ff7e5f !important;
            box-shadow: 0 0 0 2px rgba(255, 126, 95, 0.2) !important;
        }
        
        /* File uploader */
        .stFileUploader > div > button {
            background: linear-gradient(90deg, #ff7e5f, #feb47b);
            color: white;
        }
        .stFileUploader > div {
            border: 2px dashed rgba(255, 126, 95, 0.5);
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Audio player */
        audio {
            width: 100%;
            border-radius: 30px;
            background-color: rgba(40, 40, 40, 0.8);
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
        }
        audio::-webkit-media-controls-panel {
            background: linear-gradient(45deg, #333333, #1A1A1A);
        }
        audio::-webkit-media-controls-play-button {
            background-color: #ff7e5f;
            border-radius: 50%;
        }
        audio::-webkit-media-controls-timeline,
        audio::-webkit-media-controls-volume-slider {
            background: linear-gradient(90deg, #ff7e5f, #feb47b);
            border-radius: 15px;
            height: 4px;
        }
        
        /* Music card styling */
        .music-card {
            background: rgba(30, 30, 30, 0.7);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #ff7e5f;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        .music-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        /* Toggle switch */
        .css-16h7emx {
            color: rgba(250, 250, 250, 0.8) !important;
        }
        
        /* Radio buttons and checkboxes */
        .stRadio > div[role="radiogroup"] > label,
        .stCheckbox > label {
            color: white !important;
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-top-color: #ff7e5f !important;
        }
        
        /* Section dividers */
        hr {
            border: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 126, 95, 0.5), transparent);
            margin: 2rem 0;
        }
        
        /* Status messages */
        .stAlert {
            background-color: rgba(30, 30, 30, 0.7) !important;
            border-left: 4px solid;
            border-radius: 8px;
        }
        .element-container:has(.stAlert) {
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Menu styling for option menu */
        .nav-link {
            margin: 5px 0 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        .nav-link:hover {
            background-color: rgba(255, 126, 95, 0.2) !important;
        }
        .nav-link-selected {
            background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
            box-shadow: 0 4px 10px rgba(255, 126, 95, 0.4) !important;
        }
        
        /* Custom animations */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .pulse-effect {
            animation: pulse 2s infinite;
        }
        
        /* Custom containers for sections */
        .custom-container {
            background: rgba(30, 30, 30, 0.7);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(255, 126, 95, 0.2);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            background: linear-gradient(90deg, #ff7e5f, #feb47b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        [data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.8) !important;
        }
        
        /* Info box */
        .info-box {
            background: rgba(255, 126, 95, 0.1);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #ff7e5f;
            margin: 15px 0;
        }
        
        /* Glassmorphism elements */
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)
# # CSS nâng cao cho giao diện
# st.markdown(
#     """
#     <style>
#         /* Thiết lập nền và font chữ chung */
#         body, .stApp {
#             # background: linear-gradient(135deg, #0E0808 0%, #1A1A1A 100%) !important;
#             background: url("https://i.imgur.com/vzl5Tex.png") no-repeat center center fixed;
#             background-size: cover !important;
#             font-family: 'Roboto', sans-serif;
#             color: #FFFFFF;
#         }

        
#         /* Custom scrollbar */
#         ::-webkit-scrollbar {
#             width: 10px;
#             background: rgba(0, 0, 0, 0.1);
#         }
#         ::-webkit-scrollbar-thumb {
#             background: linear-gradient(45deg, #ff7e5f, #feb47b);
#             border-radius: 10px;
#         }
        
#         /* Sidebar styling */
#         [data-testid="stSidebar"] {
#             background: rgba(10, 10, 10, 0.8) !important;
#             backdrop-filter: blur(10px);
#             border-right: 1px solid rgba(255, 255, 255, 0.1);
#             box-shadow: 5px 0 15px rgba(0, 0, 0, 0.2);
#         }
#         [data-testid="stSidebar"] .css-1d391kg {
#             padding-top: 2rem;
#         }
        
#         /* Header styles */
#         h1, h2, h3 {
#             background: linear-gradient(90deg, #ff7e5f, #feb47b);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#             font-weight: 700;
#         }
#         h1 {
#             font-size: 2.5rem;
#             margin-bottom: 1.5rem;
#             text-align: center;
#         }
#         h2 {
#             font-size: 1.8rem;
#             margin-top: 2rem;
#             margin-bottom: 1rem;
#         }
#         h3 {
#             font-size: 1.4rem;
#         }
        
#         /* Button styling */
#         .stButton > button {
#             background: linear-gradient(90deg, #ff7e5f, #feb47b);
#             color: white;
#             border: none;
#             padding: 0.6rem 1.2rem;
#             border-radius: 50px;
#             font-weight: 600;
#             letter-spacing: 0.5px;
#             transition: all 0.3s ease;
#             box-shadow: 0 4px 15px rgba(255, 126, 95, 0.4);
#         }
#         .stButton > button:hover {
#             transform: translateY(-3px);
#             box-shadow: 0 7px 15px rgba(255, 126, 95, 0.6);
#             background: linear-gradient(90deg, #feb47b, #ff7e5f);
#         }
#         .stButton > button:active {
#             transform: translateY(1px);
#         }
        
#         /* Input fields */
#         .stTextInput > div > div > input,
#         .stTextArea > div > div > textarea {
#             background-color: rgba(30, 30, 30, 0.6) !important;
#             border: 1px solid rgba(255, 126, 95, 0.3) !important;
#             border-radius: 8px !important;
#             color: white !important;
#             padding: 12px !important;
#             transition: all 0.3s ease;
#         }
#         .stTextInput > div > div > input:focus,
#         .stTextArea > div > div > textarea:focus {
#             border-color: #ff7e5f !important;
#             box-shadow: 0 0 0 2px rgba(255, 126, 95, 0.2) !important;
#         }
        
#         /* File uploader */
#         .stFileUploader > div > button {
#             background: linear-gradient(90deg, #ff7e5f, #feb47b);
#             color: white;
#         }
#         .stFileUploader > div {
#             border: 2px dashed rgba(255, 126, 95, 0.5);
#             border-radius: 10px;
#             padding: 20px;
#         }
        
#         /* Audio player */
#         audio {
#             width: 100%;
#             border-radius: 30px;
#             background-color: rgba(40, 40, 40, 0.8);
#             box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
#         }
#         audio::-webkit-media-controls-panel {
#             background: linear-gradient(45deg, #333333, #1A1A1A);
#         }
#         audio::-webkit-media-controls-play-button {
#             background-color: #ff7e5f;
#             border-radius: 50%;
#         }
#         audio::-webkit-media-controls-timeline,
#         audio::-webkit-media-controls-volume-slider {
#             background: linear-gradient(90deg, #ff7e5f, #feb47b);
#             border-radius: 15px;
#             height: 4px;
#         }
        
#         /* Music card styling */
#         .music-card {
#             background: rgba(30, 30, 30, 0.7);
#             border-radius: 12px;
#             padding: 15px;
#             margin-bottom: 20px;
#             border-left: 4px solid #ff7e5f;
#             box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
#             transition: all 0.3s ease;
#         }
#         .music-card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
#         }
        
#         /* Toggle switch */
#         .css-16h7emx {
#             color: rgba(250, 250, 250, 0.8) !important;
#         }
        
#         /* Radio buttons and checkboxes */
#         .stRadio > div[role="radiogroup"] > label,
#         .stCheckbox > label {
#             color: white !important;
#         }
        
#         /* Loading spinner */
#         .stSpinner > div {
#             border-top-color: #ff7e5f !important;
#         }
        
#         /* Section dividers */
#         hr {
#             border: 0;
#             height: 1px;
#             background: linear-gradient(90deg, transparent, rgba(255, 126, 95, 0.5), transparent);
#             margin: 2rem 0;
#         }
        
#         /* Status messages */
#         .stAlert {
#             background-color: rgba(30, 30, 30, 0.7) !important;
#             border-left: 4px solid;
#             border-radius: 8px;
#         }
#         .element-container:has(.stAlert) {
#             animation: fadeIn 0.5s ease-in-out;
#         }
#         @keyframes fadeIn {
#             from { opacity: 0; transform: translateY(10px); }
#             to { opacity: 1; transform: translateY(0); }
#         }
        
#         /* Menu styling for option menu */
#         .nav-link {
#             margin: 5px 0 !important;
#             border-radius: 8px !important;
#             transition: all 0.3s ease !important;
#         }
#         .nav-link:hover {
#             background-color: rgba(255, 126, 95, 0.2) !important;
#         }
#         .nav-link-selected {
#             background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
#             box-shadow: 0 4px 10px rgba(255, 126, 95, 0.4) !important;
#         }
        
#         /* Custom animations */
#         @keyframes pulse {
#             0% { transform: scale(1); }
#             50% { transform: scale(1.05); }
#             100% { transform: scale(1); }
#         }
#         .pulse-effect {
#             animation: pulse 2s infinite;
#         }
        
#         /* Custom containers for sections */
#         .custom-container {
#             background: rgba(30, 30, 30, 0.7);
#             border-radius: 15px;
#             padding: 20px;
#             margin: 20px 0;
#             border: 1px solid rgba(255, 126, 95, 0.2);
#             box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
#         }
        
#         /* Metric styling */
#         [data-testid="stMetricValue"] {
#             font-size: 2.5rem !important;
#             background: linear-gradient(90deg, #ff7e5f, #feb47b);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#         }
#         [data-testid="stMetricLabel"] {
#             color: rgba(255, 255, 255, 0.8) !important;
#         }
        
#         /* Info box */
#         .info-box {
#             background: rgba(255, 126, 95, 0.1);
#             border-radius: 10px;
#             padding: 15px;
#             border-left: 4px solid #ff7e5f;
#             margin: 15px 0;
#         }
        
#         /* Glassmorphism elements */
#         .glass-effect {
#             background: rgba(255, 255, 255, 0.05);
#             backdrop-filter: blur(10px);
#             border-radius: 10px;
#             border: 1px solid rgba(255, 255, 255, 0.1);
#             box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
#         }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# Hàm mã hóa email
def encode_email(email):
    return base64.b64encode(email.encode()).decode()

# Hàm giải mã email
def decode_email(encoded):
    try:
        return base64.b64decode(encoded.encode()).decode()
    except Exception:
        return None

# SIDEBAR NAVIGATION
with st.sidebar:
    st.image("a-minimalist-logo-design-on-a-black-back.jpeg", use_container_width=True)

    # Xử lý đăng nhập với cookie
    cookies = CookieManager()

    # Kiểm tra cookies có sẵn và đã mã hóa email
    if cookies.ready() and cookies.get("user_email") and "user" not in st.session_state:
        decoded_email = decode_email(cookies.get("user_email"))
        if decoded_email:
            # 👉 Gọi Supabase để lấy thông tin đầy đủ từ email
            profile_data = supabase.table("user_profiles").select("*").eq("email", decoded_email).execute()
            if profile_data.data:
                profile = profile_data.data[0]
                st.session_state["user"] = {
                    "id": profile["id"],
                    "email": profile["email"],
                    "full_name": profile.get("full_name", ""),
                    "role": profile.get("role", "client"),
                    "created_at": profile.get("created_at", "")
                }

    # KHOẢNG TAI KHOẢN (AUTH)
    if "user" not in st.session_state:
        st.markdown("""
            <div class="custom-container" style="padding: 15px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; text-align: center;">
                    🔐 Tài khoản
                </h3>
        """, unsafe_allow_html=True)
        
        auth_menu = st.radio("", ["Đăng nhập", "Đăng ký", "Quên mật khẩu"], horizontal=True, label_visibility="collapsed")
        
        if auth_menu == "Đăng ký":
            st.markdown('<p style="font-weight: 600; font-size: 16px; margin-bottom: 10px;">✍️ Đăng ký tài khoản</p>', unsafe_allow_html=True)
            
            email = st.text_input("Email", type="default", placeholder="your.email@example.com")
            password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            full_name = st.text_input("Họ tên", placeholder="Nhập họ và tên của bạn")
            
            if st.button("🚀 Đăng ký"):
                from auth import register_user
                success, msg = register_user(email, password, full_name)
                if success:
                    st.success(msg)
                    st.info("📧 Vui lòng kiểm tra hộp thư để xác minh tài khoản trước khi đăng nhập.")
                else:
                    st.error(msg)

        elif auth_menu == "Đăng nhập":
            st.markdown('<p style="font-weight: 600; font-size: 16px; margin-bottom: 10px;">🔑 Đăng nhập</p>', unsafe_allow_html=True)
            
            email = st.text_input("Email đăng nhập", placeholder="your.email@example.com")
            password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            
            if st.button("🔓 Đăng nhập"):
                from auth import login_user
                success, msg = login_user(email, password)
                if success:
                    cookies["user_email"] = encode_email(email)
                    cookies["user_id"] = st.session_state["user"]["id"]
                    cookies.save()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif auth_menu == "Quên mật khẩu":
            st.markdown('<p style="font-weight: 600; font-size: 16px; margin-bottom: 10px;">📧 Đặt lại mật khẩu</p>', unsafe_allow_html=True)
            
            email = st.text_input("Nhập email đã đăng ký", placeholder="your.email@example.com")
            
            if st.button("Gửi email đặt lại mật khẩu"):
                from auth import supabase
                try:
                    res = supabase.auth.reset_password_for_email(email)
                    st.success("📬 Đã gửi email đặt lại mật khẩu. Vui lòng kiểm tra hộp thư đến.")
                except Exception as e:
                    st.error(f"❌ Lỗi khi gửi email: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # HIỂN THỊ THÔNG TIN NGƯỜI DÙNG ĐÃ ĐĂNG NHẬP
        full_name = st.session_state["user"].get("full_name", "bạn")
        
        # Lấy thông tin credits
        user_id = st.session_state["user"]["id"]
        credit_data = supabase.table("user_credits").select("credits").eq("id", user_id).execute()
        credits = credit_data.data[0]["credits"] if credit_data.data else 0
        
        st.markdown(f"""
            <div class="custom-container" style="padding: 15px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(45deg, #ff7e5f, #feb47b);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 10px;
                        font-weight: bold;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                        ">{full_name[0].upper()}</div>
                    <div>
                        <div style="font-weight: bold;">👋 {full_name}</div>
                        <div style="font-size: 0.9rem; opacity: 0.7;">{st.session_state["user"]["email"]}</div>
                    </div>
                </div>
                
            <div style="
                background: linear-gradient(45deg, rgba(255,126,95,0.2), rgba(254,180,123,0.2));
                padding: 10px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                margin-bottom: 15px;">
                <span style="font-size: 24px; margin-right: 10px;">💎</span>
                <div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Tín dụng hiện có</div>
                    <div style="font-weight: bold;">{credits:,} credits</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # if st.button("🚪 Đăng xuất", key="logout_button"):
        #     del cookies["user_email"]
        #     del st.session_state['user']
        #     cookies.save()
        #     st.success("✅ Đã đăng xuất.")
        #     st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title=None,
        options=["Home", "Create Lyrics", "Feel The Beat", "Classify", "Library", "Payment"],
        icons=["house", "music-note-list", "soundwave", "graph-up", "book", "credit-card"],
        menu_icon="menu-button-wide",
        default_index=0,
        styles={
            "container": {"background-color": "rgba(30,30,30,0.7)", "padding": "10px", "border-radius": "15px"},
            "icon": {"color": "#ff7e5f", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "color": "#ffffff", "text-align": "left", "margin": "5px", "border-radius": "8px", "padding": "10px"},
            "nav-link-selected": {"background": "linear-gradient(90deg, #ff7e5f, #feb47b)"},
        }
    )
    if "user" in st.session_state:
        if st.button("🚪 Đăng xuất", key="logout_button"):
            del cookies["user_email"]
            del st.session_state['user']
            cookies.save()
            st.success("✅ Đã đăng xuất.")
            st.rerun()

        
        # Hiển thị chatbot
        display_chatbot()


# 🚫 Chặn menu nếu chưa đăng nhập
protected_menus = ["Create Lyrics", "Feel The Beat", "Classify", "Explore", "Library","Quản lý thanh toán"]

if menu in protected_menus and "user" not in st.session_state:
    st.markdown("""
        <div class="custom-container" style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 60px; margin-bottom: 20px;">🔒</div>
            <h2 style="margin-bottom: 20px;">Vui lòng đăng nhập</h2>
            <p style="margin-bottom: 30px; color: rgba(255,255,255,0.7);">
                Bạn cần đăng nhập để truy cập chức năng này.
            </p>
            <div style="
                background: linear-gradient(45deg, rgba(255,126,95,0.2), rgba(254,180,123,0.2));
                padding: 15px;
                border-radius: 10px;
                max-width: 400px;
                margin: 0 auto;
                ">
                <p>👉 Sử dụng form đăng nhập ở menu bên trái để tiếp tục.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

def handle_empty_title(music_data):
    """Kiểm tra và điền tên bài hát nếu bị rỗng."""
    for song in music_data:
        if isinstance(song, dict):  # Kiểm tra xem song có phải là dictionary không
            # Kiểm tra nếu thiếu audioUrl hoặc imageUrl
            if not song.get('audioUrl'):
                song['audioUrl'] = "https://default-audio-url.com"  # Đặt URL mặc định nếu thiếu audioUrl
            if not song.get('imageUrl'):
                song['imageUrl'] = "https://default-image-url.com"  # Đặt URL mặc định nếu thiếu imageUrl

            # Kiểm tra nếu thiếu title
            if not song.get('title'):
                song['title'] = f"Track {song.get('id', 'Unknown')}"  # Đặt tên mặc định nếu không có title
                log_error(f"Bài hát với ID {song.get('id', 'Unknown')} thiếu title. Đặt tên mặc định.")
        else:
            log_error(f"Dữ liệu bài hát không hợp lệ: {song}")
    return music_data

# Xử lý logic theo lựa chọn trong menu
if menu == "Home":
    show_home()
elif menu == "Create Lyrics":
    create_lyrics()
elif menu == "Feel The Beat":
    asyncio.run(Feel_The_Beat()) 
elif menu == "Classify":
    classify_music()
elif menu == "Library":
    show_library()
elif menu == "Payment":
    manage_payment()
