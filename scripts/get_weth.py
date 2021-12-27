from brownie import network,config,interface

from scripts.helpful_scripts import get_account


def main():
    get_weth()

def get_weth():
    '''
        Mints WETH by depositing ETH
    '''
    # ABI and Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 *10**18})
    tx.wait(1)
    print("Recieved 0.1 ETH")
    return tx