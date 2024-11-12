'''
Date: 2024-11-12 08:40:24
LastEditors: Zfj
LastEditTime: 2024-11-12 08:40:28
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
UKEY = "h2bIHr9Q7KYKgTKb"  # *必填*: 飞鹅云后台注册账号后生成的UKEY 【备注：这不是填打印机的KEY】
SN = "932600672"  # *必填*：打印机编号，必须要在管理后台里手动添加打印机或者通过API添加之后，才能调用API


# 签名
def signature(STIME):
    s1 = sha1()
    s1.update((USER + UKEY + STIME).encode())
    return s1.hexdigest()

# 小票机打印订单接口
def printMsg(sn):
    # 标签说明：
    # 单标签:
    # "<BR>"为换行,"<CUT>"为切刀指令(主动切纸,仅限切刀打印机使用才有效果)
    # "<LOGO>"为打印LOGO指令(前提是预先在机器内置LOGO图片),"<PLUGIN>"为钱箱或者外置音响指令
    # 成对标签：
    # "<CB></CB>"为居中放大一倍,"<B></B>"为放大一倍,"<C></C>"为居中,<L></L>字体变高一倍
    # <W></W>字体变宽一倍,"<QR></QR>"为二维码,"<BOLD></BOLD>"为字体加粗,"<RIGHT></RIGHT>"为右对齐
    # 条形码标签
    # <BC128_A>123ABCDEF</BC128_A>：数字字母混合条形码, 最多支持14位数字大写字母混合
    # <BC128_C>0123456789</BC128_C>：最多支持22位纯数字
    # 拼凑订单内容时可参考如下格式
    # 根据打印纸张的宽度，自行调整内容的格式，可参考下面的样例格式

    content = "<CB>测试打印</CB><BR>"
    # content += "名称　　　　　 单价  数量 金额<BR>"
    # content += "--------------------------------<BR>"
    # content += "饭　　　　　　 1.0    1   1.0<BR>"
    # content += "炒饭　　　　　 10.0   10  10.0<BR>"
    # content += "蛋炒饭　　　　 10.0   10  100.0<BR>"
    # content += "鸡蛋炒饭　　　 100.0  1   100.0<BR>"
    # content += "番茄蛋炒饭　　 1000.0 1   100.0<BR>"
    # content += "西红柿蛋炒饭　 1000.0 1   100.0<BR>"
    # content += "西红柿鸡蛋炒饭 100.0  10  100.0<BR>"
    # content += "备注：加辣<BR>"
    # content += "--------------------------------<BR>"
    # content += "合计：xx.0元<BR>"
    # content += "送货地点：广州市南沙区xx路xx号<BR>"
    # content += "联系电话：13888888888888<BR>"
    content += "<B>订餐时间：2016-08-08 08:08:08<B><BR>"
    content += "<QR>http://www.feieyun.com</QR>"  # 把二维码字符串用标签套上即可自动生成二维码
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
    else:
        print("error")

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
    else:
        print("error")