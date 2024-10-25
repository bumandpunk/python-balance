import cv2
from pyzbar.pyzbar import decode

# 用于存储已检测到的二维码内容
detected_qrcodes = set()

def detect_qrcodes(frame):
    # 使用 pyzbar 解码检测到的所有二维码
    qrcodes = decode(frame)
    
    for qrcode in qrcodes:
        # 获取二维码的边界框位置
        x, y, w, h = qrcode.rect
        # 在二维码周围绘制矩形
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # 解码二维码内容
        qr_data = qrcode.data.decode('utf-8')
        
        # 将未检测到的二维码内容添加到集合中
        if qr_data not in detected_qrcodes:
            detected_qrcodes.add(qr_data)

    return frame

def display_qrcodes_on_screen(frame):
    # 将检测到的二维码内容显示在屏幕左上角
    y_offset = 30  # 用于调整每个二维码内容的垂直位置
    for i, qr_data in enumerate(detected_qrcodes):
        cv2.putText(frame, f'{qr_data}', (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return frame

# 打开摄像头
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # 翻转图像，使其更符合人类观察习惯
    frame = cv2.flip(frame, 1)

    # 检测二维码并显示在画面上
    frame_with_qrcodes = detect_qrcodes(frame)
    
    # 将检测到的所有二维码内容永久显示在左上角
    frame_with_qrcodes = display_qrcodes_on_screen(frame_with_qrcodes)

    # 显示结果
    cv2.imshow('QR Code Detection', frame_with_qrcodes)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头资源
camera.release()
cv2.destroyAllWindows()
