import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Hàm tạo chatbot trả lời cho người dùng
def chat_with_bot(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Hoặc "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý ảo giúp người dùng hiểu các tính năng của ứng dụng này."},
                {"role": "user", "content": message}
            ],
            temperature=0.8,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Lỗi khi kết nối API: {str(e)}"

# Hiển thị giao diện chat cho người dùng
st.title("💬 Trợ Lý Ảo - Hướng Dẫn Sử Dụng Ứng Dụng")

st.markdown("""
    Bạn có thể hỏi tôi về các tính năng của ứng dụng này. Ví dụ:
    - "Tạo lời bài hát là gì?"
    - "Cách phân loại thể loại nhạc như thế nào?"
    - "Cách thanh toán tín dụng?"
""", unsafe_allow_html=True)

# Nhập câu hỏi của người dùng
user_message = st.text_input("Nhập câu hỏi của bạn", "")

if user_message:
    # Chatbot trả lời
    bot_response = chat_with_bot(user_message)
    
    # Hiển thị câu trả lời từ chatbot
    st.markdown(f"**Trợ lý ảo:** {bot_response}")
