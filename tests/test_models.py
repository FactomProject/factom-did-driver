import unittest
import identitykeys
import json
from src import consts
from src.models import Identity, IdentityNotFoundException


class TestIdentityCreation(unittest.TestCase):

    def test_valid_input(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        public_keys = [identitykeys.generate_key_pair()[1].to_string() for _ in range(3)]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash= b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        self.assertEqual(1, identity.version)
        for i, external_id in enumerate(external_ids[1:]):
            self.assertEqual(external_id.decode(), identity.name[i])
        for k in public_keys:
            self.assertIn(k, identity.active_keys)
            self.assertIn(k, identity.all_keys)
        for k in identity.active_keys.values():
            self.assertIn('id', k)
            self.assertIn('controller', k)
            self.assertIn('type', k)
            self.assertIn('publicKeyHex', k)
            self.assertIn('activatedHeight', k)
            self.assertIn('retiredHeight', k)
            self.assertIn('priority', k)
            self.assertIn('entryHash', k)

    def test_bad_content_json(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        content = b'BAD{BAD/BAD'

        identity = Identity(did, chain_id)
        with self.assertRaises(IdentityNotFoundException):
            identity.process_creation(
                entry_hash=b'\0' * 32,
                external_ids=external_ids,
                content=content,
                stage='factom',
                height=123456
            )

    def test_bad_keys(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        public_keys = ['BAD' for _ in range(3)]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        with self.assertRaises(IdentityNotFoundException):
            identity.process_creation(
                entry_hash=b'\0' * 32,
                external_ids=external_ids,
                content=json.dumps(content, separators=(',', ':')).encode(),
                stage='factom',
                height=123456
            )

    def test_bad_version(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        public_keys = [identitykeys.generate_key_pair()[1].to_string() for _ in range(3)]
        content = {'version': 'BAD', 'keys': public_keys}

        identity = Identity(did, chain_id)
        with self.assertRaises(IdentityNotFoundException):
            identity.process_creation(
                entry_hash=b'\0' * 32,
                external_ids=external_ids,
                content=json.dumps(content, separators=(',', ':')).encode(),
                stage='factom',
                height=123456
            )


class TestIdentityKeyReplacement(unittest.TestCase):

    def test_valid_replacement(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        key_pairs = [identitykeys.generate_key_pair() for _ in range(3)]
        public_keys = [pub.to_string() for _, pub in key_pairs]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash=b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        _, old_pub = key_pairs[-1]
        signer_priv, signer_pub = key_pairs[-2]
        new_priv, new_pub = identitykeys.generate_key_pair()
        message = chain_id.encode() + old_pub.to_string().encode() + new_pub.to_string().encode()
        external_ids = [
            b'ReplaceKey',
            old_pub.to_string().encode(),
            new_pub.to_string().encode(),
            signer_priv.sign(message),
            signer_pub.to_string().encode()
        ]
        result = identity.process_key_replacement(entry_hash=b'\0' * 32, external_ids=external_ids, height=123457)
        self.assertTrue(result)

    def test_bad_external_ids(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        key_pairs = [identitykeys.generate_key_pair() for _ in range(3)]
        public_keys = [pub.to_string() for _, pub in key_pairs]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash=b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        _, old_pub = key_pairs[-1]
        signer_priv, signer_pub = key_pairs[-2]
        new_priv, new_pub = identitykeys.generate_key_pair()
        message = chain_id.encode() + old_pub.to_string().encode() + new_pub.to_string().encode()
        external_ids = [b'BAD', b'BAD', b'BAD', b'BAD', b'BAD']
        result = identity.process_key_replacement(entry_hash=b'\0' * 32, external_ids=external_ids, height=123457)
        self.assertFalse(result)

    def test_bad_new_key(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        key_pairs = [identitykeys.generate_key_pair() for _ in range(3)]
        public_keys = [pub.to_string() for _, pub in key_pairs]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash=b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        _, old_pub = key_pairs[-1]
        signer_priv, signer_pub = key_pairs[-2]
        new_pub = 'BAD'
        message = chain_id.encode() + old_pub.to_string().encode() + new_pub.encode()
        external_ids = [
            b'ReplaceKey',
            old_pub.to_string().encode(),
            new_pub.encode(),
            signer_priv.sign(message),
            signer_pub.to_string().encode()
        ]
        result = identity.process_key_replacement(entry_hash=b'\0' * 32, external_ids=external_ids, height=123457)
        self.assertFalse(result)

    def test_bad_signature(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        key_pairs = [identitykeys.generate_key_pair() for _ in range(3)]
        public_keys = [pub.to_string() for _, pub in key_pairs]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash=b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        _, old_pub = key_pairs[-1]
        signer_priv, signer_pub = key_pairs[-2]
        new_priv, new_pub = identitykeys.generate_key_pair()
        message = chain_id.encode() + old_pub.to_string().encode() + new_pub.to_string().encode()
        external_ids = [
            b'ReplaceKey',
            old_pub.to_string().encode(),
            new_pub.to_string().encode(),
            b'\0' * 64,
            signer_pub.to_string().encode()
        ]
        result = identity.process_key_replacement(entry_hash=b'\0' * 32, external_ids=external_ids, height=123457)
        self.assertFalse(result)

    def test_bad_signer_priority(self):
        did = 'did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        chain_id = 'f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758'
        external_ids = [consts.IDENTITY_CHAIN_TAG, b'Test', b'v1']
        key_pairs = [identitykeys.generate_key_pair() for _ in range(3)]
        public_keys = [pub.to_string() for _, pub in key_pairs]
        content = {'version': 1, 'keys': public_keys}

        identity = Identity(did, chain_id)
        identity.process_creation(
            entry_hash=b'\0' * 32,
            external_ids=external_ids,
            content=json.dumps(content, separators=(',', ':')).encode(),
            stage='factom',
            height=123456
        )

        _, old_pub = key_pairs[-2]
        signer_priv, signer_pub = key_pairs[-1]
        new_priv, new_pub = identitykeys.generate_key_pair()
        message = chain_id.encode() + old_pub.to_string().encode() + new_pub.to_string().encode()
        external_ids = [
            b'ReplaceKey',
            old_pub.to_string().encode(),
            new_pub.to_string().encode(),
            signer_priv.sign(message),
            signer_pub.to_string().encode()
        ]
        result = identity.process_key_replacement(entry_hash=b'\0' * 32, external_ids=external_ids, height=123457)
        self.assertFalse(result)
