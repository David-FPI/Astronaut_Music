import requests
import json

def test_suno_api(api_token):
    # URL của API Suno (cập nhật URL nếu cần)
    api_url = "https://apibox.erweima.ai/api/v1/generate"

    # Header yêu cầu, bao gồm api_token cho phép truy cập API
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Dữ liệu mà bạn muốn gửi trong yêu cầu POST
    data = {
        "prompt": "Create a relaxing piano melody.",
        "style": "Classical",  # Thể loại nhạc
        "title": "Relaxing Piano",  # Tên bài hát
        "customMode": False,
        "instrumental": True,  # Tạo nhạc không lời
        "model": "V3_5",
        "callBackUrl": "https://api.example.com/callback"  # Thay bằng URL callback thực tế nếu cần
    }

    # Gửi yêu cầu POST tới API
    response = requests.post(api_url, headers=headers, json=data)

    # Kiểm tra phản hồi từ API
    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json.get("data"):
                print("Task ID:", response_json["data"].get("taskId"))
                print("API Response:", json.dumps(response_json, indent=2))
            else:
                print("Không có dữ liệu trong phản hồi.")
                print("Lỗi từ API:", response_json.get("msg"))
        except ValueError as e:
            print(f"🚨 Lỗi khi phân tích JSON: {e}")
            print("API Response:", response.text)
    else:
        print(f"🚨 Lỗi khi gửi yêu cầu tới API: {response.status_code}")
        print("API Response:", response.text)

# Thử test API Suno với api_token của bạn
api_token = "2d551602f3a39d8f3e219db2c94d7659"
test_suno_api(api_token)
