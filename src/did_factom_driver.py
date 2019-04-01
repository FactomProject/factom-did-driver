import bottle
import consts
import datetime
import factomd_jsonrpc_parser
import harmony_connect_parser
import json
from bottle import error, get, hook, post, put, request, route, run
from harmony_connect_client.rest import ApiException
from validation import IdentityNotFoundException


@hook('before_request')
def strip_path():
    """Strip trailing '/' on all requests. '/foo' and /foo/' are two unique endpoints in bottle"""
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@get('/health')
def health_check():
    return {'data': 'Healthy!'}


@get('/1.0/identifiers/did\:factom\:<identity_chain_id>')
def resolve(identity_chain_id):
    try:
        # TODO:
        # identity, active_keys = factomd_jsonrpc_parser.get_keys(identity_chain_id)
        identity, active_keys = harmony_connect_parser.get_keys(identity_chain_id)
    except IdentityNotFoundException:
        bottle.abort(404)
    except ApiException:
        bottle.abort(500)  # Failed to make API call for some reason

    did = consts.DID_PREFIX + identity_chain_id
    key_count = len(active_keys)
    public_keys = [None] * key_count
    for i, key in enumerate(active_keys.values()):
        key['id'] = '{}#key-{}'.format(did, i)
        key['type'] = consts.DID_PUBLIC_KEY_TYPE
        public_keys[key['priority']] = key
        del key['priority']

    did_document = {
        '@context': consts.DID_CONTEXT,
        'id': did,
        'service': [],
        'publicKey': public_keys,
        'authentication': {
            'type': consts.DID_AUTHENTICATION_TYPE,
            'publicKey': '{}#key-{}'.format(did, key_count - 1)
        }
    }

    return {'didDocument': did_document, 'methodMetadata': identity }


@error(400)
def error400(error):
    body = {'errors': {'detail': 'Bad request'}}
    return json.dumps(body, separators=(',', ':'))


@error(404)
def error404(error):
    body = {'errors': {'detail': 'Page not found'}}
    return json.dumps(body, separators=(',', ':'))


@error(405)
def error405(error):
    body = {'errors': {'detail': 'Method not allowed'}}
    return json.dumps(body, separators=(',', ':'))


@error(500)
def error500(error):
    body = {'errors': {'detail': 'Internal server error'}}
    return json.dumps(body, separators=(',', ':'))


if __name__ == '__main__':
    run(host='localhost', port=8080)

app = bottle.default_app()
