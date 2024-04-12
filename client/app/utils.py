from web3 import Web3
import json

web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Load the contract ABI and Address
with open('GPURentalABI.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0x...ContractAddress...'
gpu_rental = web3.eth.contract(address=contract_address, abi=contract_abi)
account = web3.eth.account

def send_transaction(function_call, account, value=0):
    txn = function_call.buildTransaction({
        'chainId': 1,
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei'),
        'nonce': web3.eth.getTransactionCount(account.address),
        'value': value
    })
    signed_txn = web3.eth.account.signTransaction(txn, private_key='YOUR_PRIVATE_KEY')
    return web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def list_gpu():
    return gpu_rental.functions.listGPU().call()

def rent_gpu(gpu_id, compute_units, value):
    txn = gpu_rental.functions.rentGPU(gpu_id, compute_units)
    return send_transaction(txn, account, value=value)

def release_gpu(gpu_id):
    txn = gpu_rental.functions.releaseGPU(gpu_id)
    return send_transaction(txn, account)

def start_training_session(gpu_id, parameterHash ):
    txn = gpu_rental.functions.startTrainingSession(gpu_id, parameterHash)
    return send_transaction(txn, account)

def complete_training_session( session_id, is_completed):
    txn = gpu_rental.functions.completeTrainingSession(session_id, is_completed)
    return send_transaction(txn, account)

def update_gpu_specs(address, specs, price):
    txn = gpu_rental.functions.updateGPUSpecs(address, specs, price)
    return send_transaction(txn, account)
