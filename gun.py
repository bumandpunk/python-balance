'''
Date: 2024-11-06 09:34:21
LastEditors: Zfj
LastEditTime: 2024-11-06 09:35:42
FilePath: /python-balance/gun.py
Description: 
'''
import sys

def main():
    current_identifier = None  # 当前的标识码
    scans = []  # 绑定在当前标识码下的扫描结果

    print("请扫描标识码以开始绑定。")

    while True:
        try:
            # 从标准输入读取一行（模拟扫码枪的输入）
            input_line = input().strip()
            
            if not input_line:
                continue  # 忽略空输入

            if current_identifier is None:
                # 如果当前没有标识码，则将输入设为标识码
                current_identifier = input_line
                scans = []
                print(f"标识码已设置为：{current_identifier}")
            elif input_line == current_identifier:
                # 如果再次扫描到相同的标识码，表示绑定结束
                print(f"再次扫描到标识码 {current_identifier}，绑定结束。")
                # 在此处处理或输出绑定的数据
                print(f"与标识码 {current_identifier} 绑定的扫描结果：")
                for scan in scans:
                    print(f"- {scan}")
                # 重置标识码和扫描结果，准备下一次绑定
                current_identifier = None
                scans = []
                print("请扫描新的标识码以开始新的绑定。")
            else:
                # 将输入添加到当前标识码的绑定列表中
                scans.append(input_line)
                print(f"扫描结果：{input_line} 已绑定到标识码：{current_identifier}")
        except KeyboardInterrupt:
            print("\n程序已终止。")
            sys.exit()
        except Exception as e:
            print(f"发生错误：{e}")
            continue

if __name__ == "__main__":
    main()
