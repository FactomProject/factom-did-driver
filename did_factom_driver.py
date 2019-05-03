import bottle
import json
from bottle import error, get, hook, request, run
from harmony_connect_client.rest import ApiException
from src import consts
from src import factomd_jsonrpc_connection
from src import harmony_connect_connection
from src import tfa_explorer_connection
from src.config import DriverConfig
from src.models import IdentityNotFoundException


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
    did = '{}{}'.format(consts.DID_PREFIX, chain_id)
    identity = None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            identity = factomd_jsonrpc_connection.get_identity(driver_config, did, chain_id)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            identity = tfa_explorer_connection.get_identity(driver_config, did, chain_id)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            identity = harmony_connect_connection.get_identity(driver_config, did, chain_id)
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return {'didDocument': identity.get_did_document(), 'methodMetadata': identity.get_method_metadata()}


@get('/1.0/identifiers/did\:factom\:mainnet\:<chain_id:re:[0-9A-Fa-f]{64}>')
def resolve_mainnet(chain_id):
    did = '{}{}{}'.format(consts.DID_PREFIX, consts.NETWORK_MAINNET, chain_id)
    identity = None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            identity = factomd_jsonrpc_connection.get_identity(driver_config, did, chain_id)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            identity = tfa_explorer_connection.get_identity(driver_config, did, chain_id)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            identity = harmony_connect_connection.get_identity(driver_config, did, chain_id)
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return {'didDocument': identity.get_did_document(), 'methodMetadata': identity.get_method_metadata()}


@get('/1.0/identifiers/did\:factom\:testnet\:<chain_id:re:[0-9A-Fa-f]{64}>')
def resolve_testnet(chain_id):
    did = '{}{}{}'.format(consts.DID_PREFIX, consts.NETWORK_TESTNET, chain_id)
    identity = None
    try:
        if driver_config.factom_connection == DriverConfig.FACTOMD:
            identity = factomd_jsonrpc_connection.get_identity(driver_config, did, chain_id, testnet=True)
        elif driver_config.factom_connection == DriverConfig.TFA_EXPLORER:
            identity = tfa_explorer_connection.get_identity(driver_config, did, chain_id, testnet=True)
        elif driver_config.factom_connection == DriverConfig.HARMONY:
            # TODO: switch this to use the Harmony connection if Harmony ever spins up a community testnet environment
            # For now, fall back to using a factomd connection
            identity = factomd_jsonrpc_connection.get_identity(driver_config, did, chain_id, testnet=True)
        else:
            bottle.abort(500)  # Invalid connection type. This should never be executed.
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    return {'didDocument': identity.get_did_document(), 'methodMetadata': identity.get_method_metadata()}


@error(404)
def error404(e):
    body = {'errors': {'detail': 'Page not found'}}
    return json.dumps(body, separators=(',', ':'))


@error(405)
def error405(e):
    body = {'errors': {'detail': 'Method not allowed'}}
    return json.dumps(body, separators=(',', ':'))


@error(500)
def error500(e):
    body = {'errors': {'detail': 'Internal server error'}}
    return json.dumps(body, separators=(',', ':'))


# Entry point ONLY when run locally. The docker setup uses gunicorn and this block will not be executed.
if __name__ == '__main__':
    run(host='localhost', port=8080)

app = bottle.default_app()
