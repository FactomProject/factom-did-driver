import os


class DriverConfig:

    FACTOMD = 'factomd'
    TFA_EXPLORER = 'tfa_explorer'
    HARMONY = 'harmony'
    valid_connection_types = {FACTOMD, TFA_EXPLORER, HARMONY}

    def __init__(self):
        self.factom_connection = os.getenv('uniresolver_driver_did_factom_factomConnection', 'tfa_explorer')

        # Factomd JSON RPC
        self.rpc_url_mainnet = os.getenv('uniresolver_driver_did_factom_rpcUrlMainnet', 'https://api.factomd.net')
        self.rpc_url_testnet = os.getenv('uniresolver_driver_did_factom_rpcUrlTestnet', 'https://dev.factomd.net')

        # TFA's Explorer API
        self.tfa_explorer_mainnet = os.getenv('uniresolver_driver_did_factom_tfaExplorerApiUrlMainnet', 'https://explorer.factoid.org/api/v1')
        self.tfa_explorer_testnet = os.getenv('uniresolver_driver_did_factom_tfaExplorerApiUrlTestnet', 'https://testnet.factoid.org/api/v1')

        # Factom Inc's Harmony Connect
        self.harmony_url = os.getenv('uniresolver_driver_did_factom_harmonyApiUrl', 'https://api.factom.com/v1')
        self.harmony_app_id = os.getenv('uniresolver_driver_did_factom_harmonyApiAppId', '')
        self.harmony_app_key = os.getenv('uniresolver_driver_did_factom_harmonyApiAppKey', '')

        if self.factom_connection not in DriverConfig.valid_connection_types:
            raise ValueError('Invalid factom connection type: "{}"'.format(self.factom_connection))
