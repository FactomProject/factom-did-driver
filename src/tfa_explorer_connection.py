import base64
import requests
from . import consts
from . import models
from .config import DriverConfig


IDENTITY_CHAIN_TAG_BASE64 = base64.b64encode(consts.IDENTITY_CHAIN_TAG).decode()
KEY_REPLACEMENT_TAG_BASE64 = base64.b64encode(consts.KEY_REPLACEMENT_TAG).decode()


def get_identity(driver_config: DriverConfig, did: str, chain_id: str, testnet=False):
    api_base_url = driver_config.tfa_explorer_mainnet if not testnet else driver_config.tfa_explorer_testnet
    entry = get_first_entry_in_chain(api_base_url, chain_id)

    if entry['extid_count'] <= 1 or entry['extids'][0] != IDENTITY_CHAIN_TAG_BASE64:
        raise models.IdentityNotFoundException()

    content = base64.b64decode(entry['content'])
    external_ids = [base64.b64decode(x.encode()) for x in entry['extids']]

    identity = models.Identity(did, chain_id)
    if entry['pending']:
        identity.process_creation(entry['entry_hash'], external_ids, content)
        return identity

    identity.process_creation(entry['entry_hash'], external_ids, content, stage='factom', height=entry['block_height'])

    # At this point, we know there is a valid identity at the given chain ID
    limit = 25
    page = 1
    offset = 1
    keep_parsing = True
    while keep_parsing:
        entries = get_entries_in_chain(api_base_url, chain_id, limit, offset)

        if len(entries) < limit:
            keep_parsing = False

        for entry in entries:
            if entry['extid_count'] != 5:
                continue
            elif entry['pending']:
                keep_parsing = False
                break
            elif entry['extids'][0] != KEY_REPLACEMENT_TAG_BASE64:
                continue
            external_ids = [base64.b64decode(x.encode()) for x in entry['extids']]
            identity.process_key_replacement(entry['entry_hash'], external_ids, entry['block_height'])

        offset += limit
        page += 1

    return identity


def get_first_entry_in_chain(api_base_url: str, chain_id: str):
    url = '{}/chain/entries/{}?limit=1&offset=0'.format(api_base_url, chain_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError

    result = resp.json().get('result')
    if result is None:
        raise models.IdentityNotFoundException()

    return result[0]


def get_entries_in_chain(api_base_url: str, chain_id: str, limit=25, offset=0):
    url = '{}/chain/entries/{}?limit={}&offset={}'.format(api_base_url, chain_id, limit, offset)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError

    result = resp.json().get('result')
    return [] if result is None else result
