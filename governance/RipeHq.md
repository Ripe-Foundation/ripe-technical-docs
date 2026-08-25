# RipeHq

`RipeHq` is the root protocol address registry and the authority registry for
minting and token-blacklist permissions. Its first three registry IDs are
created in the constructor for GREEN, Savings GREEN, and RIPE.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/registries/RipeHq.vy)

## Composition and bootstrap

RipeHq composes `LocalGov` and `AddressRegistry`. Construction:

1. installs a temporary nonzero governor;
2. initializes a zero-delay registry for setup;
3. registers GREEN at ID 1, Savings GREEN at ID 2, and RIPE at ID 3; and
4. enables the global minting circuit breaker.

The root governance module must later complete its one-time
`finishRipeHqSetup` transition and the registry must move from setup delay zero
to its configured minimum or another valid delay.

## Registry behavior

Only the current RipeHq `governance` address may propose, confirm, or cancel
registry additions, updates, and disables. IDs remain allocated after disable,
but disabled entries resolve to zero and their old reverse mapping is removed.

The convenience views `greenToken()`, `savingsGreen()`, and `ripeToken()` read
the current addresses at IDs 1, 2, and 3; they are not constructor-address
constants after registry updates.

## Department permissions

Each non-token registry ID can have an `HqConfig` containing its description and
permissions to mint GREEN, mint RIPE, or set a token blacklist. Changes use the
registry delay and are revalidated at confirmation.

Mint authorization is two-factor:

1. governance grants the permission in `HqConfig`; and
2. the current Department implementation reports the matching immutable
   capability through `canMintGreen()` or `canMintRipe()`.

`canMintGreen(addr)` and `canMintRipe(addr)` additionally require global minting
to be enabled and `addr` to be the current address of a registered ID. Tokens at
IDs 1–3 cannot receive Department configuration. These authorization checks do
not track cumulative issuance or enforce a token supply ceiling.

`canSetTokenBlacklist(addr)` requires current registry membership and the
corresponding `HqConfig` bit, but is independent of the minting circuit breaker.

## Circuit breaker and recovery

The root governor can toggle `mintEnabled`; no-op toggles revert. This disables
both GREEN and RIPE mint authorization checks without rewriting each
Department's configuration.

The governor can also recover the full balance of one or up to 20 ERC-20 assets
held directly by RipeHq. Recovery requires nonzero asset/recipient addresses, a
nonzero balance, and a successful token transfer.

## Security boundaries

- Registry membership is current, not historical.
- Registering a Department does not automatically grant mint or blacklist
  authority.
- A registry replacement immediately changes the implementation consulted for
  capability checks.
- RipeHq governance is the fallback governor for child `LocalGov` contracts, so
  changing it affects authority throughout the protocol.

<!-- BEGIN GENERATED API REFERENCE: RipeHq -->
## Exact API reference

> Generated from `contracts/registries/RipeHq.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _greenToken, address _savingsGreen, address _ripeToken, address _initialGov, uint256 _minGovTimeLock, uint256 _maxGovTimeLock, uint256 _minRegistryTimeLock, uint256 _maxRegistryTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `0–1` | `_numBlocks` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `addrInfo(uint256 arg0)` | `view` | `(address,uint256,uint256,string)` |
| `addrToRegId(address arg0)` | `view` | `uint256` |
| `canGovern(address _addr)` | `view` | `bool` |
| `canMintGreen(address _addr)` | `view` | `bool` |
| `canMintRipe(address _addr)` | `view` | `bool` |
| `canSetTokenBlacklist(address _addr)` | `view` | `bool` |
| `cancelAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelHqConfigChange(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelNewAddressToRegistry(address _addr)` | `nonpayable` | `bool` |
| `confirmAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `confirmHqConfigChange(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmNewAddressToRegistry(address _addr)` | `nonpayable` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getAddr(uint256 _regId)` | `view` | `address` |
| `getAddrDescription(uint256 _regId)` | `view` | `string` |
| `getAddrInfo(uint256 _regId)` | `view` | `(address,uint256,uint256,string)` |
| `getGovernors()` | `view` | `address[]` |
| `getLastAddr()` | `view` | `address` |
| `getLastRegId()` | `view` | `uint256` |
| `getNumAddrs()` | `view` | `uint256` |
| `getRegId(address _addr)` | `view` | `uint256` |
| `getRegistryDescription()` | `view` | `string` |
| `getRipeHqFromGov()` | `view` | `address` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `greenToken()` | `view` | `address` |
| `hasPendingGovChange()` | `view` | `bool` |
| `hasPendingHqConfigChange(uint256 _regId)` | `view` | `bool` |
| `hqConfig(uint256 arg0)` | `view` | `(string,bool,bool,bool)` |
| `initiateHqConfigChange(uint256 _regId, bool _canMintGreen, bool _canMintRipe, bool _canSetTokenBlacklist)` | `nonpayable` | — |
| `isValidAddr(address _addr)` | `view` | `bool` |
| `isValidAddressDisable(uint256 _regId)` | `view` | `bool` |
| `isValidAddressUpdate(uint256 _regId, address _newAddr)` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidHqConfig(uint256 _regId, bool _canMintGreen, bool _canMintRipe)` | `view` | `bool` |
| `isValidNewAddress(address _addr)` | `view` | `bool` |
| `isValidRegId(uint256 _regId)` | `view` | `bool` |
| `isValidRegistryTimeLock(uint256 _numBlocks)` | `view` | `bool` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `maxRegistryTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `minRegistryTimeLock()` | `view` | `uint256` |
| `mintEnabled()` | `view` | `bool` |
| `numAddrs()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pendingAddrDisable(uint256 arg0)` | `view` | `(uint256,uint256)` |
| `pendingAddrUpdate(uint256 arg0)` | `view` | `(address,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingHqConfig(uint256 arg0)` | `view` | `((string,bool,bool,bool),uint256,uint256)` |
| `pendingNewAddr(address arg0)` | `view` | `(string,uint256,uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `registryChangeTimeLock()` | `view` | `uint256` |
| `relinquishGov()` | `nonpayable` | — |
| `ripeToken()` | `view` | `address` |
| `savingsGreen()` | `view` | `address` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setMintingEnabled(bool _shouldEnable)` | `nonpayable` | — |
| `setRegistryTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `startAddNewAddressToRegistry(address _addr, string _description)` | `nonpayable` | `bool` |
| `startAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `startAddressUpdateToRegistry(uint256 _regId, address _newAddr)` | `nonpayable` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `AddressDisableCancelled` | `uint256 regId, string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressDisableConfirmed` | `uint256 regId, string description, address addr indexed, uint256 version, string registry` |
| `AddressDisablePending` | `uint256 regId, string description, address addr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `AddressUpdateCancelled` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressUpdateConfirmed` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, string registry` |
| `AddressUpdatePending` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `HqConfigChangeCancelled` | `uint256 regId, string description, bool canMintGreen, bool canMintRipe, bool canSetTokenBlacklist, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqConfigChangeConfirmed` | `uint256 regId, string description, bool canMintGreen, bool canMintRipe, bool canSetTokenBlacklist, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqConfigChangeInitiated` | `uint256 regId, string description, bool canMintGreen, bool canMintRipe, bool canSetTokenBlacklist, uint256 confirmBlock` |
| `MintingEnabled` | `bool isEnabled` |
| `NewAddressCancelled` | `string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `NewAddressConfirmed` | `address addr indexed, uint256 regId, string description, string registry` |
| `NewAddressPending` | `address addr indexed, string description, uint256 confirmBlock, string registry` |
| `RegistryTimeLockModified` | `uint256 newTimeLock, uint256 prevTimeLock, string registry` |
| `RipeHqFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `HqConfig(description: String[64], canMintGreen: bool, canMintRipe: bool, canSetTokenBlacklist: bool)`
- `PendingHqConfig(newHqConfig: HqConfig, initiatedBlock: uint256, confirmBlock: uint256)`

<!-- END GENERATED API REFERENCE: RipeHq -->
