from brownie import accounts, network, config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract, interface
from web3 import Web3
import os

FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]
    return accounts.add(os.getenv("PRIVATE_KEY"))
    # return accounts.add(config["wallets"]["from_key"]) # for some reason it stopped working


contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator,
                    "vrf_coordinator": VRFCoordinatorMock,
                    "link_token": LinkToken}


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
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token, {"from": account})
    print("Mocks Deployed!")


# 100_000_000_000_000_000 0.1LINK
# 100_000_000_000_000_000
def fund_with_link(contract_address, account=None, link_token=None, amount=Web3.toWei(0.25, "ether")):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # tx = link_token.transfer(contract_address, amount, {"from": account})  # using get_contract
    link_token_contract = interface.LinkTokenInterface(link_token.address)  # using interface // declarations
    tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx
