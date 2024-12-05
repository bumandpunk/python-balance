import serial
import time
import requests
from datetime import datetime
import cv2
import base64
# 全局变量
token_info = {
    'access_token': None,
    'expires_at': 0  # 时间戳，表示 Token 的过期时间
}

def parse_weight(message):
    """
    解析8字节消息并转换为重量数字。

    参数:
        message (str): 接收到的8字节消息，例如 '=000.100', '-199.400', '-100.10-'

    返回:
        float: 解析后的重量值，如果格式不正确则返回 None
    """
    if len(message) != 8:
        print(f"消息长度不正确: {message} (长度: {len(message)})")
        return None

    start_char = message[0]
    weight_data = message[1:7]  # 字节2-7
    end_char = message[7]

    # 反转重量数据
    reversed_weight_data = weight_data[::-1]

    # 合并重量字符串
    if start_char == '=':
        # 正数
        if end_char != '-':
            # 第8个字节是最高位数字，添加到重量字符串前
            weight_str = end_char + reversed_weight_data
            try:
                weight = float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
        else:
            print(f"正数但末位为'-'，数据异常: {message}")
            return None
    elif start_char == '-':
        # 负数
        if end_char == '-':
            # 第8个字节为'-'，确认负数
            weight_str = reversed_weight_data
            try:
                weight = -float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
        else:
            # 第8个字节是最高位数字，添加到重量字符串前
            weight_str = end_char + reversed_weight_data
            try:
                weight = -float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
    else:
        print(f"未知的起始符号: {start_char}")
        return None

def collect_weight_data():
    # 串口配置
    port = "/dev/ttyUSB0"  # 根据实际情况替换
    baudrate = 9600
    ser = serial.Serial(port, baudrate, timeout=0.1)  # 使用小超时快速读取数据

    last_recorded_weight = None  # 上一次记录的重量
    print("开始收集电子秤数据...")

    try:
        while True:
            current_second_data = []  # 当前1秒内的重量数据
            start_time = time.time()
            buffer = ""  # 缓冲区，用于存储未处理的接收数据

            # 收集1秒内的数据
            while time.time() - start_time < 1:
                if ser.in_waiting > 0:
                    # 读取所有可用的数据
                    raw_bytes = ser.read(ser.in_waiting)
                    try:
                        raw_data = raw_bytes.decode('ascii', errors='ignore')
                        buffer += raw_data
                        # print(f"接收到的原始数据: {raw_data}")  # 输出读取到的原始数据，用于调试
                    except UnicodeDecodeError:
                        print("接收到无法解码的数据")
                        continue

                    # 处理缓冲区中的完整消息
                    while True:
                        # 查找消息起始符 '=' 或 '-'
                        start_index = buffer.find('=')
                        if start_index == -1:
                            start_index = buffer.find('-')

                        if start_index == -1:
                            # 未找到起始符，保留最后7个字符，防止消息被截断
                            buffer = buffer[-7:]
                            break

                        if len(buffer) - start_index >= 8:
                            message = buffer[start_index:start_index+8]
                            buffer = buffer[start_index+8:]

                            # print(f"提取到的完整消息: {message}")  # 输出提取到的消息，用于调试

                            weight = parse_weight(message)
                            if weight is not None:
                                current_second_data.append(weight)
                            else:
                                print("解析重量数据失败，未记录。")
                        else:
                            # 缓冲区数据不足以构成完整消息，等待更多数据
                            buffer = buffer[start_index:]
                            break
                else:
                    # 没有可读数据，等待一小段时间再检查
                    time.sleep(0.01)

            # 在1秒结束后，处理当前收集的数据
            if current_second_data:
                # 检查当前1秒内的数据是否一致
                if len(set(current_second_data)) == 1:
                    stable_weight = current_second_data[0]
                    if stable_weight != last_recorded_weight and stable_weight!=0.0:
                        print(f"采集到稳定重量数据：{stable_weight} kg")
                        token = get_valid_token()
                        photo = capture_single_photo()
                        add_data(token,stable_weight,photo)
                        last_recorded_weight = stable_weight
                    else:
                        print("数据与上一秒相同，跳过采集。")
                else:
                    print("1秒内数据不稳定，未采集。")
            else:
                print("1秒内未收到有效数据。")

    except KeyboardInterrupt:
        print("停止数据采集。")
    finally:
        ser.close()
def get_valid_token():
    current_time = time.time()
    if token_info['access_token'] and token_info['expires_at'] > current_time:
        # Token 有效，直接返回
        return token_info['access_token']
    else:
        # Token 不存在或已过期，重新获取
        return fetch_token()
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
        expires_in = token_data.get('expires_in', 360)  # 获取 Token 的有效期，默认为3600秒（1小时）
        # 计算 Token 的过期时间
        expires_at = time.time() + expires_in - 60  # 提前60秒刷新 Token
        # 更新全局 Token 信息
        token_info['access_token'] = access_token
        token_info['expires_at'] = expires_at
        return access_token
    except requests.RequestException as e:
        print(f'Error fetching token: {e}')
        return None
def add_data(token, weight_value, image_base64):
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
        "qrcode": '1',
        "weight": weight_value,
    }
    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        print('Data successfully sent to the backend.')
        return True
    except requests.RequestException as e:
        print(f'Error sending data to the backend: {e}')
        return False
def capture_single_photo():
    camera = cv2.VideoCapture('/dev/v4l/by-id/usb-KD-241010-X_HBSM_Camera-video-index0')
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
        camera.release()
        return photo_base64
    except Exception as e:
        camera.release()
        print(f"Error encoding image: {e}")
        return None

if __name__ == "__main__":
    collect_weight_data()