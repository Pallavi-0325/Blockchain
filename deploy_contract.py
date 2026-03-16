from web3 import Web3
import json
from solcx import compile_source, install_solc

install_solc('0.8.0')

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

with open("contract.sol", "r") as file:
    contract_source_code = file.read()

compiled_sol = compile_source(contract_source_code)

contract_id, contract_interface = compiled_sol.popitem()

bytecode = contract_interface['bin']
abi = contract_interface['abi']

account = w3.eth.accounts[0]

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = Contract.constructor().transact({'from': account})

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed at:", tx_receipt.contractAddress)