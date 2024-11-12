import serial
import time
import cv2
import requests
import base64
from datetime import datetime

# 全局变量
user_weight = None
scanned_qr_code = None
# 全局变量
token_info = {
    'access_token': None,
    'expires_at': 0  # 时间戳，表示 Token 的过期时间
}


# 认证码（扫描此码开始工作）
# AUTH_CODE = "https://zwjy.ziway.com.cn/scan-code?short-chain=/qOWcQu9n7y"  # 请替换为您的认证码内容

# 串口相关函数
def open_serial(port='/dev/ttyUSB0', baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        if ser.is_open:
            print(f"Serial port {port} opened successfully.")
        else:
            print(f"Failed to open serial port {port}.")
        return ser
    except serial.SerialException as e:
        print(f"Serial exception: {e}")
        return None

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
def get_valid_token():
    current_time = time.time()
    if token_info['access_token'] and token_info['expires_at'] > current_time:
        # Token 有效，直接返回
        return token_info['access_token']
    else:
        # Token 不存在或已过期，重新获取
        return fetch_token()

# 获取 token
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
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 3600)  # 获取 Token 的有效期，默认为3600秒（1小时）
        # 计算 Token 的过期时间
        expires_at = time.time() + expires_in - 60  # 提前60秒刷新 Token
        # 更新全局 Token 信息
        token_info['access_token'] = access_token
        token_info['expires_at'] = expires_at
        return access_token
    except requests.RequestException as e:
        print(f'Error fetching token: {e}')
        return None

# 获取称重阈值
def get_threshold_values():
    token = get_valid_token()
    if not token:
        print("Cannot fetch threshold values without a valid token.")
        return None, None
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
        records = response.json().get('data', {}).get('records', [])
        for item in records:
            if item.get('a173036328345917519') == '称重程序':
                standard_value = float(item['standard_value'])
                tolerance = float(item['positive_negative_value'])
                return standard_value, tolerance
        print("No threshold values found.")
        return None, None
    except requests.RequestException as e:
        print(f'Error fetching threshold values: {e}')
        return None, None

# 拍照函数
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

    cv2.putText(frame, watermark_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 2)
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        photo_base64 = 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
        print("Photo captured and converted to Base64.")
        return photo_base64
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

# 上传数据
def add_data(token, weight_value, image_base64, face_base64, qr_data):
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
        "weight": weight_value,
        "face_base64": face_base64
    }
    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        print('Data successfully sent to the backend.')
        return True
    except requests.RequestException as e:
        print(f'Error sending data to the backend: {e}')
        return False

# 主程序
def main():
    # 初始化串口和摄像头
    ser = open_serial(port='/dev/ttyUSB0', baudrate=9600)
    if not ser:
        return

    # 设置最大尝试次数
    max_attempts = 3

    # 初始化摄像头1
    attempt = 0
    while attempt < max_attempts:
        camera1 = cv2.VideoCapture('/dev/v4l/by-id/usb-Generic_HBCJ_Camera_200901010001-video-index0')
        if camera1.isOpened():
            print("Camera 1 opened successfully.")
            break
        else:
            print(f"Attempt {attempt + 1} to open Camera 1 failed.")
            camera1.release()
            attempt += 1
            time.sleep(1)  # 等待1秒后重试

    if not camera1.isOpened():
        print("Unable to open Camera 1 after multiple attempts.")
        return

    # 初始化摄像头2
    attempt = 0
    while attempt < max_attempts:
        camera2 = cv2.VideoCapture('/dev/v4l/by-id/usb-DR-MX200C_DR-MX200C_342621-video-index0')
        if camera2.isOpened():
            print("Camera 2 opened successfully.")
            break
        else:
            print(f"Attempt {attempt + 1} to open Camera 2 failed.")
            camera2.release()
            attempt += 1
            time.sleep(1)  # 等待1秒后重试

    if not camera2.isOpened():
        print("Unable to open Camera 2 after multiple attempts.")
        return

    standard_value, tolerance = get_threshold_values()
    if standard_value is None or tolerance is None:
        print("Failed to get threshold values. Exiting.")
        return

    try:
        while True:
            # 初始化状态变量
            weight_value = None
            qr_data = None
            weight_in_range = True  # 初始设为 True，后续可能修改

            # 循环等待输入，直到获取到重量值和二维码数据
            while weight_value is None or qr_data is None:
                user_input = input("Please enter the weight value or scan the QR code: ").strip()
                # 判断输入内容是重量值还是二维码数据
                try:
                    # 尝试将输入转换为浮点数，如果成功，则认为是重量值
                    weight_value = float(user_input)
                    print(f"Weight value received: {weight_value}")
                except ValueError:
                    # 如果转换失败，认为是二维码数据
                    if user_input:
                        qr_data = user_input
                        print(f"QR code data received: {qr_data}")
                    else:
                        print("Empty input, please try again.")

            # 检查重量是否在阈值范围内
            lower_limit = standard_value - tolerance
            upper_limit = standard_value + tolerance
            if not (lower_limit <= weight_value <= upper_limit):
                weight_in_range = False  # 不满足条件
                print("Weight is out of range.")
            else:
                print("Weight is within the acceptable range.")

            # 拍摄两张照片
            image_base64 = capture_single_photo(camera1)
            face_base64 = capture_single_photo(camera2)
            if not image_base64 or not face_base64:
                print("Failed to capture photos.")
                weight_in_range = False  # 不满足条件

             # 根据条件闪烁灯光
            if weight_in_range:
                green_light_blink(ser)
            else:
                red_light(ser)
            time.sleep(2)
            turn_off_light(ser)

            # 上传数据
            token = get_valid_token()
            add_data(token, weight_value, image_base64, face_base64, qr_data)
                # if not data_sent:
                #     weight_in_range = False  # 不满足条件

            print("Process completed. Ready for the next cycle.\n")

    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # 释放资源
        close_serial(ser)
        camera1.release()
        camera2.release()

if __name__ == "__main__":
    main()