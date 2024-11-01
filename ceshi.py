'''
Date: 2024-11-01 17:04:54
LastEditors: Zfj
LastEditTime: 2024-11-01 17:18:09
FilePath: /python-balance/ceshi.py
Description: 
'''
import serial
import time
import cv2
import requests
import base64
from datetime import datetime
# 程序标识
WEIGHING_URL = "123"   # 称重程序
EVIDENCE_URL = "444"   # 取证程序
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
def check_value(ser, user_value, standard_value, tolerance):
    lower_limit = standard_value - tolerance  # 150
    upper_limit = standard_value + tolerance  # 250
    if user_value < lower_limit or user_value > upper_limit:
            print('红灯')
    else:
        print('绿灯')
    # print(user_value, standard_value, tolerance,lower_limit,upper_limit)

def process_input(input_data):
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
            print(weight_value,standard_value,positive_negative_value)
            check_value('123', weight_value,standard_value,positive_negative_value)
            time.sleep(2)
          
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

      
    else:
        print("Please enter a valid program URL to start (weighing or evidence collection).")

def main():
    global current_program


  
    try:
        while True:
            input_data = input("Please enter input (program URL or other content): ")
            process_input(input_data)
    except KeyboardInterrupt:
        print("Program terminated by user.")
   
    
if __name__ == "__main__":
    main()
