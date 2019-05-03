import json
from . import consts
from collections import OrderedDict
from identitykeys import is_valid_idpub, PublicIdentityKey


class IdentityNotFoundException(Exception):
    pass


class Identity:

    def __init__(self, did, chain_id):
        self.did = did
        self.chain_id = chain_id
        self.active_keys = {}
        self.all_keys = OrderedDict()
        self.version = 1
        self.name = None
        self.created_height = None
        self.stage = None

    def process_creation(self, entry_hash: str, external_ids: list, content: bytes, stage='pending', height=None):
        if stage == 'pending':
            assert height is None, 'Stage "pending", height must be None'
        elif stage in {'anchored', 'factom'}:
            assert isinstance(height, int), 'Stage not "pending", height must not be None'
        else:
            raise ValueError('Invalid stage. Must be "pending", "factom", or "anchored"')

        # Verify that this is a actually an Identity Chain
        # Rules:
        # - ExtID[0] == "IdentityChain"
        # - Content is a proper JSON object with 'version' and 'keys' elements
        # - All elements of the 'keys' array are valid public keys (idpub format)
        if external_ids[0] != consts.IDENTITY_CHAIN_TAG:
            raise IdentityNotFoundException()

        try:
            content_json = json.loads(content.decode())
        except json.JSONDecodeError:
            raise IdentityNotFoundException()

        if content_json.get('version') == 1:
            if not isinstance(content_json.get('keys'), list):
                raise IdentityNotFoundException()

            for i, key in enumerate(content_json['keys']):
                if not is_valid_idpub(key):
                    raise IdentityNotFoundException()
                elif key in self.active_keys:
                    continue
                key_object = {
                    'id': '{}#key-{}'.format(self.did, i),
                    'controller': self.did,
                    'type': consts.PUBLIC_KEY_TYPE,
                    'publicKeyHex': PublicIdentityKey(key_string=key).to_bytes().hex(),
                    'activatedHeight': height,
                    'retiredHeight': None,
                    'priority': i,
                    'entryHash': entry_hash
                }
                self.active_keys[key] = key_object
                self.all_keys[key] = key_object
        else:
            raise IdentityNotFoundException()

        self.version = content_json.get('version')
        self.name = [x.decode() for x in external_ids[1:]]
        self.created_height = height
        self.stage = stage

    def process_key_replacement(self, entry_hash: str, external_ids: list, height: int):
        if len(external_ids) != 5 or external_ids[0] != consts.KEY_REPLACEMENT_TAG:
            return

        old_key = external_ids[1].decode()
        new_key = external_ids[2].decode()
        signature = external_ids[3]
        signer_key = external_ids[4].decode()

        # all provided keys must be valid
        if not is_valid_idpub(old_key) or not is_valid_idpub(new_key) or not is_valid_idpub(signer_key):
            return False

        # new_key must never have been active
        if new_key in self.all_keys:
            return False

        # old_key and signer_key must be currently active
        if old_key not in self.active_keys or signer_key not in self.active_keys:
            return False

        # signer_key must be the same (or higher) priority as old_key
        old_priority = self.active_keys[old_key]['priority']
        if old_priority < self.active_keys[signer_key]['priority']:
            return False

        # Finally check the signature
        message = self.chain_id.encode() + old_key.encode() + new_key.encode()
        k = PublicIdentityKey(key_string=signer_key)
        if not k.verify(signature, message):
            return False

        # Key replacement is valid and finalized
        self.all_keys[old_key]['retiredHeight'] = height
        new_key_object = {
            'id': '{}#key-{}'.format(self.did, old_priority),
            'controller': self.did,
            'type': consts.PUBLIC_KEY_TYPE,
            'publicKeyHex': PublicIdentityKey(key_string=new_key).to_bytes().hex(),
            'activatedHeight': height,
            'retiredHeight': None,
            'priority': old_priority,
            'entryHash': entry_hash
        }
        del self.active_keys[old_key]
        self.active_keys[new_key] = new_key_object
        self.all_keys[new_key] = new_key_object
        return True

    def get_did_document(self):
        key_count = len(self.active_keys)
        did_document = {
            '@context': consts.DID_CONTEXT,
            'id': self.did,
            'service': [],
            'publicKey': list(self.active_keys.values()),
            'authentication': ['{}#key-{}'.format(self.did, key_count - 1)]
        }
        return did_document

    def get_method_metadata(self):
        return {
            'version': self.version,
            'name': self.name,
            'createdHeight': self.created_height,
            'stage': self.stage,
            'publicKeyHistory': list(self.all_keys.values())
        }

