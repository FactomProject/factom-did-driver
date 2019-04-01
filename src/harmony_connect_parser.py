import base64
import consts
import harmony_connect_client as api
import validation
from collections import OrderedDict
from harmony_connect_client.rest import ApiException


# TODO: take configuration from env vars
api_config = api.Configuration()
api_config.host = 'https://durable.api.factom.com/v1'
api_config.api_key['app_id'] = ''
api_config.api_key['app_key'] = ''
entries_api = api.EntriesApi(api.ApiClient(api_config))

IDENTITY_CHAIN_TAG_BASE64 = base64.b64encode(consts.IDENTITY_CHAIN_TAG).decode()
KEY_REPLACEMENT_TAG_BASE64 = base64.b64encode(consts.KEY_REPLACEMENT_TAG).decode()


def get_keys(chain_id):
    active_keys = OrderedDict()
    all_keys = OrderedDict()

    try:
        entry = entries_api.get_first_entry(chain_id).data
    except ApiException as e:
        if e.status == 404:
            raise validation.IdentityNotFoundException()
        raise e

    if len(entry.external_ids) <= 1 or entry.external_ids[0] != IDENTITY_CHAIN_TAG_BASE64:
        raise validation.IdentityNotFoundException()

    content = base64.b64decode(entry.content)
    external_ids = [base64.b64decode(x.encode()) for x in entry.external_ids]
    if entry.stage == 'replicated':
        identity = validation.process_identity_creation(active_keys, all_keys, entry.entry_hash, external_ids, content)
        return identity, active_keys

    identity = validation.process_identity_creation(
        active_keys, all_keys, entry.entry_hash,
        external_ids, content, entry.stage, entry.dblock.height, entry.created_at
    )

    # At this point, we know there is a valid identity at the given chain ID
    limit = 25
    page = 1
    offset = 0
    keep_parsing = True
    while keep_parsing:
        all_entries_response = entries_api.get_entries_by_chain_id(
            chain_id, limit=limit, offset=offset, stages=['factom', 'anchored']
        )

        if all_entries_response.count <= page * limit:
            keep_parsing = False

        for entry_description in all_entries_response.data:
            entry = entries_api.get_entry_by_hash(chain_id, entry_description.entry_hash).data
            if entry.stage != 'replicated':
                keep_parsing = False
                break

            if len(entry.external_ids) != 5 or entry.external_ids[0] != KEY_REPLACEMENT_TAG_BASE64:
                continue

            external_ids = [base64.b64decode(x.encode()) for x in entry.external_ids]
            validation.process_key_replacement(
                active_keys, all_keys,
                chain_id, entry.entry_hash, external_ids, entry.dblock.height, entry.created_at
            )

        offset += limit
        page += 1

    return identity, active_keys
