# test scripts
import time
from scripts.helpful_scripts import get_account, get_contract, fund_with_link

from brownie import Lottery, accounts, network, config

# delpoy the contract
def deploy_lottery():
    account = get_account()  # get account according to network
    lottery = Lottery.deploy(
        # get contract address and, according to different network setup.
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        # verify the contract
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("deployed lottery")
    return lottery  # return the lottery object


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]  # get the latest deployed contract in brownie
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)  # wait 1 second for the chain to execute
    print("the lottery is started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000  # add a small amount to avoid failure
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("entered lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # need to fund the contract to use Chainlink functions
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    # normally chainlink return a random number with fulfillRandomness , within 60s
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
