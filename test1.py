import time
import requests

# 全局变量
user_weight = None
scanned_qr_code = None

# 获取 token
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
        print("Token fetched successfully.")
        return token
    except requests.RequestException as e:
        print(f'Error fetching token: {e}')
        return None

# 获取称重阈值
def get_threshold_values():
    token = fetch_token()
    if not token:
        print("Cannot fetch threshold values without a valid token.")
        return None, None
    url = 'https://os.cajob.cloud/fd/formInstance/page'
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'platform-id': '1748273862476910594',
        'tenant-id': '1749325197760434178'
    }
    data_payload = {
        "templateId": "1850929236043276288",
        "current": 1,
        "size": 10,
        "queryFieldList": [],
        "queryDefaultRecordCondition": [],
        "orders": []
    }
    try:
        response = requests.post(url, headers=headers, json=data_payload)
        response.raise_for_status()
        records = response.json().get('data', {}).get('records', [])
        print("Fetched records:", records)

        for item in records:
            if item.get('a173036328345917519') == '称重程序':
                standard_value_str = item.get('standard_value')
                tolerance_str = item.get('positive_negative_value')
                print(f"Standard value (str): {standard_value_str}, Tolerance (str): {tolerance_str}")

                if standard_value_str and tolerance_str:
                    standard_value = float(standard_value_str)
                    tolerance = float(tolerance_str)
                    print(f"Standard value (float): {standard_value}, Tolerance (float): {tolerance}")
                    return standard_value, tolerance
                else:
                    print("Standard value or tolerance is missing.")
                    return None, None
        print("No threshold values found.")
        return None, None
    except requests.RequestException as e:
        print(f'Error fetching threshold values: {e}')
        return None, None

# 模拟红灯闪烁
def red_light():
    print("Red light would blink here.")

# 模拟绿灯慢闪烁
def green_light_blink():
    print("Green light would blink here.")

# 模拟关闭灯光
def turn_off_light():
    print("Lights would turn off here.")

# 主程序
def main():
    # 获取阈值
    standard_value, tolerance = get_threshold_values()
    if standard_value is None or tolerance is None:
        print("Failed to get threshold values. Exiting.")
        return

    # 添加调试信息
    print(f"Standard value: {standard_value}, Tolerance: {tolerance}")

    try:
        while True:
            try:
                # 输入重量值
                weight_input = input("Please enter the weight value: ").strip()
                weight_value = float(weight_input)
                print(f"Weight value: {weight_value}")

                # 检查重量是否在阈值范围内
                lower_limit = standard_value - tolerance
                upper_limit = standard_value + tolerance
                print(f"Lower limit: {lower_limit}, Upper limit: {upper_limit}")

                weight_in_range = lower_limit <= weight_value <= upper_limit
                print(f"Weight in range: {weight_in_range}")

                # 根据条件，调用相应的灯光函数（此处为模拟）
                if weight_in_range:
                    green_light_blink()
                else:
                    red_light()

                # 模拟等待时间
                time.sleep(2)
                turn_off_light()

                print("Process completed. Ready for the next cycle.\n")

            except ValueError:
                print("Invalid weight input. Please enter a valid number.")
            except Exception as e:
                print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()
