import serial
import time
import cv2
import requests
import base64
from datetime import datetime

# 全局变量
user_input = None
scanned_qr_code = None
current_program = None  # 当前运行的程序

# 程序标识
WEIGHING_URL = "https://zwjy.ziway.com.cn/scan-code?short-chain=/nywHyitYCh"   # 称重程序
EVIDENCE_URL = "https://zwjy.ziway.com.cn/scan-code?short-chain=/qOWcQu9n7y"   # 取证程序

# 称重程序相关函数
def open_serial(port='/dev/ttyUSB0', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    if ser.is_open:
        print(f"Serial port {port} opened successfully.")
    else:
        print(f"Failed to open serial port {port}.")
    return ser

def red_light(ser):
    command = bytes.fromhex("01 06 00 C2 00 31 E9 E2")
    ser.write(command)
    print("Red light blinking.")

def green_light_blink(ser):
    command = bytes.fromhex("01 06 00 C2 00 33 68 23")
    ser.write(command)
    print("Green light slow blinking.")

def turn_off_light(ser):
    command = bytes.fromhex("01 06 00 C2 00 60 28 1E")
    ser.write(command)
    print("Light turned off.")

def close_serial(ser):
    ser.close()
    print("Serial port closed.")

def check_value(ser, user_value, standard_value, tolerance):
    lower_limit = standard_value - tolerance  # 150
    upper_limit = standard_value + tolerance  # 250

    if user_value < lower_limit or user_value > upper_limit:
        red_light(ser)  # 超出范围，红灯爆闪
    else:
        green_light_blink(ser)  # 正常范围内，绿灯慢闪烁

# 取证程序相关函数
def fetch_token_and_send(user_input, image_base64, face_base64, qr_data,ser):
    token = fetch_token()
    if token:
        add_data(token, user_input, image_base64, face_base64, qr_data,ser)
    else:
        print("Cannot send data without a valid token.")
#获取token并返回
def fetch_token():
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
        return token
    except requests.RequestException as e:
        print(f'Error fetching token: {e}')
def add_data(token, user_input, image_base64, face_base64, qr_data,ser):
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
        # 称重+拍照完成后，绿灯慢闪烁
        green_light_blink(ser)
        time.sleep(1)
        turn_off_light(ser)
        print('Data successfully sent to the backend.')
    except requests.RequestException as e:
        print(f'Error sending data to the backend: {e}')
        red_light(ser)
        time.sleep(1)
        turn_off_light(ser)

#获取称重程序阈值
def get_data():
    token = fetch_token()
    url = 'https://os.cajob.cloud/fd/formInstance/page'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
       "templateId":"1850929236043276288",
       "current":1,
       "size":10,
       "queryFieldList":[],
       "queryDefaultRecordCondition":[],
       "orders":[]
    }
    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        if response.status_code == 200:
            records = response.json().get('data', {}).get('records', [])
        if records:
            return [{'标准值': float(item['standard_value']), '浮动值': float(item['positive_negative_value'])} for item in records if item['a173036328345917519'] == '称重程序']
    
    except requests.RequestException as e:
        print(f'Error sending data to the backend: {e}')
def capture_single_photo(camera):
    if not camera.isOpened():
        print("Camera not opened for capture.")
        return None

    for _ in range(5):
        ret, frame = camera.read()
        if not ret:
            print("Failed to read frame from camera.")
            return None

    fixed_text = 'Xthings'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watermark_text = f"{fixed_text} {current_time}"

    text_size, _ = cv2.getTextSize(watermark_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    text_x = frame.shape[1] - text_size[0] - 10
    text_y = text_size[1] + 10

    cv2.putText(frame, watermark_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        photo_base64 = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
        print("Photo captured and converted to Base64.")
        return photo_base64
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def process_input(input_data, ser, camera1, camera3):
    global user_input, scanned_qr_code, current_program,standard_value,positive_negative_value

    input_data = input_data.strip()

    # 检查是否是程序切换的URL
    if input_data == WEIGHING_URL:
        current_program = 'weighing'
        #如果是称重码 调用接口查询称重阈值，，
        data = get_data()
        if data:
            standard_value = data[0]['标准值']
            positive_negative_value = data[0]['浮动值']
        print("Switched to weighing program.")
        return
    elif input_data == EVIDENCE_URL:
        current_program = 'evidence'
        print("Switched to evidence collection program.")
        return

    # 根据当前程序处理输入
    if current_program == 'weighing':
        try:
            weight_value = float(input_data)
            check_value(ser, weight_value,standard_value,positive_negative_value)
            time.sleep(2)
            turn_off_light(ser)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    elif current_program == 'evidence':
        try:
            # 尝试将输入数据转换为浮点数
            user_input = float(input_data)
            print(f"Number entered: {user_input}")
        except ValueError:
            # 如果转换失败，则认为是二维码
            scanned_qr_code = input_data
            print(f"QR code scanned: {scanned_qr_code}")

        # 当数字和二维码内容都已填充时，开始拍照
        if user_input is not None and scanned_qr_code is not None:
            start_capture(camera1, camera3,ser)
            # 重置输入状态，准备下一次操作
            user_input, scanned_qr_code = None, None
    else:
        print("Please enter a valid program URL to start (weighing or evidence collection).")

def start_capture(camera1, camera3,ser):
    global user_input, scanned_qr_code

    image_base64 = capture_single_photo(camera1)
    if not image_base64:
        print("Failed to capture image, stopping.")
        return

    face_base64 = capture_single_photo(camera3)
    if not face_base64:
        print("Failed to capture face image, stopping.")
        return

    fetch_token_and_send(user_input, image_base64, face_base64, scanned_qr_code,ser)

def main():
    global current_program

    # 初始化串口和摄像头
    ser = open_serial(port='/dev/ttyUSB0', baudrate=9600)

    camera1 = cv2.VideoCapture('/dev/v4l/by-id/usb-Generic_HBCJ_Camera_200901010001-video-index0')
    camera3 = cv2.VideoCapture('/dev/v4l/by-id/usb-DR-MX200C_DR-MX200C_342621-video-index0')

    camera1.set(cv2.CAP_PROP_FPS, 60)
    camera3.set(cv2.CAP_PROP_FPS, 30)

    if not camera1.isOpened():
        print("Unable to open camera 1 for capturing photo.")
    if not camera3.isOpened():
        print("Unable to open camera 3 for face capture.")

    try:
        while True:
            input_data = input("Please enter input (program URL or other content): ")
            process_input(input_data, ser, camera1, camera3)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # 释放资源
        close_serial(ser)
        camera1.release()
        camera3.release()

if __name__ == "__main__":
    main()
