import os
import json
from web3 import Web3

# Configurações
RPC_URL = "https://rpc.ankr.com/eth_sepolia"
PRIVATE_KEY = os.environ.get('SEPOLIA_PRIVATE_KEY')
# Contrato de Registro Canônico (Exemplo ou Deploy se necessário)
# Se não houver contrato, faremos uma transação simples com o hash no campo 'data'
CANONICAL_HASH = ""
with open("/home/ubuntu/symbios_project/canonical_hash.txt", "r") as f:
    CANONICAL_HASH = f.read().strip()

def register_on_sepolia():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Failed to connect to Sepolia")
        return None
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    
    # Criar transação para o próprio endereço com o hash nos dados (Data field)
    # Isso cria um registro imutável do hash na blockchain
    tx = {
        'nonce': w3.eth.get_transaction_count(address),
        'to': address,
        'value': 0,
        'gas': 21000 + 10000, # Base + data cost
        'gasPrice': w3.eth.gas_price,
        'data': w3.to_hex(text=f"symbiOS_hash:{CANONICAL_HASH}"),
        'chainId': 11155111
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)

if __name__ == "__main__":
    if not PRIVATE_KEY:
        print("Sepolia Private Key not found.")
    else:
        tx_id = register_on_sepolia()
        if tx_id:
            print(f"Registered on Sepolia. TX: {tx_id}")
            with open("/home/ubuntu/symbios_project/sepolia_tx.txt", "w") as f:
                f.write(tx_id)
