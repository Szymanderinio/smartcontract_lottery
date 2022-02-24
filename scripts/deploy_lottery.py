from .helpful_scripts import *
from brownie import Lottery, config, network
from web3 import Web3
import time
import os


# deploy needs _priceFeedAddress, _vrfCoordinator, _link, _fee, _keyhash
def deploy_lottery():
    account = get_account()
    Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
        # if there is no verify key = False
    )
    print("Deployed lottery!")


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + Web3.toWei(0.001, "ether")  # adding some extra just to make sure it go thru
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with LINK
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    print("{} is the new winner!".format(lottery.recentWinner()))

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
