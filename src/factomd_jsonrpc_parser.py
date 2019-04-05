import consts
import datetime
import validation
from collections import OrderedDict
from config import DriverConfig
from factom import Factomd
from factom.exceptions import MissingChainHead


def get_keys(driver_config: DriverConfig, chain_id: str, testnet=False):
    active_keys = {}
    all_keys = OrderedDict()

    rpc_url = driver_config.rpc_url_mainnet if not testnet else driver_config.rpc_url_testnet
    factomd = Factomd(host=rpc_url)
    try:
        chain = factomd.read_chain(chain_id, include_entry_context=True)
    except MissingChainHead:
        raise validation.IdentityNotFoundException()

    entry = chain[-1]
    if len(entry['extids']) <= 1 or entry['extids'][0] != consts.IDENTITY_CHAIN_TAG:
        raise validation.IdentityNotFoundException()

    timestamp = unix_nano_to_iso8601(entry['timestamp'])
    metadata = validation.process_identity_creation(
        active_keys, all_keys, entry['entryhash'],
        entry['extids'], entry['content'], stage='factom', height=123, time=timestamp
    )

    # At this point, we know there is a valid identity at the given chain ID
    for entry in reversed(chain[:-1]):
        if len(entry['extids']) != 5 or entry['extids'][0] != consts.KEY_REPLACEMENT_TAG:
            continue

        timestamp = unix_nano_to_iso8601(entry['timestamp'])
        validation.process_key_replacement(
            active_keys, all_keys, chain_id, entry['entryhash'], entry['extids'], entry['dbheight'], timestamp
        )

    metadata['publicKeyHistory'] = list(all_keys.values())
    return metadata, active_keys


def unix_nano_to_iso8601(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat() + 'Z'
