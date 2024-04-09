from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os

# Initialize Web3 connection
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')  # Consider using secure storage for private keys

web3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))
assert web3.isConnected(), "Failed to connect to Ethereum network."

web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load contract
with open('GPURentalABI.json', 'r') as file:
    CONTRACT_ABI = json.load(file)
gpu_rental_contract = web3.eth.contract(address=Web3.toChecksumAddress(CONTRACT_ADDRESS), abi=CONTRACT_ABI)

# Function to perform Ethereum transactions securely
def perform_transaction(transaction, account_address, private_key, value=0):
    try:
        nonce = web3.eth.getTransactionCount(account_address)
        txn_dict = transaction.buildTransaction({
            'chainId': web3.eth.chain_id,
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei'),
            'nonce': nonce,
            'value': value
        })
        signed_txn = web3.eth.account.signTransaction(txn_dict, private_key)
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        receipt = web3.eth.waitForTransactionReceipt(txn_hash)
        print(f"Transaction successful. Hash: {receipt.transactionHash.hex()}")
        return receipt
    except Exception as e:
        print(f"Transaction failed: {e}")
        return None

# Discover available GPUs
def discover_gpus():
    try:
        available_gpus = gpu_rental_contract.functions.discoverGPUs().call()
        print("Available GPUs:", available_gpus)
        return available_gpus
    except Exception as e:
        print(f"Error discovering GPUs: {e}")
        return []

# Submit a training job
def submit_training_job(training_request, provider_address):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.submitJob(provider_address, json.dumps(training_request)),
        account_address,
        PRIVATE_KEY
    )

# Lock payment for a task with commission
def lock_payment_with_commission(task_id, amount_ether):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.lockPaymentWithCommission(task_id),
        account_address,
        PRIVATE_KEY,
        value=web3.toWei(amount_ether, 'ether')
    )

# Release payment to the GPU provider
def release_payment_with_commission(task_id):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.releasePaymentWithCommission(task_id),
        account_address,
        PRIVATE_KEY
    )

# Verify the results of a training task
def verify_results(task_id, is_successful):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.verifyResults(task_id, is_successful),
        account_address,
        PRIVATE_KEY
    )

# Submit a consensus vote for a task
def submit_consensus_vote(task_id, vote):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.submitConsensusVote(task_id, vote),
        account_address,
        PRIVATE_KEY
    )

# Update the reputation of a GPU provider
def update_provider_reputation(provider_address, change):
    account_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    return perform_transaction(
        gpu_rental_contract.functions.updateReputation(provider_address, change),
        account_address,
        PRIVATE_KEY
    )
