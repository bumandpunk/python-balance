import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time
import threading
import requests
def fetch_token(user_input, image_path, qr_data):
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
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        add_data(response.json().get('access_token'),user_input, image_path, qr_data)
    else:
        print('获取 token 出错:', response.text)
        return None
    
def add_data(token,user_input, image_path, qr_data):
    url = 'https://os.cajob.cloud/fd/formInstance'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
        "img_base64": image_path,
        "templateId": "1848003481851305984",
        "qrcode": qr_data,
        "weight": user_input
    }
    response = requests.post(url, headers=headers, json=data_payload)
    if response.status_code == 200:
        print('add success')



fetch_token('70','24234','2342342342')