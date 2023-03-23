import csv
import subprocess
import json
import sys
from datetime import datetime

def main(argv):
    if len(argv) != 6:
        print("参数数量错误。")
        print("使用方法: python sendmany.py <bitcoin_data_dir> <wallet_name> <sats> <count> <fee_rate>")
        print("示例: python sendmany.py e:\\Bitcoin ord 1000 5 2 (此处的 fee_rate 是 2 sat/vB)")
        return

    bitcoin_data_dir = argv[1]
    wallet_name = argv[2]
    sats = int(argv[3])
    count = int(argv[4])
    fee_rate = int(argv[5])

    if sats < 546:
        print("错误: sats 值不能小于 546 聪。")
        return

    addresses = []

    for i in range(count):
        cmd = ["ord", "--bitcoin-data-dir", bitcoin_data_dir, "wallet", "receive"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        address = json.loads(result.stdout)["address"]
        addresses.append((address, sats))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'addresses_{timestamp}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Address", "Sats"])
        writer.writerows(addresses)

    print(f"已生成 {count} 个地址，保存在 {csv_filename} 文件中")

    recipients = {}
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            address, sats = row
            recipients[address] = float(sats) / 1e8  # Convert sats to BTC

    recipients_json = json.dumps(recipients)
    cmd_sendmany = ["bitcoin-cli", f"-datadir={bitcoin_data_dir}", f"-rpcwallet={wallet_name}", "sendmany", "", recipients_json, "[]", "{}", "UNSET", str(fee_rate)]
    print("执行的命令: ", " ".join(cmd_sendmany))  # 打印命令字符串
    result = subprocess.run(cmd_sendmany, stdout=subprocess.PIPE, text=True)
    print("发送结果: ", result.stdout)

if __name__ == "__main__":
    main(sys.argv)
