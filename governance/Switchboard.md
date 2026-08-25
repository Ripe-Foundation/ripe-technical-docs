# Switchboard

`Switchboard` is the registry of configuration and operational authority
contracts. Contracts currently registered here are recognized by `Addys` as
Switchboard addresses and can call the configuration surfaces exposed by
MissionControl and shared Department modules.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/registries/Switchboard.vy)

## Composition

Switchboard composes `LocalGov`, `AddressRegistry`, `Addys`, and `DeptBasics`.
It cannot mint GREEN or RIPE. Its registry starts with setup delay zero and must
be finalized to a valid delay after bootstrap.

`isSwitchboardAddr(addr)` is a current registry-membership check. When a
configuration implementation is replaced or disabled, the old address no
longer passes that check.

## Registry lifecycle

A recognized governor may propose, confirm, or cancel additions, updates, and
disables only while Switchboard is not paused. The generic registry timelock and
current-address semantics apply: an allocated ID can remain valid while its
current address is zero.

Configuration contracts generally have their own `LocalGov` and `TimeLock`
modules. Registration authorizes their selector surface; it does not eliminate
their internal governance, delay, validation, or directional-lite-access rules.

## Token blacklist forwarding

`setBlacklist(token, account, shouldBlacklist)` forwards a blacklist change to
the token contract. Its caller must be a currently registered Switchboard
address. This pass-through is not the same as RipeHq's
`canSetTokenBlacklist` query; the token implementation is responsible for its
own root permission check.

The blacklist forwarding path checks current caller registration directly. The
registry-management pause gate does not itself revoke already-registered
configuration contracts; removing or disabling a compromised configuration
address is the membership-level revocation.

## Operational cautions

- Registry IDs identify configuration roles, while the current address defines
  who can exercise them.
- Pausing Switchboard blocks its governance-managed registry changes but does
  not automatically pause every registered configuration contract.
- A configuration contract's lite actions are governed by MissionControl's
  iterable lite-signer set and that contract's own direction-specific checks.

<!-- BEGIN GENERATED API REFERENCE: Switchboard -->
## Exact API reference

> Generated from `contracts/registries/Switchboard.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minRegistryTimeLock, uint256 _maxRegistryTimeLock)`

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
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `cancelAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelNewAddressToRegistry(address _addr)` | `nonpayable` | `bool` |
| `confirmAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `confirmNewAddressToRegistry(address _addr)` | `nonpayable` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getAddr(uint256 _regId)` | `view` | `address` |
| `getAddrDescription(uint256 _regId)` | `view` | `string` |
| `getAddrInfo(uint256 _regId)` | `view` | `(address,uint256,uint256,string)` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getGovernors()` | `view` | `address[]` |
| `getLastAddr()` | `view` | `address` |
| `getLastRegId()` | `view` | `uint256` |
| `getNumAddrs()` | `view` | `uint256` |
| `getRegId(address _addr)` | `view` | `uint256` |
| `getRegistryDescription()` | `view` | `string` |
| `getRipeHq()` | `view` | `address` |
| `getRipeHqFromGov()` | `view` | `address` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `hasPendingGovChange()` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `isSwitchboardAddr(address _addr)` | `view` | `bool` |
| `isValidAddr(address _addr)` | `view` | `bool` |
| `isValidAddressDisable(uint256 _regId)` | `view` | `bool` |
| `isValidAddressUpdate(uint256 _regId, address _newAddr)` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidNewAddress(address _addr)` | `view` | `bool` |
| `isValidRegId(uint256 _regId)` | `view` | `bool` |
| `isValidRegistryTimeLock(uint256 _numBlocks)` | `view` | `bool` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `maxRegistryTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `minRegistryTimeLock()` | `view` | `uint256` |
| `numAddrs()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingAddrDisable(uint256 arg0)` | `view` | `(uint256,uint256)` |
| `pendingAddrUpdate(uint256 arg0)` | `view` | `(address,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingNewAddr(address arg0)` | `view` | `(string,uint256,uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `registryChangeTimeLock()` | `view` | `uint256` |
| `relinquishGov()` | `nonpayable` | — |
| `setBlacklist(address _tokenAddr, address _addr, bool _shouldBlacklist)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
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
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewAddressCancelled` | `string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `NewAddressConfirmed` | `address addr indexed, uint256 regId, string description, string registry` |
| `NewAddressPending` | `address addr indexed, string description, uint256 confirmBlock, string registry` |
| `RegistryTimeLockModified` | `uint256 newTimeLock, uint256 prevTimeLock, string registry` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

<!-- END GENERATED API REFERENCE: Switchboard -->
