import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time
import threading

def capture_single_photo(camera):
    """
    用于通过摄像头1拍照并保存
    """
    ret, frame = camera.read()
    if ret:
        image_path = "captured_photo.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Photo saved at {image_path}")
    else:
        print("Failed to capture photo.")

def capture_and_decode_qrcode(camera, stop_event):
    """
    用于通过摄像头2识别二维码
    """
    print("Camera for QR code scanning started, waiting to detect QR code...")

    while not stop_event.is_set():  # 如果没有停止标志则持续识别二维码
        ret, frame = camera.read()

        if not ret:
            print("Failed to read data from camera.")
            continue  # 如果读取失败，则继续读取下一帧

        # 转换为灰度图像
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 二值化处理
        _, binary_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)

        try:
            # 解码二维码
            decoded_objects = decode(binary_frame, symbols=[ZBarSymbol.QRCODE])
        except Exception as e:
            print(f"Decoding error: {e}")
            continue  # 如果发生解码错误，跳过当前帧继续下一个

        # 如果检测到二维码
        if decoded_objects:
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    qr_data = obj.data.decode("utf-8")
                    print("QR code data:", qr_data)
                    stop_event.set()  # 成功识别到二维码后停止二维码识别
                    return  # 识别到二维码后退出

        print("No QR code detected, continuing...")
        time.sleep(0.1)  # 每0.1秒检测一次二维码

def start_capture(camera1, camera2):
    """
    启动两个摄像头的操作，一个拍照，一个二维码识别
    """
    # 创建停止事件，用于控制二维码识别线程的停止
    stop_event = threading.Event()

    # 启动二维码识别线程
    qr_thread = threading.Thread(target=capture_and_decode_qrcode, args=(camera2, stop_event))

    qr_thread.start()

    # 拍摄单张照片
    capture_single_photo(camera1)

    # 等待二维码识别完成
    qr_thread.join()

def main():
    # 主程序
    camera1 = cv2.VideoCapture('/dev/video1')  # 摄像头 1 用于拍照
    camera2 = cv2.VideoCapture('/dev/video4')  # 摄像头 2 用于二维码识别

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
            # 等待用户输入数字并按回车
            user_input = int(input("Please enter a number and press Enter to start: "))

            # 用户输入后，启动摄像头操作
            print(f"Starting capture with input: {user_input}")
            start_capture(camera1, camera2)  # 开始拍照和二维码识别

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
