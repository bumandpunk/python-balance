import cv2
import time
import requests
import base64
from datetime import datetime

# 全局变量存储用户输入和二维码内容
user_input = None
scanned_qr_code = None

def fetch_token(user_input, image_base64, face_base64, qr_data):
    url = 'https://os.cajob.cloud/auth/oauth/token?randomStr=blockPuzzle&code=&grant_type=password'
    headers = {
        'accept': 'application/json',
        'authorization': 'Basic cGlnOnBpZw==',
        'content-type': 'application/x-www-form-urlencoded',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data = {
        'username': 'im0204',
        'password': 'JFat0Zdc'
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token = response.json().get('access_token')
        if token:
            add_data(token, user_input, image_base64, face_base64, qr_data)
        else:
            print('Failed to fetch token: No access token returned.')
    except requests.RequestException as e:
        print(f'Error fetching token: {e}')

def add_data(token, user_input, image_base64, face_base64, qr_data):
    url = 'https://os.cajob.cloud/fd/formInstance'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
        "img_base64": image_base64,
        "templateId": "1848003481851305984",
        "qrcode": qr_data,
        "weight": user_input,
        "face_base64": face_base64
    }
    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        print('Data successfully sent to the backend.')
    except requests.RequestException as e:
        print(f'Error sending data to the backend: {e}')

def capture_single_photo(camera):
    """
    用于通过摄像头拍照并将其转换为 Base64 编码
    """
    if not camera.isOpened():
        print("Camera not opened for capture.")
        return None

    # 丢弃旧帧，确保捕获的是最新帧
    for _ in range(5):
        ret, frame = camera.read()
        if not ret:
            print("Failed to read frame from camera.")
            return None

    # 获取当前时间
    fixed_text = 'Xthings'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watermark_text = f"{fixed_text} {current_time}"

    # 设置水印位置
    text_size, _ = cv2.getTextSize(watermark_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    text_x = frame.shape[1] - text_size[0] - 10  # 距右上角10px
    text_y = text_size[1] + 10  # 距上方10px

    # 绘制水印
    cv2.putText(frame, watermark_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        photo_base64 = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
        print("Photo captured and converted to Base64.")
        return photo_base64
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def process_input(input_data):
    """
    判断输入数据是数字还是二维码，并存储到相应的变量中
    """
    global user_input, scanned_qr_code
    input_data = input_data.strip()
    
    if input_data.isdigit():  # 如果是数字
        user_input = int(input_data)
        print(f"Number entered: {user_input}")
    else:  # 如果不是数字，则认为是二维码
        scanned_qr_code = input_data
        print(f"QR code scanned: {scanned_qr_code}")

def start_capture(camera1, camera3):
    """
    启动摄像头操作：一个摄像头用于拍照，另一个摄像头用于人脸拍照
    """
    global user_input, scanned_qr_code

    # 拍摄单张照片并转换为 Base64
    image_base64 = capture_single_photo(camera1)
    if not image_base64:
        print("Failed to capture image, stopping.")
        return

    face_base64 = capture_single_photo(camera3)
    if not face_base64:
        print("Failed to capture face image, stopping.")
        return

    # 将数据传递给后台
    fetch_token(user_input, image_base64, face_base64, scanned_qr_code)

def main():
    global user_input, scanned_qr_code

    # 主程序
    camera1 = cv2.VideoCapture('/dev/video2')  # 摄像头 1 用于拍照
    camera3 = cv2.VideoCapture('/dev/video1')  # 摄像头 3 用于人脸拍照

    # 设置摄像头帧率，确保帧速足够快
    camera1.set(cv2.CAP_PROP_FPS, 60)
    camera3.set(cv2.CAP_PROP_FPS, 30)

    # 检查摄像头是否成功打开
    if not camera1.isOpened():
        print("Unable to open camera 1 for capturing photo.")
        return
    if not camera3.isOpened():
        print("Unable to open camera 3 for face capture.")
        return

    # 主循环：等待用户输入和扫码枪扫描
    while True:
        try:
            input_data = input("Please enter a number or scan the QR code (end with Enter): ")
            process_input(input_data)  # 处理输入数据

            # 当数字和二维码内容都已填充时，开始拍照
            if user_input is not None and scanned_qr_code is not None:
                start_capture(camera1, camera3)
                # 重置输入状态，准备下一次操作
                user_input, scanned_qr_code = None, None

        except KeyboardInterrupt:
            print("Program terminated by user.")
            break

    # 释放摄像头资源
    camera1.release()
    camera3.release()

if __name__ == "__main__":
    main()
