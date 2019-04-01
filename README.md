![DIF Logo](https://raw.githubusercontent.com/decentralized-identity/decentralized-identity.github.io/master/images/logo-small.png)

# Universal Resolver Driver: did:fct

This is a [Universal Resolver](https://github.com/decentralized-identity/universal-resolver/) driver for **did:fct** identifiers.

## Specifications

* [Decentralized Identifiers](https://w3c-ccg.github.io/did-spec/)
* [Factom DID Method Specification](DID-Method-factom.md)

## Example DIDs

```
did:factom:
```

## Build and Run (Docker)

```
docker build -f ./docker/Dockerfile . -t universalresolver/driver-did-factom
docker run -p 8080:8080 universalresolver/driver-did-factom
curl -X GET http://localhost:8080/1.0/identifiers/did:factom:
```

## Build and Run (python)

1. First, get the driver's dependencies `pip3 install -r requirements.txt`
1. Then, run the driver `python3 did_fct_driver.py`
1. The driver will now be accessible to curl at `localhost:8080`

## Driver Environment Variables

The driver recognizes the following environment variables:

### `uniresolver_driver_did_factom_factomConnection`

* Specifies the type of connection used to interact with the Factom blockchain:`factomd` or `harmony`. (Note: the `harmony` connection type only supports resolution of mainnet DIDs at this time)
* Default value: `factomd`
 
### `uniresolver_driver_did_factom_rpcUrlMainnet`

* Specifies the JSON-RPC URL of a factomd instance running on mainnet
* Default value: `https://api.factomd.net`

### `uniresolver_driver_did_factom_rpcUrlTestnet`

* Specifies the JSON-RPC URL of a factomd instance running on the community testnet
* Default value: `https://dev.factomd.net`

### `uniresolver_driver_did_factom_harmonyApiUrl`

* Specifies the URL of a Factom Harmony Connect API
* Default value: `https://api.factom.com/v1`

### `uniresolver_driver_did_factom_harmonyApiAppId`

* Specifies the `app_id` to be sent in request headers to the Factom Harmony Connect API
* Default value: ``

### `uniresolver_driver_did_factom_harmonyApiAppKey`

* Specifies the `app_key` to be sent in request headers to the Factom Harmony Connect API
* Default value: ``

 
## Driver Metadata

The driver returns the following metadata in addition to a DID document:

* `name`: The array of partial names that the identity was initialized with.
* `stage`: The current state of the DID on the blockchain, could be any of the following:
    * `pending`: The identity chain has been submitted for creation, and is waiting to be included in a Directory Block
    * `factom`: The identity chain has been created and included in a Directory Block (i.e. confirmed)
    * `anchored`: The identity chain has been created and confirmed, and the directory block that it was included in has been anchored to Bitcoin and/or Ethereum
* `createdHeight`: The Directory Block height that the identity chain was created at (null if `stage` is `pending`)
* `createdTime`: The time of the identity's creation (null if `stage` is `pending`)
