import serial
import time

def parse_weight(message):
    """
    解析8字节消息并转换为重量数字。

    参数:
        message (str): 接收到的8字节消息，例如 '=000.100', '-199.400', '-100.10-'

    返回:
        float: 解析后的重量值，如果格式不正确则返回 None
    """
    if len(message) != 8:
        print(f"消息长度不正确: {message} (长度: {len(message)})")
        return None

    start_char = message[0]
    weight_data = message[1:7]  # 字节2-7
    end_char = message[7]

    # 反转重量数据
    reversed_weight_data = weight_data[::-1]

    # 合并重量字符串
    if start_char == '=':
        # 正数
        if end_char != '-':
            # 第8个字节是最高位数字，添加到重量字符串前
            weight_str = end_char + reversed_weight_data
            try:
                weight = float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
        else:
            print(f"正数但末位为'-'，数据异常: {message}")
            return None
    elif start_char == '-':
        # 负数
        if end_char == '-':
            # 第8个字节为'-'，确认负数
            weight_str = reversed_weight_data
            try:
                weight = -float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
        else:
            # 第8个字节是最高位数字，添加到重量字符串前
            weight_str = end_char + reversed_weight_data
            try:
                weight = -float(weight_str)
                return weight
            except ValueError:
                print(f"无法解析重量数据: {weight_str}")
                return None
    else:
        print(f"未知的起始符号: {start_char}")
        return None

def collect_weight_data():
    # 串口配置
    port = "COM3"  # 根据实际情况替换
    baudrate = 9600
    ser = serial.Serial(port, baudrate, timeout=0.1)  # 使用小超时快速读取数据

    last_recorded_weight = None  # 上一次记录的重量
    print("开始收集电子秤数据...")

    try:
        while True:
            current_second_data = []  # 当前1秒内的重量数据
            start_time = time.time()
            buffer = ""  # 缓冲区，用于存储未处理的接收数据

            # 收集1秒内的数据
            while time.time() - start_time < 1:
                if ser.in_waiting > 0:
                    # 读取所有可用的数据
                    raw_bytes = ser.read(ser.in_waiting)
                    try:
                        raw_data = raw_bytes.decode('ascii', errors='ignore')
                        buffer += raw_data
                        # print(f"接收到的原始数据: {raw_data}")  # 输出读取到的原始数据，用于调试
                    except UnicodeDecodeError:
                        print("接收到无法解码的数据")
                        continue

                    # 处理缓冲区中的完整消息
                    while True:
                        # 查找消息起始符 '=' 或 '-'
                        start_index = buffer.find('=')
                        if start_index == -1:
                            start_index = buffer.find('-')

                        if start_index == -1:
                            # 未找到起始符，保留最后7个字符，防止消息被截断
                            buffer = buffer[-7:]
                            break

                        if len(buffer) - start_index >= 8:
                            message = buffer[start_index:start_index+8]
                            buffer = buffer[start_index+8:]

                            # print(f"提取到的完整消息: {message}")  # 输出提取到的消息，用于调试

                            weight = parse_weight(message)
                            if weight is not None:
                                current_second_data.append(weight)
                            else:
                                print("解析重量数据失败，未记录。")
                        else:
                            # 缓冲区数据不足以构成完整消息，等待更多数据
                            buffer = buffer[start_index:]
                            break
                else:
                    # 没有可读数据，等待一小段时间再检查
                    time.sleep(0.01)

            # 在1秒结束后，处理当前收集的数据
            if current_second_data:
                # 检查当前1秒内的数据是否一致
                if len(set(current_second_data)) == 1:
                    stable_weight = current_second_data[0]
                    if stable_weight != last_recorded_weight:
                        print(f"采集到稳定重量数据：{stable_weight} kg")
                        last_recorded_weight = stable_weight
                    else:
                        print("数据与上一秒相同，跳过采集。")
                else:
                    print("1秒内数据不稳定，未采集。")
            else:
                print("1秒内未收到有效数据。")

    except KeyboardInterrupt:
        print("停止数据采集。")
    finally:
        ser.close()

if __name__ == "__main__":
    collect_weight_data()