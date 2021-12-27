from brownie import accounts, config, network

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache",
    "hardhat",
    "local-ganache",
    "mainnet-fork",
]

def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None