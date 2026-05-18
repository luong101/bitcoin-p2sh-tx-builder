from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2shAddress, P2pkhAddress
from bitcoinutils.script import Script
import requests
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
import math

def calculate_virtual_size(tx_hex_str):
    # Tính kích thước của transaction
    total_size = len(tx_hex_str) // 2 # Chuyển từ hex sang bytes vì 2 ký tự hex mới là 1 byte
    return math.ceil(total_size)


def getFeeRate():
    url = "https://mempool.space/testnet4/api/v1/fees/recommended"
    response = requests.get(url)
    # Kiểm tra phản hồi từ API
    if response.status_code == 200:
        # Chuyển đổi dữ liệu từ JSON
        fee = response.json()
        
        # Lấy thông tin phí
        if fee:
            return fee["fastestFee"]
        else:
            print("No Recommended Fee")
    else:
        print(f"Error: {response.status_code}")

def broadcast_transaction(tx_hex):
    url = "https://mempool.space/testnet4/api/tx"
    headers = {"Content-Type": "text/plain"}

    try:
        response = requests.post(url, data=tx_hex, headers=headers)
        print(f"Phản hồi từ server: {response.status_code}, {response.text}")
        
        if response.status_code == 200:  # Thành công
            print("Broadcast successfully!")
            print("Transaction ID (txid):", response.text.strip())
        else:
            print(f"Broadcast failed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def callAPI(address):
    url = f'https://mempool.space/testnet4/api/address/{address}/utxo'
    # print(url)
    response = requests.get(url)

    # Kiểm tra phản hồi từ API
    if response.status_code == 200:
        # Chuyển đổi dữ liệu từ JSON
        utxo = response.json()
        
        # Lấy thông tin UTXO
        if utxo:
            tx = utxo[0]
            txid = tx['txid']
            vout = tx['vout']
            value = tx['value']
            return txid, vout, value
        else:
            print("No UTXO found for this address.")
    else:
        print(f"Error: {response.status_code}")


def spend_multisig():
    with open("list.txt", "r") as file:
        lines = file.readlines()
        # Lấy các private key từ tệp
        private_key1f = lines[0].strip().split(": ")[1]  # Dòng đầu tiên là Private Key 1
        private_key2f = lines[1].strip().split(": ")[1]  # Dòng thứ hai là Private Key 2
        destination_addressf = lines[8].strip().split(": ")[1]
    # Khóa riêng
    private_key1 = PrivateKey(private_key1f)
    private_key2 = PrivateKey(private_key2f)

    # Khóa công khai
    public_key1 = private_key1.get_public_key().to_hex()
    public_key2 = private_key2.get_public_key().to_hex()

    # Tạo 2-of-2 multisig script
    redeem_script = Script(['OP_2', public_key1, public_key2, 'OP_2', 'OP_CHECKMULTISIG'])

    # Địa chỉ multisig
    multisig_address = P2shAddress.from_script(redeem_script)


    txid, vout, value = callAPI(multisig_address.to_string())


    # Tạo transaction input
    txin = TxInput(txid, vout)

    # Các thông tin của transaction output
    amount_to_send = 800
    destination_address = P2pkhAddress(destination_addressf).to_script_pub_key()

    # Tạo transaction output
    txout = TxOutput(amount_to_send, destination_address)
    
    fee = 500 # Phí tượng trưng

    # Làm một transaction giả để tính kích thước của transaction
    dummy_changes = value - amount_to_send - fee
    txout_dummy_changes = TxOutput(dummy_changes, multisig_address.to_script_pub_key())
    tx_dummy = Transaction([txin], [txout, txout_dummy_changes])
    sig1 = private_key1.sign_input(tx_dummy, 0, redeem_script)
    sig2 = private_key2.sign_input(tx_dummy, 0, redeem_script)
    script_sig = Script(['OP_0', sig1, sig2, redeem_script.to_hex()])
    tx_dummy.inputs[0].script_sig = script_sig
    tx_dummy = tx_dummy.serialize()

    # Phí thật sự
    fee = getFeeRate() * calculate_virtual_size(tx_dummy)
    
    # Tạo transaction output để chuyển lại tiền thừa cho địa chỉ multisig
    changes = value - amount_to_send - fee
    txout_changes = TxOutput(changes, multisig_address.to_script_pub_key())


    tx = Transaction([txin], [txout, txout_changes])

    # Ký bằng cả hai private key
    sig1 = private_key1.sign_input(tx, 0, redeem_script)

    sig2 = private_key2.sign_input(tx, 0, redeem_script)

    # Tạo script_sig
    script_sig = Script(['OP_0', sig1, sig2, redeem_script.to_hex()])
    tx.inputs[0].script_sig = script_sig
    signed_tx = tx.serialize()

    print(f"Địa chỉ gửi: {multisig_address.to_string()}")
    print(f"Địa chỉ nhận: {destination_addressf}")
    print(f"Lượng Satoshis được gửi: {amount_to_send}")
    print(f"Phí: {fee} Satoshis")
    broadcast_transaction(signed_tx)







def main():
    spend_multisig()

main()
