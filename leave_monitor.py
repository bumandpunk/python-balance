import cv2
import os
import numpy as np
import face_recognition
import time
from datetime import datetime
import csv
from PIL import Image, ImageDraw, ImageFont

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def cv2ImgAddText(img, text, left, top, textColor=(255, 255, 255), textSize=30):
    if isinstance(img, np.ndarray):  # 判断是否 OpenCV 图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        print("输入的图像格式不支持")
        return
    draw = ImageDraw.Draw(img)
    # 使用支持中文的字体（需要系统中有该字体）
    fontStyle = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回 OpenCV 格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def register_faces():
    name = input("请输入员工姓名：")
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("无法打开摄像头")
        return

    face_encodings = []
    count = 0

    ensure_dir('encodings')

    while True:
        ret, frame = cam.read()
        if not ret:
            print("无法读取摄像头")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            count += 1
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            face_encodings.append(face_encoding)

            cv2.rectangle(frame, (face_locations[0][3], face_locations[0][0]), (face_locations[0][1], face_locations[0][2]), (0, 255, 0), 2)
            frame = cv2ImgAddText(frame, f"已采集 {count} 张人脸图像", 10, 30, (255,255,255), 30)
            cv2.imshow('Register', frame)

            if count >= 10:
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    # 保存人脸编码
    ensure_dir('encodings')
    np.save(f"encodings/{name}.npy", face_encodings)
    print(f"{name} 的人脸数据已保存。")

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists('encodings'):
        print("没有找到人脸编码数据，请先录入人脸。")
        return known_face_encodings, known_face_names

    for file in os.listdir("encodings"):
        if file.endswith(".npy"):
            name = file[:-4]
            encodings = np.load(f"encodings/{file}")
            for encoding in encodings:
                known_face_encodings.append(encoding)
                known_face_names.append(name)

    return known_face_encodings, known_face_names

def save_log(name, start_time, end_time, log_file):
    duration = (end_time - start_time).total_seconds() / 60
    try:
        with open(log_file, "a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([name, start_time.strftime('%Y-%m-%d %H:%M:%S'),
                             end_time.strftime('%Y-%m-%d %H:%M:%S'),
                             f"{duration:.2f}分钟"])
        print(f"记录完成: {name} 离岗 {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}, 持续 {duration:.2f} 分钟")
    except Exception as e:
        print(f"保存日志时出错：{e}")

def monitor_leave():
    known_face_encodings, known_face_names = load_known_faces()
    if not known_face_encodings:
        print("没有已知人脸数据，无法开始监测。")
        return

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("无法打开摄像头")
        return

    timeout = 5  # 离岗判定时间（秒）
    last_seen = {}
    is_away = {}
    leave_start = {}

    for name in known_face_names:
        last_seen[name] = time.time()
        is_away[name] = False
        leave_start[name] = None

    print("\n [INFO] 开始离岗监测，按 'q' 键退出程序")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("无法读取摄像头")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        current_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            current_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, current_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            frame = cv2ImgAddText(frame, name, left + 6, top - 30, (255, 255, 255), 30)

            if name != "Unknown":
                last_seen[name] = time.time()
                if is_away[name]:
                    is_away[name] = False
                    leave_end = datetime.now()
                    save_log(name, leave_start[name], leave_end, 'leave_log.csv')
                    leave_start[name] = None

        # 检查离岗状态
        for name in known_face_names:
            if name not in current_names:
                if not is_away[name] and time.time() - last_seen[name] > timeout:
                    is_away[name] = True
                    leave_start[name] = datetime.now()
                    print(f"{name} 离岗开始: {leave_start[name]}")

        cv2.imshow('Monitoring', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    while True:
        print("\n请选择功能：")
        print("1. 录入人脸")
        print("2. 开始离岗监测")
        print("3. 退出程序")
        choice = input("请输入选项：")

        if choice == "1":
            register_faces()
        elif choice == "2":
            monitor_leave()
        elif choice == "3":
            print("程序已退出。")
            break
        else:
            print("无效选项，请重新输入！")
