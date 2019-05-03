import base64
import harmony_connect_client as api
from . import consts
from . import models
from .config import DriverConfig
from factom_sdk import FactomClient
from harmony_connect_client.rest import ApiException
from identitykeys import PublicIdentityKey
from requests import HTTPError


IDENTITY_CHAIN_TAG_BASE64 = base64.b64encode(consts.IDENTITY_CHAIN_TAG).decode()
KEY_REPLACEMENT_TAG_BASE64 = base64.b64encode(consts.KEY_REPLACEMENT_TAG).decode()


def get_identity(driver_config: DriverConfig, did: str, chain_id: str):
    if driver_config.harmony_caching_enabled:
        return _get_identity_with_cache(driver_config, did, chain_id)

    return _get_identity_without_cache(driver_config, did, chain_id)


def _get_identity_with_cache(driver_config: DriverConfig, did: str, chain_id: str):
    """Fetch a cached copy of the identity's current state from Harmony.
    Useful for identities with an absurd number of key replacements, or for a chain with a lot of spam."""
    factom_sdk = FactomClient(driver_config.harmony_url, driver_config.harmony_app_id, driver_config.harmony_app_key)
    try:
        identity = factom_sdk.identities.get(chain_id)
    except HTTPError as e:
        raise models.IdentityNotFoundException() if e.response.status_code == 404 else e

    identity_response = identity.get('data')
    identity = models.Identity(did, chain_id)
    identity.version = identity_response.get('version')
    identity.name = identity_response.get('names')
    identity.created_height = identity_response.get('created_height')
    identity.stage = identity_response.get('stage')
    identity.active_keys = {
        k.get('key'):
        {
            'id': '{}#key-{}'.format(did, k.get('priority')),
            'controller': did,
            'type': consts.PUBLIC_KEY_TYPE,
            'publicKeyHex': PublicIdentityKey(key_string=k.get('key')).to_bytes().hex(),
            'activatedHeight': k.get('activated_height'),
            'retiredHeight': None,
            'priority': k.get('priority'),
            'entryHash': k.get('entry_hash')
        }
        for k in identity_response.get('active_keys')
    }

    limit = 25
    page = 1
    offset = 0
    while True:
        keys_response = factom_sdk.identities.keys.list(chain_id, limit=limit, offset=offset)
        for k in keys_response.get('data'):
            if k.get('activated_height') is None:
                continue
            identity.all_keys[k.get('key')] = {
                'id': '{}#key-{}'.format(did, k.get('priority')),
                'controller': did,
                'type': consts.PUBLIC_KEY_TYPE,
                'publicKeyHex': PublicIdentityKey(key_string=k.get('key')).to_bytes().hex(),
                'activatedHeight': k.get('activated_height'),
                'retiredHeight': k.get('retired_height'),
                'priority': k.get('priority'),
                'entryHash': k.get('entry_hash')
            }

        if keys_response.get('count') <= page * limit:
            break
        offset += limit
        page += 1

    return identity


def _get_identity_without_cache(driver_config: DriverConfig, did: str, chain_id: str):
    """Parse the entire chain to build up the identity's current state"""
    api_config = api.Configuration()
    api_config.host = driver_config.harmony_url
    api_config.api_key['app_id'] = driver_config.harmony_app_id
    api_config.api_key['app_key'] = driver_config.harmony_app_key
    entries_api = api.EntriesApi(api.ApiClient(api_config))

    try:
        entry = entries_api.get_first_entry(chain_id).data
    except ApiException as e:
        raise models.IdentityNotFoundException() if e.status == 404 else e

    if len(entry.external_ids) <= 1 or entry.external_ids[0] != IDENTITY_CHAIN_TAG_BASE64:
        raise models.IdentityNotFoundException()

    content = base64.b64decode(entry.content)
    external_ids = [base64.b64decode(x.encode()) for x in entry.external_ids]
    identity = models.Identity(did, chain_id)
    if entry.stage == 'replicated':
        identity.process_creation(entry.entry_hash, external_ids, content)
        return identity

    identity.process_creation(entry.entry_hash, external_ids, content, stage=entry.stage, height=entry.dblock.height)

    # At this point, we know there is a valid identity at the given chain ID
    limit = 25
    page = 1
    offset = 0
    keep_parsing = True
    while keep_parsing:
        all_entries_response = entries_api.get_entries_by_chain_id(chain_id, limit=limit, offset=offset)

        if all_entries_response.count <= page * limit:
            keep_parsing = False

        for entry_description in all_entries_response.data:
            entry = entries_api.get_entry_by_hash(chain_id, entry_description.entry_hash).data
            if entry.stage == 'replicated':
                keep_parsing = False
                break

            if len(entry.external_ids) != 5 or entry.external_ids[0] != KEY_REPLACEMENT_TAG_BASE64:
                continue

            external_ids = [base64.b64decode(x.encode()) for x in entry.external_ids]
            identity.process_key_replacement(entry.entry_hash, external_ids, entry.dblock.height)

        offset += limit
        page += 1

    return identity
