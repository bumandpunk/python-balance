import cv2
from pyzbar.pyzbar import decode

def capture_and_decode_qrcode():
    # 打开外接摄像头，假设外接摄像头编号为 1
    cap = cv2.VideoCapture(0)  # 修改为合适的摄像头编号

    if not cap.isOpened():
        print("shexiangtou   NO")
        return

    print("deng dai  shi bie ")

    while True:
        # 读取摄像头帧
        ret, frame = cap.read()

        if not ret:
            print("wufa duqu shuju ")
            break

        # 使用 pyzbar 识别二维码
        decoded_objects = decode(frame)

        # 如果检测到二维码
        if decoded_objects:
            for obj in decoded_objects:
                print("qrcode data:", obj.data.decode("utf-8"))
                print("qr type:", obj.type)

            # 在识别到二维码后拍照并保存
            image_path = "qrcode_detected.jpg"
            cv2.imwrite(image_path, frame)
            print(f"image saved at{image_path}")
            break  # 识别到二维码后退出循环

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放摄像头资源
    cap.release()
    cv2.destroyAllWindows()

# 等待用户输入数字
while True:
    try:
        user_input = int(input("please enter a number, then press enter to start the camera for qr code recognition:"))
        print(f"输入的数字是：{user_input}")
        break
    except ValueError:
        print("shuru wu xiao ")

# 用户输入数字后，启动摄像头并进行二维码识别
capture_and_decode_qrcode()
