from brownie import accounts, network, config, MockV3Aggregator, VRFCoordinatorMock, Contract
from web3 import Web3

FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator, "vrf_coordinator": VRFCoordinatorMock}


def get_contract(contract_name):
    """
    This function will grab the contract addresses form the brownie config
     if defined, otherwise, it will deploy a mock version of that contract, and
     return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:  # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]  # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address, ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)  # MockV3Aggregator.abi
    return contract


DECIMALS = 8
STARTING_PRICE = 200000000000


def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_price, {"from": account})
    print("Mocks Deployed!")
