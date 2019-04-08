import bottle
import consts
import factomd_jsonrpc_parser
import harmony_connect_parser
import tfa_explorer_parser
import json
from bottle import error, get, hook, request, run
from config import DriverConfig
from harmony_connect_client.rest import ApiException
from validation import IdentityNotFoundException


driver_config = DriverConfig()


@hook('before_request')
def strip_path():
    """Strip trailing '/' on all requests. '/foo' and /foo/' are two unique endpoints in bottle"""
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@get('/health')
def health_check():
    return {'data': 'Healthy!'}


@get('/1.0/identifiers/did\:factom\:<chain_id:re:[0-9A-Fa-f]{64}>')
def resolve(chain_id):
    metadata, active_keys = None, None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            metadata, active_keys = factomd_jsonrpc_parser.get_keys(driver_config, chain_id)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            metadata, active_keys = tfa_explorer_parser.get_keys(driver_config, chain_id)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            metadata, active_keys = harmony_connect_parser.get_keys(driver_config, chain_id)
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return construct_resolution_result(chain_id, active_keys, metadata)


@get('/1.0/identifiers/did\:factom\:mainnet\:<chain_id:re:[0-9A-Fa-f]{64}>')
def resolve_mainnet(chain_id):
    metadata, active_keys = None, None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            metadata, active_keys = factomd_jsonrpc_parser.get_keys(driver_config, chain_id)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            metadata, active_keys = tfa_explorer_parser.get_keys(driver_config, chain_id)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            metadata, active_keys = harmony_connect_parser.get_keys(driver_config, chain_id)
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return construct_resolution_result(chain_id, active_keys, metadata, network_identifier=consts.NETWORK_MAINNET)


@get('/1.0/identifiers/did\:factom\:testnet\:<chain_id:re:[0-9A-Fa-f]{64}>')
def resolve_testnet(chain_id):
    metadata, active_keys = None, None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            metadata, active_keys = factomd_jsonrpc_parser.get_keys(driver_config, chain_id, testnet=True)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            metadata, active_keys = tfa_explorer_parser.get_keys(driver_config, chain_id, testnet=True)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            bottle.abort(422)  # Connection type does not support testnet
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return construct_resolution_result(chain_id, active_keys, metadata, network_identifier=consts.NETWORK_TESTNET)


def construct_resolution_result(chain_id: str, active_keys: dict, metadata: dict, network_identifier=''):
    did = '{}{}{}'.format(consts.DID_PREFIX, network_identifier, chain_id)
    key_count = len(active_keys)
    public_keys = [None] * key_count
    for key in active_keys.values():
        key['id'] = '{}#key-{}'.format(did, key['priority'])
        key['type'] = consts.PUBLIC_KEY_TYPE
        key['controller'] = did
        public_keys[key['priority']] = key

    did_document = {
        '@context': consts.DID_CONTEXT,
        'id': did,
        'service': [],
        'publicKey': public_keys,
        'authentication': ['{}#key-{}'.format(did, key_count - 1)]
    }
    return {'didDocument': did_document, 'methodMetadata': metadata}


@error(400)
def error400(e):
    body = {'errors': {'detail': 'Bad request'}}
    return json.dumps(body, separators=(',', ':'))


@error(404)
def error404(e):
    body = {'errors': {'detail': 'Page not found'}}
    return json.dumps(body, separators=(',', ':'))


@error(405)
def error405(e):
    body = {'errors': {'detail': 'Method not allowed'}}
    return json.dumps(body, separators=(',', ':'))


@error(422)
def error422(e):
    body = {'errors': {'detail': 'Unprocessable entity'}}
    return json.dumps(body, separators=(',', ':'))


@error(500)
def error500(e):
    body = {'errors': {'detail': 'Internal server error'}}
    return json.dumps(body, separators=(',', ':'))


# Entry point ONLY when run locally. The docker setup uses gunicorn and this block will not be executed.
if __name__ == '__main__':
    run(host='localhost', port=8080)

app = bottle.default_app()
