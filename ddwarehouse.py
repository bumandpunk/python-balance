'''
Date: 2024-10-28 15:28:15
LastEditors: Zfj
LastEditTime: 2024-10-29 08:55:07
FilePath: /python-balance/ddwarehouse.py
Description: 
'''
import cv2
import mediapipe as mp
import numpy as np

# 初始化MediaPipe姿势检测模块
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 使用OpenCV打开摄像头
cap = cv2.VideoCapture(0)  # 可以根据设备设置不同的摄像头编号

def detect_posture(landmarks):
    """
    基于关节点检测坐姿或站姿
    :param landmarks: 人体关键点
    :return: 姿势状态
    """
    # 提取肩膀和臀部的y坐标差距，用于判断姿势
    shoulder_y = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
    hip_y = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].y + landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
    
    # 根据肩膀和臀部的距离判断是否为坐姿或站姿
    if abs(shoulder_y - hip_y) < 0.1:
        return "zuozi"
    else:
        return "zhanli"

def main():
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 转换为RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # 检测到人体
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # 检测工作姿势
            posture = detect_posture(landmarks)
            
            # 显示检测结果
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.putText(image, f"Posture: {posture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # 绘制人体关键点
            mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 显示结果
        cv2.imshow("Posture Detection", image)

        # 按 'q' 退出
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()