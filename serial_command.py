
import serial
import time

# 串口连接配置，根据实际情况设置
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def initialize_serial():
    """
    初始化串口连接
    """
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Serial connection established on {SERIAL_PORT} at {BAUD_RATE} bps.")
        return ser
    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        return None

def send_serial_command(ser, command):
    """
    向串口发送指令
    """
    if ser and ser.is_open:
        ser.write(f"{command}\n".encode())
        print(f"Sent command to serial: {command}")
    else:
        print("Serial connection not available.")

def main():
    # 初始化串口连接
    ser = initialize_serial()

    # 检查串口是否打开
    if ser:
        while True:
            # 读取用户输入的指令
            command = input("Enter command to send to serial (type 'exit' to quit): ").strip()
            if command.lower() == "exit":
                print("Exiting program.")
                break
            
            # 发送指令到串口
            send_serial_command(ser, command)
            time.sleep(0.5)  # 控制发送速率

        # 关闭串口连接
        ser.close()
        print("Serial connection closed.")

if __name__ == "__main__":
    main()
