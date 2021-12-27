from brownie import network, config, interface
from eth_utils import address
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account
from web3 import Web3

amount = Web3.toWei(0.1,"ether")

def main():
    account = get_account()
    erc20_add = config["networks"][network.show_active()]["weth_token"]
    dia_token_add = config["networks"][network.show_active()]["dia_token_add"]
    dia_eth_add = config["networks"][network.show_active()]["dai_eth_price_feed"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    
    lending_pool = get_lending_pool()
    # print(lending_pool)
    
    approve_erc20(lending_pool.address,amount,erc20_add,account)
    print("Depositing...")
    tx = lending_pool.deposit(erc20_add,amount,account.address,0,{"from": account})
    tx.wait(1)
    print("deposited!!")
    borrowable_eth, total_debt = swipable_data(lending_pool,account)
    # DAI in terms of ETH
    dia_eth_price = get_asset_price(dia_eth_add)

    amount_dai_to_borrow = (1/dia_eth_price) * (borrowable_eth* 0.95)
    # Borrowble_dai = borrowable_eth * 95%
    print(f" We are borrowing {amount_dai_to_borrow} DIA")
    # Borrowing
    print("Borrowing!!")
    borrow_tx = lending_pool.borrow(dia_token_add,Web3.toWei(amount_dai_to_borrow,"ether"),1,0,account.address, {"from": account})
    borrow_tx.wait(1)
    print("DAI Borrowed")
    swipable_data(lending_pool,account)
    repay_all(amount, lending_pool,account)
    print("AAVE Functionalities achieved")
    swipable_data(lending_pool,account)
    
    

def repay_all(amount, lending_pool, account):
    approve_erc20(lending_pool.address,Web3.toWei(amount,"ether"),config["networks"][network.show_active()]["dia_token_add"],account)
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dia_token_add"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid")

def get_asset_price(price_feed_address):
    dia_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dia_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price,"ether")
    print(f"The latest DIA/ETH price is {converted_latest_price}")
    return float(converted_latest_price)


def swipable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    availableBorrowsETH = Web3.fromWei(available_borrow_eth,"ether")
    totalCollateralETH = Web3.fromWei(total_collateral_eth, "ether")
    totalDebtETH=Web3.fromWei(total_debt_eth, "ether")

    print(f"You have {totalCollateralETH} worth of ETH deposited")
    print(f"You can borrow {availableBorrowsETH} worth of ETH")
    print(f"You have {totalDebtETH} worth of ETH borrowed")
    return (float(availableBorrowsETH), float(totalDebtETH))

# Approve sendind out ERC20 tokens
def approve_erc20(spender, value, erc20_address,account):
    print("Appproving ERC20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender,value,{"from": account})
    tx.wait(1)
    print("Approved")
    return tx

def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_address_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool