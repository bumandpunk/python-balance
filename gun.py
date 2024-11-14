import sys
import urllib.parse
import requests
import json
import time
from printLabel import printMsg
import schedule
import threading
# 全局变量，用于存储 token 和过期时间
token_info = {
    'access_token': None,
    'expires_at': 0  # 时间戳，表示 token 的过期时间
}

# 全局缓存，存储所有已绑定的商品码
all_bound_product_codes = set()

# 获取 token
def fetch_token():
    url = 'https://os.cajob.cloud/auth/oauth/token?randomStr=blockPuzzle&code=&grant_type=password'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic cGlnOnBpZw==',  # 请替换为正确的授权信息
        'Content-Type': 'application/x-www-form-urlencoded',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data = {
        'username': 'im0204',  # 请替换为您的用户名
        'password': 'JFat0Zdc'   # 请替换为您的密码
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 300)  # 默认1小时过期
        # 计算 token 的过期时间
        expires_at = time.time() + expires_in - 60  # 提前60秒刷新
        # 更新全局 token 信息
        token_info['access_token'] = access_token
        token_info['expires_at'] = expires_at
        return access_token
    except requests.RequestException as e:
        print(f'获取 token 时出错：{e}')
        return None

# 检查并获取有效的 token
def get_valid_token():
    current_time = time.time()
    if token_info['access_token'] and token_info['expires_at'] > current_time:
        # Token 有效
        return token_info['access_token']
    else:
        # Token 不存在或已过期，重新获取
        return fetch_token()

# 重命名后的函数，原代码 A 中的 get_all_bound_product_codes
def process_packages():
    """
    获取包裹列表并处理
    """
    token = get_valid_token()
    if not token:
        print("无法获取有效的 token，无法处理包裹。")
        return

    page = 1
    size = 100  # 每页获取 100 条记录

    # 获取所有包裹码
    while True:
        url = 'https://os.cajob.cloud/fd/formInstance/page'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json;charset=UTF-8',
            'platform-id': '1748273862476910594',
            'tenant-id': '1749325197760434178',
        }
        query_field_list = [{"fieldName": "a173131436547072450", "fieldValue": "0", "operType": "fuzzy"}]
        data_payload = {
            "templateId": "1853070969242693632",
            "current": page,
            "size": size,
            "queryFieldList": query_field_list,
            "queryDefaultRecordCondition": [],
            "orders": []
        }

        try:
            response = requests.post(url, headers=headers, json=data_payload)
            response.raise_for_status()
            response_data = response.json()
            records = response_data.get('data', {}).get('records', [])
            if not records:
                break
            for record in records:
                package_id = record.get('id')
                # 获取订单团 a173087390507965044
                product_code = record.get('a173087390507965044')
                # 获取配送地址 a173130986937073648
                adress = record.get('a173130986937073648')
                # 获取A套餐数量 a173130981465020296
                num_a = record.get('a173130981465020296')
                # 获取B套餐数量 a173130982288125457
                num_b = record.get('a173130982288125457')
                # 获取C套餐数量 a173130983085389180
                num_c = record.get('a173130983085389180')
                # 获取辣椒用量 a173130984148617041
                chili_num = record.get('a173130984148617041')
                # 获取配送人员 a17313103081973913
                delivery_personnel = record.get('a17313103081973913')
                # 获取包裹编号 a173087376594083170
                package_no = record.get('a173087376594083170')
                #获取配送时间  a173147637339175555
                delivery_time = record.get('a173147637339175555')

                content = f"<CB>知味配送单</CB><BR>"
                content += f"团信息：<BR>"
                content += f"<B>{product_code}</B><BR>"
                content += f"配送地址：<BR>"
                content += f"<B>{adress}</B><BR>"
                content += f"套餐数量：<BR>"
                content += f"<B>A套餐：{num_a}</B><BR>"
                content += f"<B>B套餐：{num_b}</B><BR>"
                content += f"<B>C套餐：{num_c}</B><BR>"
                content += f"<B>辣椒用量：{chili_num}</B><BR>"
                content += f"配送时间：<BR>"
                content += f"{delivery_time}<BR><BR>"
                content += f"<QR>https://h5.ziway.com.cn/#/subPackages/sy/evaluate/index?BgNO={package_no}</QR>"
                content += f"知味工场 干净卫生 味美价廉 透明厨房 拒绝预制<BR><BR>"
                content += f"{package_no}<BR><BR>"
                content += f"<B>----------------<B>"
                if package_id:
                    printMsg("932600672", content)
                    update_data(token, package_id)
            total = response_data.get('data', {}).get('total', 0)
            if page * size >= total:
                break
            page += 1
        except requests.RequestException as e:
            print(f'获取包裹码列表时出错：{e}')
            if e.response is not None:
                print("服务器响应内容：")
                print(e.response.text)
            break

def update_data(token, id):
    url = 'https://os.cajob.cloud/fd/formInstance'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
        "id": id,
        "templateId": "1853070969242693632",
        "a173131436547072450": "1"
    }
    response = requests.put(url, headers=headers, json=data_payload)
    if response.status_code == 200:
        print(f'{id} 修改成功')
    else:
        print('更新数据出错:', response.text)

def query_package_code(token, package_code):
    url = 'https://os.cajob.cloud/fd/formInstance/page'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178',
    }

    data_payload = {
        "templateId": "1853070719971012608",
        "current": 1,
        "size": 10,
        "queryFieldList": [
            {
                "fieldName": "box_qr",
                "fieldValue": package_code,
                "operType": "fuzzy"
            }
        ],
        "queryDefaultRecordCondition": [],
        "orders": []
    }

    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        response_data = response.json()
        records = response_data.get('data', {}).get('records', [])
        if records:
            # 如果找到匹配的包裹码，返回第一个的 id
            package_id = records[0].get('id')
            print(f"包裹码已存在，ID：{package_id}")
            return package_id
        else:
            return None
    except requests.RequestException as e:
        print(f'查询包裹码时出错：{e}')
        if e.response is not None:
            print("服务器响应内容：")
            print(e.response.text)
        return None

def upload_package_code(token, package_code):
    url = 'https://os.cajob.cloud/fd/formInstance'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178',
    }

    data_payload = {
        "box_qr": package_code,
        "rice_qr": [],
        "templateId": "1853070719971012608"
    }

    print("正在上传包裹码：")
    print(json.dumps(data_payload, ensure_ascii=False, indent=4))

    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        response_data = response.json()
        package_id = response_data.get('id')
        if not package_id:
            package_id = response_data.get('data')
        print(f'包裹码已成功上传，ID：{package_id}')
        return package_id
    except requests.RequestException as e:
        print(f'上传包裹码时出错：{e}')
        if e.response is not None:
            print("服务器响应内容：")
            print(e.response.text)
        return None

def get_existing_product_codes(token, package_id):
    url = 'https://os.cajob.cloud/fd/formInstance/queryChildTablePage'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178',
    }

    data_payload = {
        "current": 1,
        "size": 1000,  # 假设不会超过 1000 个商品码
        "mainRecordId": package_id,
        "queryFieldList": [],
        "orders": [],
        "templateId": "1853070719971012608",
        "tableProp": "rice_qr"
    }

    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        response_data = response.json()
        records = response_data.get('records', [])
        existing_codes = set()
        for record in records:
            one_qr = record.get('one_qr')
            if one_qr:
                existing_codes.add(one_qr)
        return existing_codes
    except requests.RequestException as e:
        print(f'查询商品码列表时出错：{e}')
        if e.response is not None:
            print("服务器响应内容：")
            print(e.response.text)
        return set()

def add_product_code(token, package_id, product_code):
    url = 'https://os.cajob.cloud/fd/formInstance/saveChildTable'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178',
    }

    data_payload = {
        "one_qr": product_code,
        "templateId": "1853070719971012608",
        "tableProp": "rice_qr",
        "mainTableId": package_id,
        "subTableField": "rice_qr"
    }

    print("正在新增商品码：")
    # print(json.dumps(data_payload, ensure_ascii=False, indent=4))

    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        print(f'商品码已成功添加。')
    except requests.RequestException as e:
        print(f'添加商品码时出错：{e}')
        if e.response is not None:
            print("服务器响应内容：")
            print(e.response.text)

def get_all_bound_product_codes(token):
    """
    获取所有已绑定的商品码，缓存到全局变量 all_bound_product_codes 中
    """
    global all_bound_product_codes
    page = 1
    size = 100  # 每页获取 100 条记录
    all_package_ids = []

    # 获取所有包裹码的 ID
    while True:
        url = 'https://os.cajob.cloud/fd/formInstance/page'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json;charset=UTF-8',
            'platform-id': '1748273862476910594',
            'tenant-id': '1749325197760434178',
        }

        data_payload = {
            "templateId": "1853070719971012608",
            "current": page,
            "size": size,
            "queryFieldList": [],
            "queryDefaultRecordCondition": [],
            "orders": []
        }

        try:
            response = requests.post(url, headers=headers, json=data_payload)
            response.raise_for_status()
            response_data = response.json()
            records = response_data.get('data', {}).get('records', [])
            if not records:
                break
            for record in records:
                package_id = record.get('id')
                if package_id:
                    all_package_ids.append(package_id)
            total = response_data.get('data', {}).get('total', 0)
            if page * size >= total:
                break
            page += 1
        except requests.RequestException as e:
            print(f'获取包裹码列表时出错：{e}')
            if e.response is not None:
                print("服务器响应内容：")
                print(e.response.text)
            break

    # 获取所有已绑定的商品码
    for package_id in all_package_ids:
        existing_codes = get_existing_product_codes(token, package_id)
        all_bound_product_codes.update(existing_codes)
    print(f"已缓存所有已绑定的商品码，共计 {len(all_bound_product_codes)} 个。")

def interactive_input():
    global all_bound_product_codes
    current_package_code = None  # 当前的包裹码（完整的二维码内容）
    current_package_id = None    # 当前包裹码对应的 ID
    existing_product_codes = set()  # 当前包裹码下已存在的商品码集合

    print("请扫描包裹码（含有 'BgNo'）以开始。")

    # 获取有效的 token
    token = get_valid_token()
    if not token:
        print("无法获取有效的 token，程序无法继续。")
        sys.exit()

    # 在程序启动时，缓存所有已绑定的商品码
    get_all_bound_product_codes(token)

    while True:
        try:
            # 从标准输入读取一行（模拟扫码枪的输入）
            input_line = input().strip()

            if not input_line:
                continue  # 忽略空输入

            # 判断是否为包裹码
            if 'BgNo' in input_line:
                # 包裹码处理
                current_package_code = input_line  # 存储完整的二维码内容
                # 首先查询包裹码是否已存在
                package_id = query_package_code(token, current_package_code)
                if package_id:
                    current_package_id = package_id
                    print(f"包裹码已存在，使用已有的包裹码，ID：{current_package_id}")
                else:
                    # 如果不存在，添加新的包裹码
                    package_id = upload_package_code(token, current_package_code)
                    if package_id:
                        current_package_id = package_id
                        print(f"包裹码已成功添加，ID：{current_package_id}")
                    else:
                        print("包裹码上传失败。")
                        current_package_code = None
                        current_package_id = None
                        existing_product_codes = set()
                        continue  # 结束当前循环，等待下一个输入

                # 查询当前包裹码下已有的商品码列表
                existing_product_codes = get_existing_product_codes(token, current_package_id)
                print(f"包裹码已设置为：{current_package_code}")
            else:
                # 商品码处理
                if current_package_code is None or current_package_id is None:
                    print("请先扫描包裹码（含有 'BgNo'）以开始。")
                else:
                    if input_line in all_bound_product_codes:
                        print(f"商品码已被绑定到其他包裹码中，不能重复绑定。")
                    elif input_line in existing_product_codes:
                        print(f"商品码已存在于当前包裹码中，已忽略重复扫描。")
                    else:
                        add_product_code(token, current_package_id, input_line)
                        existing_product_codes.add(input_line)
                        all_bound_product_codes.add(input_line)  # 更新全局缓存
        except KeyboardInterrupt:
            print("\n程序已终止。")
            sys.exit()
        except Exception as e:
            print(f"发生错误：{e}")
            continue
def schedule_task():
        # 每秒执行一次 process_packages
        schedule.every(1).seconds.do(process_packages)
        while True:
            schedule.run_pending()
            time.sleep(1)
def main():
    # 定义并启动定时任务线程
    
    # 启动定时任务线程
    task_thread = threading.Thread(target=schedule_task)
    task_thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    task_thread.start()

    # 启动用户交互线程
    input_thread = threading.Thread(target=interactive_input)
    input_thread.daemon = True  # 设置为守护线程
    input_thread.start()

    # 主线程保持运行，等待用户中断
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已终止。")
        sys.exit()

if __name__ == "__main__":
    main()
