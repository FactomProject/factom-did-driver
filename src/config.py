import os


class DriverConfig:

    FACTOMD = 'factomd'
    HARMONY = 'harmony'
    valid_connection_types = {FACTOMD, HARMONY}

    def __init__(self):
        self.factom_connection = os.getenv('uniresolver_driver_did_factom_factomConnection', 'factomd')
        self.rpc_url_mainnet = os.getenv('uniresolver_driver_did_factom_rpcUrlMainnet', 'https://api.factomd.net')
        self.rpc_url_testnet= os.getenv('uniresolver_driver_did_factom_rpcUrlTestnet', 'https://dev.factomd.net')
        self.harmony_url = os.getenv('uniresolver_driver_did_factom_harmonyApiUrl', 'https://api.factom.com/v1')
        self.harmony_app_id = os.getenv('uniresolver_driver_did_factom_harmonyApiAppId', '')
        self.harmony_app_key = os.getenv('uniresolver_driver_did_factom_harmonyApiAppKey', '')

        if self.factom_connection not in DriverConfig.valid_connection_types:
            raise ValueError('Invalid factom connection type: "{}"'.format(self.factom_connection))
