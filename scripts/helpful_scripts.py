from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface
)
from pyparsing import java_style_comment

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    
    # accounts.add(config)
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """this function will grabe the contract addresses from the brownie config
    if defined, otherwise it will deploy a mock version of that contract, and
    return that mock contract,

        Args:
            contract_name (string)

        returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
            eg. MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]  # 获取
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:  # 是否有已经部署的Mock合约
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    print("Deployed MockV3Aggregator Mock!")
    link_token = LinkToken.deploy({"from": account})
    print("Link Token mock deployed")
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("VRFcoordinator mock deployed")

def fund_with_link(
    contract_address, account=None, link_token=None, amount=300000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # tx = interface.LinkTokenInterface.transfer(contract_address, amount, {"from": account})

    # another way to use the function, through interface
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from":account})
    tx.wait(1)
    print(f"Fund contract with: {amount / (10 ** 18)} LINK")
    return tx

