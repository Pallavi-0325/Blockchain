from web3 import Web3
from solcx import compile_source, install_solc

# Install Solidity compiler
try:
    install_solc("0.8.0")
except:
    pass

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("❌ Failed to connect to Ganache")

print("✅ Connected to Blockchain")

# Global variables
contract_instance = None
contract_address = None
abi = None
bytecode = None


def compile_contract():
    """Compile Solidity contract"""
    with open("contracts/ConsentManager.sol", "r") as file:
        source = file.read()

    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version="0.8.0"
    )

    contract_id, interface = next(iter(compiled.items()))

    return interface["abi"], interface["bin"]


def deploy_contract():
    """Deploy contract to blockchain"""
    global contract_instance
    global contract_address

    deployer = w3.eth.accounts[0]

    Contract = w3.eth.contract(
        abi=abi,
        bytecode=bytecode
    )

    tx_hash = Contract.constructor().transact({
        "from": deployer,
        "gas": 6000000
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress

    contract_instance = w3.eth.contract(
        address=contract_address,
        abi=abi
    )

    print("🚀 Contract deployed at:", contract_address)

    return contract_instance


def get_contract():
    """Return contract instance"""
    global contract_instance

    if contract_instance is None:
        contract_instance = deploy_contract()

    return contract_instance


def get_accounts():
    """Return blockchain accounts"""
    return w3.eth.accounts


# Compile contract
abi, bytecode = compile_contract()

# Deploy contract once
contract_instance = deploy_contract()
