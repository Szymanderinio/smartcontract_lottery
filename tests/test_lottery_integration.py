from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, fund_with_link, get_contract
from scripts.deploy_lottery import deploy_lottery
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in testnet!")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0