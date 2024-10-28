'''
Date: 2024-10-25 17:47:07
LastEditors: Zfj
LastEditTime: 2024-10-25 18:26:55
FilePath: /python-balance/app.py
Description: 
'''
import cv2
from flask import Flask, render_template, request, jsonify
import base64
from pyzbar.pyzbar import decode, ZBarSymbol
from datetime import datetime

app = Flask(__name__)

# 初始化摄像头
camera1 = cv2.VideoCapture(0)  # 摄像头1
camera3 = cv2.VideoCapture(2)  # 摄像头3

def capture_photo(camera):
    """
    捕获照片并添加时间水印，返回Base64编码图像
    """
    if not camera.isOpened():
        return None

    ret, frame = camera.read()
    if not ret:
        return None

    # 添加水印
    watermark_text = f"Captured at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    cv2.putText(frame, watermark_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # 转为Base64
    _, buffer = cv2.imencode('.jpg', frame)
    photo_base64 = base64.b64encode(buffer).decode('utf-8')
    return photo_base64

def scan_qrcode(camera):
    """
    使用摄像头扫描二维码并返回解码结果
    """
    if not camera.isOpened():
        return []

    ret, frame = camera.read()
    if not ret:
        return []

    decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])
    qrcodes = [obj.data.decode("utf-8") for obj in decoded_objects]
    return qrcodes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/capture", methods=["POST"])
def capture():
    camera_id = request.form.get("camera_id")
    camera = camera1 if camera_id == "1" else camera3
    photo_base64 = capture_photo(camera)
    if photo_base64:
        return jsonify({"photo": photo_base64})
    return jsonify({"error": "Failed to capture photo"}), 500

@app.route("/scan_qrcode2", methods=["POST"])
def scan_qrcode2():
    camera_id = request.form.get("camera_id")
    camera = camera1 if camera_id == "1" else camera3
    qrcodes = scan_qrcode(camera)
    if qrcodes:
        return jsonify({"qrcodes": qrcodes})
    return jsonify({"error": "No QR code detected"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

