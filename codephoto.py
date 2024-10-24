import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time
import threading
import requests
import base64

def fetch_token(user_input, image_path, qr_data):
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
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        if token:
            add_data(token, user_input, image_path, qr_data)
        else:
            print('Failed to fetch token: No access token returned.')
    else:
        print('Error fetching token:', response.text)

def add_data(token, user_input, image_path, qr_data):
    url = 'https://os.cajob.cloud/fd/formInstance'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
        "img_base64": image_path,
        "templateId": "1848003481851305984",
        "qrcode": qr_data,
        "weight": user_input
    }
    response = requests.post(url, headers=headers, json=data_payload)
    if response.status_code == 200:
        print('Data successfully sent to the backend.')
    else:
        print('Error sending data to the backend:', response.text)

def capture_single_photo(camera):
    """
    用于通过摄像头1拍照并将其转换为 Base64 编码
    """
    # 丢弃旧帧，确保捕获的是最新帧
    for _ in range(5):
        camera.read()

    ret, frame = camera.read()
    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        photo_base64 = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
        print("Photo captured and converted to Base64.")
        return photo_base64
    else:
        print("Failed to capture photo.")
        return None

def capture_and_decode_qrcode(camera, stop_event):
    """
    用于通过摄像头2识别二维码
    """
    print("Camera for QR code scanning started, waiting to detect QR code...")

    # 丢弃旧帧，确保捕获的是最新帧
    for _ in range(5):
        camera.read()

    while not stop_event.is_set():  # 持续识别二维码
        ret, frame = camera.read()

        if not ret:
            print("Failed to read data from camera.")
            continue

        # 转换为灰度图像并处理
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)

        try:
            decoded_objects = decode(binary_frame, symbols=[ZBarSymbol.QRCODE])
        except Exception as e:
            print(f"Decoding error: {e}")
            continue

        if decoded_objects:
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    qr_data = obj.data.decode("utf-8")
                    print("QR code detected:", qr_data)
                    stop_event.set()  # 成功识别到二维码后停止
                    return qr_data  # 返回识别到的二维码数据

        print("No QR code detected, continuing...")
        time.sleep(0.1)

    return None

def start_capture(camera1, camera2, user_input):
    """
    启动摄像头操作：一个拍照，一个二维码识别
    """
    # 拍摄单张照片并转换为 Base64
    image_base64 = capture_single_photo(camera1)
    if not image_base64:
        print("Failed to capture image, stopping.")
        return

    # 创建停止事件
    stop_event = threading.Event()

    # 启动二维码识别
    qr_data = capture_and_decode_qrcode(camera2, stop_event)
    if qr_data:
        fetch_token(user_input, image_base64, qr_data)
    else:
        print("Failed to detect QR code, no request sent.")

def main():
    # 主程序
    camera1 = cv2.VideoCapture('/dev/video1')  # 摄像头 1 用于拍照
    camera2 = cv2.VideoCapture('/dev/video4')  # 摄像头 2 用于二维码识别

    # 设置摄像头帧率，确保帧速足够快
    camera1.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率为30
    camera2.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率为30

    # 检查两个摄像头是否成功打开
    if not camera1.isOpened():
        print("Unable to open camera 1 for capturing photo.")
        return
    if not camera2.isOpened():
        print("Unable to open camera 2 for QR code recognition.")
        return

    # 主循环：持续等待用户输入
    while True:
        try:
            user_input = int(input("Please enter a number and press Enter to start: "))
            print(f"Starting capture with input: {user_input}")
            start_capture(camera1, camera2, user_input)
        except ValueError:
            print("Invalid input, please enter a valid number.")
        except KeyboardInterrupt:
            print("Program terminated by user.")
            break

    # 释放摄像头资源
    camera1.release()
    camera2.release()

# 主入口
if __name__ == "__main__":
    main()
