import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time

def capture_and_decode_qrcode():
    # 打开外接摄像头，假设设备编号为 0（如有需要可调整编号）
    cap = cv2.VideoCapture(1)

    # 设置摄像头分辨率（根据摄像头的能力调整）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Unable to open camera. Please check the connection.")
        return

    print("Camera started, waiting to detect QR code...")

    while True:
        # 从摄像头读取一帧
        ret, frame = cap.read()

        if not ret:
            print("Failed to read data from camera.")
            continue  # 如果读取失败，则继续读取下一帧

        # 缩放图像以确保二维码区域更加突出
        scale_percent = 150  # 缩放比例为150%
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        # 转换为灰度图像
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        
        # 简单二值化，增强对比度
        _, binary_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)

        try:
            # 允许 QR Code 类型的解码
            decoded_objects = decode(binary_frame, symbols=[ZBarSymbol.QRCODE])
        except Exception as e:
            print(f"Decoding error: {e}")
            continue  # 如果发生解码错误，跳过当前帧继续下一个

        # 如果检测到二维码
        if decoded_objects:
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    qr_data = obj.data.decode("utf-8")
                    print("QR code detected!")
                    print("QR code data:", qr_data)
                    # print("QR code type:", obj.type)

                    # 检测到二维码后保存当前帧
                    image_path = "qrcode_detected.jpg"
                    cv2.imwrite(image_path, frame)
                    print(f"Image saved at {image_path}")
                    return  # 识别到二维码后退出函数，等待用户下一次输入
        else:
            print("No QR code detected, continuing...")
        
        # 暂停0.1秒以减少CPU使用率
        time.sleep(0.1)

    # 释放摄像头资源
    cap.release()

# 主循环：等待用户输入数字并启动摄像头
while True:
    try:
        # 等待用户输入数字
        user_input = int(input("Please enter a number, then press Enter to start the camera for QR code recognition: "))
        print(f"Entered number is: {user_input}")

        # 用户输入数字后，启动摄像头并进行二维码识别
        capture_and_decode_qrcode()
    except ValueError:
        print("Invalid input, please enter a valid number.")
