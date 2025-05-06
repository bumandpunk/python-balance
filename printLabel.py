'''
Date: 2024-11-12 08:40:24
LastEditors: Zfj
LastEditTime: 2024-11-14 07:56:48
FilePath: /python-balance/printLabel.py
Description: 
'''
# coding:utf-8

import time
from hashlib import sha1
import requests

# 说明：
URL = "http://api.feieyun.cn/Api/Open/"  # 不需要修改
USER = "844788189@qq.com"  # *必填*：飞鹅云后台注册账号
UKEY = "*******"  # *必填*: 飞鹅云后台注册账号后生成的UKEY 【备注：这不是填打印机的KEY】
SN = "********"  # *必填*：打印机编号，必须要在管理后台里手动添加打印机或者通过API添加之后，才能调用API


# 签名
def signature(STIME):
    s1 = sha1()
    s1.update((USER + UKEY + STIME).encode())
    return s1.hexdigest()

# 小票机打印订单接口

def printMsg(sn,content):
    STIME = str(int(time.time()))  # 不需要修改
    params = {
        'user': USER,
        'sig': signature(STIME),
        'stime': STIME,
        'apiname': 'Open_printMsg',  # 固定值,不需要修改
        'sn': sn,
        'content': content,
        'times': '1'  # 打印联数
        
    }
    response = requests.post(URL, data=params, timeout=30)
    code = response.status_code  # 响应状态码
    if code == 200:
        print(response.content)  # 服务器返回的JSON字符串,建议要当做日志记录起来
        return response.content  # 服务器返回的JSON字符串,建议要当做日志记录起来
    else:
        print("error")
