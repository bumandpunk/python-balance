import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time
import threading
import requests
import base64
from datetime import datetime

def fetch_token(user_input, image_path,face_base64, qr_data):
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
            add_data(token, user_input, image_path,face_base64, qr_data)
        else:
            print('Failed to fetch token: No access token returned.')
    else:
        print('Error fetching token:', response.text)

def add_data(token, user_input, image_path,face_base64, qr_data):
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
        "qrcode": ', '.join(qr_data),
        "weight": user_input,
        "face_base64": face_base64
    }
    response = requests.post(url, headers=headers, json=data_payload)
    if response.status_code == 200:
        print('Data successfully sent to the backend.')
    else:
        print('Error sending data to the backend:', response.text)

def capture_single_photo(camera):
    """
    用于通过摄像头拍照并将其转换为 Base64 编码
    """
    if not camera.isOpened():
        print("Camera not opened for capture")
        return None

    # 丢弃旧帧，确保捕获的是最新帧
    for _ in range(5):
        camera.read()

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


def capture_and_decode_qrcode(camera, stop_event):
    """
    持续使用摄像头检测多个二维码，直到用户停止或检测到二维码。
    """
    print("Scanning QR codes...")

    qr_data_set = set()  # 使用集合来存储二维码数据，防止重复

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
                qr_data = obj.data.decode("utf-8")
                if qr_data not in qr_data_set:  # 确保不重复添加
                    qr_data_set.add(qr_data)
                    print("QR code detected:", list(qr_data_set))  # 转换为列表以打印输出

        if len(qr_data_set) > 0:
            stop_event.set()  # 检测到二维码后停止检测

        time.sleep(0.1)  # 控制帧率，减少处理负载

    return list(qr_data_set)  # 返回所有去重后的二维码



def start_capture(camera1, camera3, user_input):
    """
    启动摄像头操作：一个摄像头用于拍照+二维码识别，另一个摄像头用于人脸拍照
    """
    # 拍摄单张照片并转换为 Base64
    image_base64 = capture_single_photo(camera1)
    face_base64 = capture_single_photo(camera3)
    if not image_base64:
        print("Failed to capture image, stopping.")
        return

    # 创建停止事件
    stop_event1 = threading.Event()

    # 使用 camera1 进行二维码识别
    qr_data_list = capture_and_decode_qrcode(camera1, stop_event1)

    if qr_data_list:
        # 将检测到的二维码列表传递给后台
        fetch_token(user_input, image_base64, face_base64, qr_data_list)
    else:
        print("Failed to detect QR codes, no request sent.")




def main():
   # 主程序
    camera1 = cv2.VideoCapture(0)  # 摄像头 1 用于拍照+二维码识别
    camera3 = cv2.VideoCapture(2)  # 摄像头 3 用于人脸拍照

    # 设置摄像头帧率，确保帧速足够快
    camera1.set(cv2.CAP_PROP_FPS, 60)  # 设置帧率为30
    camera3.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率为30

    # 检查摄像头是否成功打开
    if not camera1.isOpened():
        print("Unable to open camera 1 for capturing photo.")
        return
    if not camera3.isOpened():
        print("Unable to open camera 3 for face capture.")
        return

    # 主循环：持续等待用户输入
    while True:
        try:
            user_input = int(input("Please enter a number and press Enter to start: "))
            print(f"Starting capture with input: {user_input}")
            start_capture(camera1, camera3, user_input)
        except ValueError:
            print("Invalid input, please enter a valid number.")
        except KeyboardInterrupt:
            print("Program terminated by user.")
            break

    # 释放摄像头资源
    camera1.release()
    camera3.release()
    

# 主入口
if __name__ == "__main__":
    main()
