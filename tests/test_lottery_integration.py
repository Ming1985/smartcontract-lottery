# integration test, test a whole prcess of a contract on test network
import time
import pytest
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
)
from brownie import network


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # start lottery
    lottery.startLottery({"from": account})
    # enter lottery with minimum required fund
    lottery.enter(
        {
            "from": account,
            "value": lottery.getEntranceFee() + 1000,
            "gasPrice": 10000000000000,
        }
    )
    lottery.enter(
        {
            "from": account,
            "value": lottery.getEntranceFee() + 1000,
            "gasPrice": 10000000000000,
        }
    )
    # fund the contract for random generation
    fund_with_link(lottery)
    # end lottery
    lottery.endLottery({"from": account, "gasPrice":1000000000000})
    time.sleep(160)
    # assert if the contract worked as intended
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
