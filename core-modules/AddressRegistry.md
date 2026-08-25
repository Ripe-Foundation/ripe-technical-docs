# AddressRegistry

`AddressRegistry` is an inherited registry module used by `RipeHq`,
`Switchboard`, `VaultBook`, and other registry contracts. It supplies stable
numeric IDs, current address lookup, version metadata, and a block-based
propose/confirm/cancel lifecycle.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/registries/modules/AddressRegistry.vy)

## Data model

Registry IDs are one-based. `numAddrs` stores the next ID, so
`getNumAddrs()` returns `numAddrs - 1`.

`AddressInfo` records the current address, version, last-modified timestamp, and
description for an ID. `addrToRegId` contains only current reverse mappings.
Updating or disabling an entry clears the old address's reverse mapping.

An ID remains structurally valid after its address is disabled:
`isValidRegId(id)` checks the allocated ID range, while `getAddr(id)` may return
zero. Consumers that require a current implementation must check both the ID and
its current address.

## Change lifecycle

| Operation | Proposal key | Confirmation result |
| --- | --- | --- |
| Add | New address | Allocates the next ID and version 1 |
| Update | Existing ID | Repoints the ID and increments its version |
| Disable | Existing ID | Sets the current address to zero and increments its version |

Every proposal stores its initiation and confirmation blocks. Confirmation is
allowed once `block.number >= confirmBlock`. The implementation revalidates the
requested state at confirmation; if it is no longer valid, it clears the
pending record and returns a failure value rather than installing stale state.
Cancellation clears the pending record and emits the corresponding audit event.

The module does not keep an address-history array. Historical versions are
observable through events, while storage exposes the current address and
monotonic version number.

## Timelock configuration

The constructor fixes immutable minimum and maximum registry delays and accepts
an optional initial delay. `setRegistryTimeLock` requires governance and rejects
unchanged or out-of-range values. `setRegistryTimeLockAfterSetup` is a one-time
transition from a zero setup delay to either the supplied value or the immutable
minimum.

Registry delays use EVM `block.number`. Their wall-clock duration is therefore
chain-specific.

## Host responsibilities

The host contract must:

- gate the internal start, confirm, cancel, update, and disable functions;
- add any component-specific replacement checks;
- decide whether an allocated-but-disabled ID is acceptable; and
- enforce custody or interface invariants that the generic registry cannot
  know about.

`VaultBook`, for example, adds fund checks and specialized RipeGov/StabilityPool
interface checks around these generic operations.

<!-- BEGIN GENERATED API REFERENCE: AddressRegistry -->
## Exact API reference

> Generated from declarations in `contracts/registries/modules/AddressRegistry.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def getAddr(_regId: uint256) -> address`
- `def getAddrDescription(_regId: uint256) -> String[64]`
- `def getAddrInfo(_regId: uint256) -> AddressInfo`
- `def getLastAddr() -> address`
- `def getLastRegId() -> uint256`
- `def getNumAddrs() -> uint256`
- `def getRegId(_addr: address) -> uint256`
- `def getRegistryDescription() -> String[28]`
- `def isValidAddr(_addr: address) -> bool`
- `def isValidAddressDisable(_regId: uint256) -> bool`
- `def isValidAddressUpdate(_regId: uint256, _newAddr: address) -> bool`
- `def isValidNewAddress(_addr: address) -> bool`
- `def isValidRegId(_regId: uint256) -> bool`
- `def isValidRegistryTimeLock(_numBlocks: uint256) -> bool`
- `def maxRegistryTimeLock() -> uint256`
- `def minRegistryTimeLock() -> uint256`
- `def setRegistryTimeLock(_numBlocks: uint256) -> bool`
- `def setRegistryTimeLockAfterSetup(_numBlocks: uint256 = 0) -> bool`

### Events declared by this source

- `NewAddressPending(addr: indexed(address), description: String[64], confirmBlock: uint256, registry: String[28])`
- `NewAddressConfirmed(addr: indexed(address), regId: uint256, description: String[64], registry: String[28])`
- `NewAddressCancelled(description: String[64], addr: indexed(address), initiatedBlock: uint256, confirmBlock: uint256, registry: String[28])`
- `AddressUpdatePending(regId: uint256, description: String[64], newAddr: indexed(address), prevAddr: indexed(address), version: uint256, confirmBlock: uint256, registry: String[28])`
- `AddressUpdateConfirmed(regId: uint256, description: String[64], newAddr: indexed(address), prevAddr: indexed(address), version: uint256, registry: String[28])`
- `AddressUpdateCancelled(regId: uint256, description: String[64], newAddr: indexed(address), prevAddr: indexed(address), initiatedBlock: uint256, confirmBlock: uint256, registry: String[28])`
- `AddressDisablePending(regId: uint256, description: String[64], addr: indexed(address), version: uint256, confirmBlock: uint256, registry: String[28])`
- `AddressDisableConfirmed(regId: uint256, description: String[64], addr: indexed(address), version: uint256, registry: String[28])`
- `AddressDisableCancelled(regId: uint256, description: String[64], addr: indexed(address), initiatedBlock: uint256, confirmBlock: uint256, registry: String[28])`
- `RegistryTimeLockModified(newTimeLock: uint256, prevTimeLock: uint256, registry: String[28])`

### Structs declared by this source

- `AddressInfo(addr: address, version: uint256, lastModified: uint256, description: String[64])`
- `PendingNewAddress(description: String[64], initiatedBlock: uint256, confirmBlock: uint256)`
- `PendingAddressUpdate(newAddr: address, initiatedBlock: uint256, confirmBlock: uint256)`
- `PendingAddressDisable(initiatedBlock: uint256, confirmBlock: uint256)`

<!-- END GENERATED API REFERENCE: AddressRegistry -->
