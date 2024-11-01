import serial
import time

def open_serial(port='/dev/tty.usbserial-1120', baudrate=9600):
    """
    打开串口连接。
    """
    ser = serial.Serial(port, baudrate, timeout=1)
    if ser.is_open:
        print(f"Serial port {port} opened successfully.")
    else:
        print(f"Failed to open serial port {port}.")
    return ser

def red_light(ser):
    """
    红灯爆闪。
    """
    command = bytes.fromhex("01 06 00 C2 00 31 E9 E2")
    ser.write(command)
    print("Red light blinking.")

def green_light_blink(ser):
    """
    绿灯快闪烁。
    """
    command = bytes.fromhex("01 06 00 C2 00 33 68 23")
    ser.write(command)
    print("Green light slow blinking.")

def turn_off_light(ser):
    """
    关闭灯。
    """
    command = bytes.fromhex("01 06 00 C2 00 60 28 1E")
    ser.write(command)
    print("Light turned off.")

def close_serial(ser):
    """
    关闭串口连接。
    """
    ser.close()
    print("Serial port closed.")

def check_value(ser, user_value, standard_value=200, tolerance=50):
    """
    检查输入值，并根据条件点亮相应的灯。
    
    参数:
    - user_value: 输入的数值。
    - standard_value: 标准值，默认为200。
    - tolerance: 上下浮动范围，默认为50。
    """
    lower_limit = standard_value - tolerance  # 150
    upper_limit = standard_value + tolerance  # 250

    if user_value < lower_limit or user_value > upper_limit:
        red_light(ser)  # 超出范围，红灯爆闪
    else:
        green_light_blink(ser)  # 正常范围内，绿灯慢闪烁

def main():
    # 初始化串口
    ser = open_serial(port='/dev/tty.usbserial-1120', baudrate=9600)

    while True:
        try:
            # 获取用户输入
            user_input = input("Please enter a number (or 'exit' to quit): ")

            if user_input.lower() == 'exit':
                break

            # 转换输入为浮点数
            user_value = float(user_input)

            # 检查输入值并根据范围控制灯
            check_value(ser, user_value)
            time.sleep(2)  # 确保指令有效执行
            turn_off_light(ser)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # 关闭串口
    close_serial(ser)

if __name__ == "__main__":
    main()
