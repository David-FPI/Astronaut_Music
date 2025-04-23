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

def  manage_payment():
        
    # MoMo config
    MOMO_CONFIG = {
        "MomoApiUrl": "https://test-payment.momo.vn/v2/gateway/api/create",
        "PartnerCode": "MOMO",
        "AccessKey": "F8BBA842ECF85",
        "SecretKey": "K951B6PE1waDMi640xX08PD3vg6EkVlz",
        "ReturnUrl": "https://aimusic-fvj4bjxfbumlktejiy6gb4.streamlit.app/",
        "IpnUrl": "https://webhook.site/b052aaf4-3be0-43c5-8bad-996d2d0c0e54",
        "RequestType": "captureWallet",
        "ExtraData": "Astronaut_Music_payment"
    }

    @st.cache_data(ttl=86400)
    def get_usd_to_vnd():
        try:
            url = "https://v6.exchangerate-api.com/v6/5bfc9ccf0ed4b1708159250f/latest/USD"
            res = requests.get(url)
            if res.status_code == 200:
                rate = res.json()["conversion_rates"]["VND"]
                return int(rate)
        except:
            st.error("❌  Error fetching exchange rate.")
        return 25000

    def generate_signature(data, secret_key):
        raw_signature = (
            f"accessKey={data['accessKey']}&amount={data['amount']}&extraData={data['extraData']}&"
            f"ipnUrl={data['ipnUrl']}&orderId={data['orderId']}&orderInfo={data['orderInfo']}&"
            f"partnerCode={data['partnerCode']}&redirectUrl={data['redirectUrl']}&"
            f"requestId={data['requestId']}&requestType={data['requestType']}"
        )
        return hmac.new(secret_key.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()


    st.title("💰 Payment")
    if "user" not in st.session_state:
        st.warning("🔐 Please log in.")
        st.stop()
    user_id = st.session_state["user"]["id"]
    usd_to_vnd = get_usd_to_vnd()
    # Lấy số dư hiện tại
    credit_data = supabase.table("user_credits").select("credits").eq("id", user_id).execute()
    credits = credit_data.data[0]["credits"] if credit_data.data else 0
    current_credits = credit_data.data[0]["credits"] if credit_data.data else 0
    st.markdown(f"""
    <div class="credit-container">
        <div class="credit-item">
            <div class="credit-info-row">
                <div class="cost-item">
                    <h3>{current_credits} Credits</h3>
                </div>
            </div>
            <div class="cost-container">
                <h2>💱 USD → VND Exchange Rate (ExchangeRate-API): {usd_to_vnd:,.0f}</h2>
                <p>Cost per generation</p>
                <div class="cost-items">
                    <div class="cost-item">
                        <h3>25</h3>
                        <p>Feel The Beat</p>
                    </div>
                    <div class="cost-item">
                        <h3>10</h3>
                        <p>Lyrics</p>
                    </div>
                    <div class="cost-item">
                        <h3>5</h3>
                        <p>Classify</p>
                    </div>
                </div>
            </div>
        </div>
    </div>                                      

    <style>
        .credit-container {{
            background: linear-gradient(to bottom right, #6a0dad, #00008b, #000000);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 10px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
            border: 5px solid #00b8ff;
            box-shadow: 0 0 20px 5px #00b8ff;
        }}

        .credit-item {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 10px;
        }}

        .credit-info-row {{
            display: flex;
            justify-content: center;
            margin-bottom: 15px;
        }}

        .cost-container {{
            color: white;
            font-size: 14px;
        }}

        .cost-container p {{
            text-align: center;
            margin-bottom: 8px;
            font-size: 20px;
            color: #F28500 !important;
        }}

        .cost-container h2 {{
            text-align: center;
            margin-bottom: 8px;
            font-size: 20px;
            color: #FF1C3B !important;
        }}

        .cost-items {{
            display: flex;
            justify-content: center;
            gap: 10px;
        }}

        .cost-item {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            flex: 1;
        }}

        .cost-item h3 {{
            color: #FFFF33 !important;
            font-size: 30px;
            margin-bottom: 6px;
        }}

        .cost-item p {{
            color: white !important;
            font-size: 18px;
            margin: 0;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Lấy số dư hiện tại
    credit_data = supabase.table("user_credits").select("credits").eq("id", user_id).execute()
    credits = credit_data.data[0]["credits"] if credit_data.data else 0
    current_credits = credit_data.data[0]["credits"] if credit_data.data else 0
    
    # Bảng giá
    st.subheader("📦 Credit Packages")
    
    packages = [
    {"name": "Basic", "price": 5, "credits": 1000, "discount": None},
    {"name": "Standard", "price": 50, "credits": 10000, "discount": None},
    {"name": "Premium", "price": 500, "credits": 105000, "discount": "Save 5%"},
    {"name": "Professional", "price": 1250, "credits": 275000, "discount": "Save 10%"},
    ]

    cols = st.columns(len(packages), gap="large")

    for i, (col, pack) in enumerate(zip(cols, packages)):
        with col:
            # Tính số lượng dựa vào credits
            musical_creations = pack["credits"] // 25
            lyrics_generations = pack["credits"] // 10

            included_html = f"""<div style='text-align: left;'>
            <h2><strong>This pack includes:</strong></h2>
            <h2>✅ {musical_creations:,} musical creations</h2>
            <h2>✅ {lyrics_generations:,} generations of lyrics</h2>
            </div>"""

            if pack["discount"]:
                package_html = f"""
                <div class="package highlight">
                    <div class="ribbon">{pack["discount"]}</div>
                    <h1>{pack['name']}</h1>
                    <h3>${pack['price']}</h3>
                    <p>{pack['credits']:,} Credits</p>
                    {included_html}
                </div>
                """
            else:
                package_html = f"""
                <div class="package">
                    <h1>{pack['name']}</h1>
                    <h3>${pack['price']}</h3>
                    <p>{pack['credits']:,} Credits</p>
                    {included_html}
                </div>
                """

            st.markdown(package_html, unsafe_allow_html=True)

            with st.form(f"form_{i}"):
                if st.form_submit_button("🛒Buy Credits"):
                    order_id = str(uuid.uuid4())
                    request_id = str(uuid.uuid4())
                    price_vnd = int(pack["price"] * usd_to_vnd)
                    order_info = f"Mua {pack['credits']} credits cho user {user_id}"                  
                    payload = {
                        "partnerCode": MOMO_CONFIG["PartnerCode"],
                        "accessKey": MOMO_CONFIG["AccessKey"],
                        "requestId": request_id,
                        "amount": str(price_vnd),
                        "orderId": order_id,
                        "orderInfo": order_info,
                        "redirectUrl": MOMO_CONFIG["ReturnUrl"],
                        "ipnUrl": MOMO_CONFIG["IpnUrl"],
                        "extraData": MOMO_CONFIG["ExtraData"],
                        "requestType": MOMO_CONFIG["RequestType"]
                    }
                    payload["signature"] = generate_signature(payload, MOMO_CONFIG["SecretKey"])

                    res = requests.post(MOMO_CONFIG["MomoApiUrl"], json=payload)
                    if res.status_code == 200 and res.json().get("payUrl"):
                        pay_url = res.json()["payUrl"]
                        supabase.table("pending_payments").insert({
                            "user_id": user_id,
                            "order_id": order_id,
                            "credits": pack["credits"],
                            "amount": price_vnd
                        }).execute()

                        st.success("✅ Order created. Click the button below to pay.")
                        st.markdown(f"""
                            <a href="{pay_url}" target="_blank">
                                <button style="background-color:#f72585; color:white; padding:10px 20px;
                                               border:none; border-radius:5px; cursor:pointer;">
                                    🚀 Open MoMo to pay
                                </button>
                            </a>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to create order. Please try again.")

    st.markdown("<hr>", unsafe_allow_html=True)
    # CSS đẹp
    st.markdown("""
        <style>
        .package h1 {
            font-size: 1.4rem !important;
            margin-bottom: 0.33rem;
            color: #FF1493 !important;
        }

        .package.highlight h1 {
            font-size: 1.4rem !important;
            margin-bottom: 0.3rem;
            color:  #FF1493 !important;
            
        }
        
        .package h2{
            font-size: 0.8rem !important;
            margin-bottom: 0.3rem;
            color: #CCCCCC !important;
        }
        .package h3{
                font-size: 2.7rem !important;
            color: #FFFF33 !important;}
        .package p {
            color: #FFA500 !important;
                font-size: 1.4rem !important;
        }

        
        .package.highlight h2{
            font-size: 0.8rem !important;
            margin-bottom: 0.3rem;
            color: #CCCCCC !important;
        }
        .package.highlight h3{
                font-size: 2.7rem !important;
            color: #FFFF33 !important;}
        .package.highlight p {
            color: #FFA500 !important;
                font-size: 1.4rem !important;
        }

        .package {
            position: relative;
            background: linear-gradient(to right, #0f4c81, #4b2c83) !important;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            color: #FFD700 !important;
            transition: 0.3s;
            border: 5px solid #00b8ff;
            box-shadow: 0 0 20px 5px #00b8ff;

        }
        .package.highlight {
            background: linear-gradient(to bottom right, #4B0082, #000000) !important;
            color: #ffffff;
        }
        
        .ribbon {
            width: 80px;
            background: linear-gradient(to right, #1A237E, #4A148C) !important;;
            color: #FFB300;
            font-weight: bold;
            text-align: center;
            font-size: 0.7rem;
            position: absolute;
            right: -25px;
            top: 10px;
            transform: rotate(45deg);
            padding: 3px 0;
        }

        </style>
    """, unsafe_allow_html=True)

    

    # ✅ Xử lý khi quay lại từ MoMo qua ReturnUrl
    params = st.query_params
    order_id_param = params.get("orderId")
    result_code = params.get("resultCode")
    trans_id = params.get("transId")
    amount = int(params.get("amount", "0"))

    if order_id_param:
        exists = supabase.table("payment_history").select("*").eq("order_id", order_id_param).execute()
        if exists.data:
            st.info("Transaction already processed.")
        else:
            pending = supabase.table("pending_payments").select("*").eq("order_id", order_id_param).execute().data
            if pending:
                pending = pending[0]
                if result_code == "0":
                    supabase.table("user_credits").update({"credits": credits + pending["credits"]}).eq("id", user_id).execute()
                    supabase.table("payment_history").insert({
                        "user_id": user_id,
                        "order_id": order_id_param,
                        "amount": amount,
                        "credits": pending["credits"],
                        "status": "completed",
                        "payment_method": "momo",
                        "transaction_id": trans_id,
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    supabase.table("pending_payments").delete().eq("order_id", order_id_param).execute()
                    st.success(f"✅ Added {pending['credits']:,} credits.")
                    st.rerun()
                else:
                    st.warning("❌ Payment failed or cancelled.")
    
    st.markdown("## 🧾 Transaction History (last 3 months)")

    # user_id = st.session_state['user']['id']
    three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()

    # Lấy dữ liệu từ Supabase
    history = supabase.table("payment_history").select("*") \
        .eq("user_id", user_id).gte("created_at", three_months_ago) \
        .order("created_at", desc=True).execute()

    if history.data:
        df = pd.DataFrame(history.data)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y %H:%M')
        df_display = df[['order_id', 'amount', 'credits', 'status', 'payment_method', 'transaction_id', 'created_at']]

        st.dataframe(df_display, use_container_width=True, height=220)
    else:
        st.info("No transactions in the last 3 months.")
    # ✅ Trường hợp không có orderId → Kiểm tra đơn pending chưa xác nhận
    if not order_id_param:
        pending_query = supabase.table("pending_payments").select("*").eq("user_id", user_id).execute()
        pending_data = pending_query.data[0] if pending_query.data else None


