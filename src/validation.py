import consts
import json
from collections import  OrderedDict
from identitykeys import is_valid_idpub, PublicIdentityKey


class IdentityNotFoundException(Exception):
    pass


def process_identity_creation(
        active_keys: OrderedDict, all_keys: OrderedDict, entry_hash: str,
        external_ids: list, content: bytes, stage='pending', height=None, time=None
):
    if stage == 'pending':
        assert height is None and time is None, 'Stage "pending", height and time must be None'
    elif stage in {'anchored', 'factom'}:
        assert isinstance(height, int) and time is not None, 'Stage not "pending", height and time must not be None'
    else:
        raise ValueError('Invalid stage. Must be "pending", "factom", or "anchored"')

    # Verify that this is a actually an Identity Chain
    # Rules:
    # - ExtID[0] == "IdentityChain"
    # - Content is a proper JSON object with 'version' and 'keys' elements
    # - All elements of the 'keys' array are valid public keys (idpub format)
    initial_identity = json.loads(content.decode())

    if 'keys' not in initial_identity and 'version' not in initial_identity:
        raise IdentityNotFoundException()

    for i, key in enumerate(initial_identity['keys']):
        if not is_valid_idpub(key):
            raise IdentityNotFoundException()
        elif key in active_keys:
            continue
        key_object = {
            'publicKeyString': key,
            'publicKeyHex': PublicIdentityKey(key_string=key).to_bytes().hex(),
            'activatedHeight': height,
            'activatedTime': time,
            'retiredHeight': None,
            'retiredTime': None,
            'priority': i,
            'entryHash': entry_hash
        }
        active_keys[key] = key_object
        all_keys[key] = key_object

    return {
        'name': [x.decode() for x in external_ids[1:]],
        'createdHeight': height,
        'createdTime': time,
        'stage': stage,
    }


def process_key_replacement(active_keys, all_keys, chain_id, entry_hash, external_ids, height, time):
    if len(external_ids) != 5 or external_ids[0] != consts.KEY_REPLACEMENT_TAG:
        return

    old_key = external_ids[1].decode()
    new_key = external_ids[2].decode()
    signature = external_ids[3]
    signer_key = external_ids[4].decode()

    # all provided keys must be valid
    if not is_valid_idpub(old_key) or not is_valid_idpub(new_key) or not is_valid_idpub(signer_key):
        return

    # new_key must never have been active
    if new_key in all_keys:
        return

    # old_key and signer_key must be currently active
    if old_key not in active_keys or signer_key not in active_keys:
        return

    # signer_key must be the same (or higher) priority as old_key
    old_priority = active_keys[old_key]['priority']
    if old_priority < active_keys[signer_key]['priority']:
        return

    # Finally check the signature
    message = chain_id.encode() + old_key.encode() + new_key.encode()
    k = PublicIdentityKey(key_string=signer_key)
    if not k.verify(signature, message):
        return

    # Key replacement is valid and finalized
    new_key_object = {
        'publicKeyString': new_key,
        'publicKeyHex': PublicIdentityKey(key_string=new_key).to_bytes().hex(),
        'activatedHeight': height,
        'activatedTime': time,
        'retiredHeight': None,
        'retiredTime': None,
        'priority': old_priority,
        'entryHash': entry_hash
    }
    del active_keys[old_key]
    active_keys[new_key] = new_key_object
    all_keys[new_key] = new_key_object
