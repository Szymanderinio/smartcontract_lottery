from .helpful_scripts import *
from brownie import Lottery, config, network

# deploy needs _priceFeedAddress, _vrfCoordinator, _link, _fee, _keyhash
def deploy_lottery():
    account = get_account(id="testAcc")
    Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False) # if there is no verify key = False
    )
    print("Deployed lottery!")

def main():
    deploy_lottery()