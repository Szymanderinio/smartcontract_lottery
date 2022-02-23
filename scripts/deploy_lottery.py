from .helpful_scripts import *
from brownie import Lottery

# deploy needs _priceFeedAddress, _vrfCoordinator, _link, _fee, _keyhash
def deploy_lottery():
    account = get_account(id="testAcc")
    lotter = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,

    )

def main():
    deploy_lottery()