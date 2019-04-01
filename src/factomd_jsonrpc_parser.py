import consts
import datetime
import validation
from collections import OrderedDict
from factom import Factomd


# TODO: take configuration from env vars
factomd = Factomd(host='http://localhost:8088')


def get_keys(chain_id):
    active_keys = OrderedDict()
    all_keys = OrderedDict()

    chain = factomd.read_chain(chain_id, include_entry_context=True)

    entry = chain[-1]
    if len(entry['extids']) <= 1 or entry['extids'][0] != consts.IDENTITY_CHAIN_TAG:
        raise validation.IdentityNotFoundException()

    timestamp = unix_nano_to_iso8601(entry['timestamp'])
    identity = validation.process_identity_creation(
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

    return identity, active_keys


def unix_nano_to_iso8601(timestamp):
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.isoformat().replace("+00:00", "Z")
