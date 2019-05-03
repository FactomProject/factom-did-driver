from . import consts
from . import models
from .config import DriverConfig
from factom import Factomd
from factom.exceptions import MissingChainHead


def get_identity(driver_config: DriverConfig, did: str, chain_id: str, testnet=False):
    rpc_url = driver_config.rpc_url_mainnet if not testnet else driver_config.rpc_url_testnet
    factomd = Factomd(host=rpc_url)
    try:
        chain = factomd.read_chain(chain_id, include_entry_context=True)
    except MissingChainHead:
        raise models.IdentityNotFoundException()

    entry = chain[-1]
    if len(entry['extids']) <= 1 or entry['extids'][0] != consts.IDENTITY_CHAIN_TAG:
        raise models.IdentityNotFoundException()

    identity = models.Identity(did, chain_id)
    identity.process_creation(entry['entryhash'], entry['extids'], entry['content'],
                              stage='factom', height=entry['dbheight'])

    # At this point, we know there is a valid identity at the given chain ID
    for entry in reversed(chain[:-1]):
        if len(entry['extids']) != 5 or entry['extids'][0] != consts.KEY_REPLACEMENT_TAG:
            continue

        identity.process_key_replacement(entry['entryhash'], entry['extids'], entry['dbheight'])

    return identity
