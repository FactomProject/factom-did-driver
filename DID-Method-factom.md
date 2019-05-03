# Factom DID Method

30 March 2019

Sam Barnes <sam.barnes@factom.com>

Decentralized Identifiers (i.e. DIDs, see [1]) are a ledger agnostic standard to represent entities. In the Factom community, an Identity Chain (see [2]) is a construct that can be used to represent an individual or group of individuals and facilitate key management. An identity is initialized with the following:
* An array of partial names that together represent the identity's name. This could be human readable or otherwise semantically meaningful to the creator, however privacy and linkability should be taken into consideration when choosing names as these are persisted on chain
* An array of public ED25519 keys encoded in base58 with [a specific prefix and a checksum](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-key-pair)[2]. These keys represent a hierarchy and are ordered from highest to lowest priority, where key A is authorized to sign for the replacement of another key B so long as A is of the same or higher priority. Any key is allowed to sign for its own replacement.

# DID Method Name
The namestring that shall identify this DID method is: `factom`

A DID that uses this method MUST begin with the following prefix: `did:factom`. Per the DID specification, this string MUST be in lowercase. The remainder of the DID, after the prefix is specified below.

# Method Specific Identifier

The method specific name string is composed of an optional Factom network identifier with a `:` separator, followed by a hex-encoded Factom chain ID.

```
factom-did = "did:factom:" factom-specific-idstring
factom-specific-idstring = [ factom-network ":" ] factom-chain-id
factom-network = "mainnet" / "testnet"
factom-chain-id = 64*HEXDIG
```

The factom-chain-id is case-insensitive.

This specification currently only supports Factom "mainnet" and "testnet", but can be extended to support any number of public or private Factom networks.

Example `factom` DIDs:
* `did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758`
* `did:factom:mainnet:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758`
* `did:factom:testnet:`

# DID Document

## Example
```
{
  "redirect": null,
  "didDocument": {
    "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758",
    "service": [],
    "authentication": {
      "type": "Ed25519SignatureAuthentication2018",
      "publicKey": [
        "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-2"
      ]
    },
    "publicKey": [
      {
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-0",
        "type": "Ed25519VerificationKey2018",
        "publicKeyHex": "26d921a49a81d661ba5068c800cc59101725a8562873862cbdf2e90047cc645d"
      },
      {
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-1",
        "type": "Ed25519VerificationKey2018",
        "publicKeyHex": "4df876bf7cf71f00d350edfd121d3e2734a56cd359b71e2c23d00a8a85ae9979"
      },
      {
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-2",
        "type": "Ed25519VerificationKey2018",
        "publicKeyHex": "de0af63490f461f7d8431c77e60a9e85483f947e3b1f3b55c72679b8d2c1b3fa"
      }
    ],
    "@context": "https://w3id.org/did/v1"
  },
  "resolverMetadata": {
    "driverId": "did-factom",
    "driver": "HttpDriver",
    "duration": 1430,
    "didReference": {
      "didReference": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758",
      "did": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758",
      "method": "factom",
      "specificId": "f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758",
      "service": null,
      "path": null,
      "query": null,
      "fragment": null
    }
  },
  "methodMetadata": {
    "version": 1,
    "createdHeight": 186882,
    "name": [
      "Test",
      "v1"
    ]
    "stage": "factom",
    "publicKeyHistory": [
      {
        "type": "Ed25519VerificationKey2018",
        "activatedHeight": 186882,
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-0",
        "entryHash": "e2cad7c5898ad2508689267bd86a61408a091d48ac5631452d153db8c72ee8ac",
        "retiredHeight": null,
        "publicKeyHex": "26d921a49a81d661ba5068c800cc59101725a8562873862cbdf2e90047cc645d",
        "priority": 0
      },
      {
        "type": "Ed25519VerificationKey2018",
        "activatedHeight": 186882,
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-1",
        "entryHash": "e2cad7c5898ad2508689267bd86a61408a091d48ac5631452d153db8c72ee8ac",
        "retiredHeight": null,
        "publicKeyHex": "4df876bf7cf71f00d350edfd121d3e2734a56cd359b71e2c23d00a8a85ae9979",
        "priority": 1
      },
      {
        "activatedHeight": 186882,
        "entryHash": "e2cad7c5898ad2508689267bd86a61408a091d48ac5631452d153db8c72ee8ac",
        "retiredHeight": 186883,
        "publicKeyHex": "8ff6c30d9ad24512933ca96220411b117f0a15e932b88be3931164622e583abd",
        "priority": 2
      },
      {
        "activatedHeight": 186883,
        "entryHash": "908955fefb66741a392eb8ed701554126780c2ee70f77e48487da14821d85159",
        "retiredHeight": 186884,
        "publicKeyHex": "cf459062261dfa3386b8db5ddbd691032d5bb8c3b64fb0c795160740ccf6efca",
        "priority": 2
      },
      {
        "type": "Ed25519VerificationKey2018",
        "activatedHeight": 186884,
        "id": "did:factom:f26e1c422c657521861ced450442d0c664702f49480aec67805822edfcfee758#key-2",
        "entryHash": "9b70f0beb52b337289ec67eb3e558cb87682d3cce534891bc1133125e67b3f67",
        "retiredHeight": null,
        "publicKeyHex": "de0af63490f461f7d8431c77e60a9e85483f947e3b1f3b55c72679b8d2c1b3fa",
        "priority": 2
      }
    ]
  }
}

```

## JSON-LD Context Definition

*TODO*

# CRUD Operation Definitions

## Create (Register)
To create a `factom` DID, a chain must be created on a supported Factom network, and that chain's first entry MUST conform to the structure defined in [this section](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-chain)[2] of the Factom Project's identity specification. Although possible, the entity identified by the DID is not necessarily the holder of the Entry Credit private key that paid for the chain creation. Rather, the identity represents a person or group of people that control the private keys corresponding to the public keys in the hierarchy.

## Read (Resolve)
To construct a valid DID document from a `factom` DID, the following steps are performed:

* Determine the Factom network identifier (`"mainnet"` or `"testnet"`). If no network identifier is explicitly provided, then `"mainnet"` is assumed.
* Ensure that the first entry in the identity's chain conforms to the structure laid out in [this section](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-chain)[2] of the Factom Project's identity specification. The array of keys that the chain was initialized with become the hierarchical set of keys that can control and sign on behalf of the identity. The array is ordered from highest to lowest priority.
* Apply the following rules to each entry in the identity's chain (in the order that they appear within their blocks):
	* The entry MUST strictly follow the External ID format specified [here](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-key-replacement)[2]
	* Old key MUST be currently active for the identity of interest
	* New key MUST have never been active for the identity of interest (for any priority level)
	* Signer key MUST be currently active for the identity of interest
	* Signer key MUST be of the same or higher priority than the old key
	* The signature MUST be able to be verified with the signer key and the message `<chain-id> + <old-key-string> + <new-key-string>` where each of the strings are concatenated together
	* If the above are all true, the new key replaces the old key at the same priority level and is now part of the active set of keys.
* Once all entry blocks for the identity's chain have been parsed in their entirety, the resulting set of keys are considered currently active for the DID
* For each currently active key, add a `publicKey` element of type `Ed25519VerificationKey2018` to the DID
* For the lowest priority key (i.e. the last one in the active keys array), add an `authentication` element of type `Ed25519SignatureAuthentication2018`, referencing the public key

## Update
The DID Document may be updated by creating a new key replacement entry in the DID's chain on Factom. The entry structure and validation rules can be seen in [this section](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-key-replacement)[2] of the Factom Project's identity specification. A key replacement entry that resides outside of the identity's chain will not be taken into consideration when determining which keys were valid at a given block height.

## Delete (Revoke)
*TODO*

This method has yet to be specified, however, it will likely take the form of a signed entry that is put into the identity's chain, stating that the DID should be marked as *revoked*.

# Security Considerations
*TODO*

# Recovery From Key Compromise
Factom DID's have a hierarchical structure of public keys, where `#key-0` is the highest priority and `#key-n` the lowest. A key replacement can be authorized by any key at the same or higher priority. Such a scheme allows for an entity to store their keys in various levels of security. For example:
- `#key-0` - in cold storage
- `#key-1` - on an airgapped machine
- `#key-2` - used in applications (a.k.a. the hot key)

If the hot key is lost or compromised, the other two higher priority keys are able to authorize a replacement.

# Privacy Considerations
*TODO*

# Performance Considerations
*TODO*

# References
* [1] https://w3c-ccg.github.io/did-spec/
* [2] https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md
