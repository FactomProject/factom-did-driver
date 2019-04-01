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

This specification currently only supports Ethereum "mainnet" and "testnet", but can be extended to support any number of public or private Factom networks.

Example `factom` DIDs:
* `did:factom:`
* `did:factom:mainnet:`
* `did:factom:testnet:`

# DID Document

## Example
```
{
	"@context": "https://w3id.org/did/v1",
	"id": "did:factom:<CHAINID>",
	"publicKey": [{
		"id": "did:factom:<CHAINID>#key-0",
		"type": "ED25519SignatureVerification",
		"publicKeyHex": ""
	}, {
		"id": "did:factom:<CHAINID>#key-1",
		"type": "ED25519SignatureVerification",
		"publicKeyHex": ""
	}],
	"authentication": {
		"type": "ED25519SigningAuthentication",
		"publicKey": "did:factom:<CHAINID>#key-1"
	},
	"service": []
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
* For each key, add a `publicKey` element of type `ED25519SignatureVerification` to the DID
* For the lowest priority key (i.e. the last one in the active keys array), add an `authentication` element of type `ED25519SigningAuthenticationThreshold`, referencing the public key

## Update
The DID Document may be updated by creating a new key replacement entry in the DID's chain on Factom. The entry structure and validation rules can be seen in [this section](https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md#identity-key-replacement)[2] of the Factom Project's identity specification. A key replacement entry that resides outside of the identity's chain will not be taken into consideration when determining which keys were valid at a given block height.

## Delete (Revoke)
*TODO*

This method has yet to be specified, however, it will likely take the form of a signed entry that is put into the identity's chain, stating that the DID should be marked as *revoked*.

# Security Considerations
*TODO*

# Privacy Considerations
*TODO*

# Performance Considerations
*TODO*

# References
* [1] https://w3c-ccg.github.io/did-spec/
* [2] https://github.com/FactomProject/FactomDocs/blob/master/ApplicationIdentity.md
