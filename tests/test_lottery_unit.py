from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, fund_with_link, get_contract
from scripts.deploy_lottery import deploy_lottery
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in local blockchain env")
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2.000 usd / eth --> fee 50usd --> 0.025 eth
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in local blockchain env")
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in local blockchain env")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in local blockchain env")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act / Assert
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2  # CALCULATING_WINNER = 2

def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Not in local blockchain env")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    # Act
    request_id = transaction.events["RequestedRandomness"]["requestId"] # takes emit as an event into id
    STATIC_NUMBER = 777
    get_contract("vrf_coordinator").callBackWithRandomness\
        (request_id, STATIC_NUMBER, lottery.address, {"from": account}) # callBackWithRandomness function
    # 777 % 3 = 0
    starting_balance_of_winner = account.balance()
    balance_of_lottery = lottery.balance()
    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_winner + balance_of_lottery

