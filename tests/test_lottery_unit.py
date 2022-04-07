# 0.019
# 19000000000000000
from brownie import Lottery, accounts, config, network
from web3 import Web3

def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    # print('current fee is', lottery.getEntranceFee())
    assert lottery.getEntranceFee() > Web3.toWei(0.014, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.019, "ether")