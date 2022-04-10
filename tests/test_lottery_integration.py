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
    lottery.startLottery({"from": account})
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
    fund_with_link(lottery)
    lottery.endLottery({"from": account, "gasPrice":1000000000000})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
