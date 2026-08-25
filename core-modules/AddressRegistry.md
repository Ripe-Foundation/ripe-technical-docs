# AddressRegistry

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/registries/modules/AddressRegistry.vy)

`AddressRegistry` is an inherited registry module used by `RipeHq`,
`Switchboard`, `VaultBook`, and other registry contracts. It supplies stable
numeric IDs, current address lookup, version metadata, and a block-based
propose/confirm/cancel lifecycle.

## Data model

Registry IDs are one-based. `numAddrs` stores the next ID, so
`getNumAddrs()` returns `numAddrs - 1`.

`AddressInfo` records the current address, version, last-modified timestamp, and
description for an ID. `addrToRegId` contains only current reverse mappings.
Updating or disabling an entry clears the old address's reverse mapping.
After that mapping is cleared, the old address may be proposed as a new entry;
confirmation allocates the next ID rather than restoring its former ID.

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

The generic module enforces these eligibility rules:

- an add target must be a nonzero contract address with no current reverse
  registration;
- an update requires an allocated ID and a target that satisfies the add rules
  and differs from the ID's current address; an allocated-but-disabled ID may
  therefore be repointed; and
- a disable requires an allocated ID whose current address is nonzero.

Every proposal stores its initiation and confirmation blocks. Confirmation is
allowed once `block.number >= confirmBlock`. Starting another proposal of the
same kind for the same key overwrites that pending record. Update and disable
records are separate, so both kinds may be pending for one ID at the same time.

Every confirmation revalidates its operation. An ineligible add, update, or
disable clears its pending record and returns a zero/false result. A disable's
pending record is keyed only by ID and does not retain the address seen at
proposal. If an update repoints that ID before the disable is confirmed, the
disable applies to the then-current address, and the confirmation event reports
that current address. Operators must therefore explicitly order or cancel
overlapping update and disable proposals; the registry does not bind a disable
to its proposal-time target.

An invalid confirmation emits neither a confirmation event nor a cancellation
or failure event. Event-only consumers must therefore reconcile pending storage
or call results rather than retaining a stale proposal indefinitely. Add and
update proposals also use independent keys, so one unregistered address can be
pending simultaneously as a new entry and as an update target. Whichever action
confirms first registers it; the other then clears silently as ineligible.

The reverse order matters too. Confirming a disable does not cancel an update
pending for the same ID. If that update's target remains eligible, its later
confirmation repoints and reactivates the allocated ID. Update and disable
confirmation and cancellation events read the relevant address from the ID's
then-current `AddressInfo`, not from a proposal-time address snapshot; update
confirmation also adjusts reverse mappings against that current predecessor.

Cancellation clears the selected pending record and emits the corresponding
audit event.

The module does not keep an address-history array. Historical versions are
observable through events, while storage exposes the current address and
monotonic version number.

## Timelock configuration

The constructor requires minimum, maximum, and initial-delay arguments. The
minimum must be nonzero and below the maximum, and the maximum cannot be the
largest `uint256`. The initial-delay value may be zero for setup; a nonzero
value must fall within the immutable bounds. `setRegistryTimeLock` requires
governance and rejects unchanged or out-of-range values.
`setRegistryTimeLockAfterSetup` is a one-time transition from a zero setup delay
to either the supplied value or the immutable minimum.

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
## Exact source-declared API reference

> Generated from declarations in `contracts/registries/modules/AddressRegistry.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers deployment/module initializers, external functions and their default-argument call forms, compiler-generated public getters inferred from declarations, events, flags, constants, structs, and source-declared revert reasons found in this source. It does not claim a composed host ABI or canonical runtime selector surface.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__(_minTimeLock: uint256, _maxTimeLock: uint256, _initialTimeLock: uint256, _registryStr: String[28])`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def getAddr(_regId: uint256) -> address` | `1` | `view` | `address` |
| `def getAddrDescription(_regId: uint256) -> String[64]` | `1` | `view` | `String[64]` |
| `def getAddrInfo(_regId: uint256) -> AddressInfo` | `1` | `view` | `AddressInfo` |
| `def getLastAddr() -> address` | `0` | `view` | `address` |
| `def getLastRegId() -> uint256` | `0` | `view` | `uint256` |
| `def getNumAddrs() -> uint256` | `0` | `view` | `uint256` |
| `def getRegId(_addr: address) -> uint256` | `1` | `view` | `uint256` |
| `def getRegistryDescription() -> String[28]` | `0` | `view` | `String[28]` |
| `def isValidAddr(_addr: address) -> bool` | `1` | `view` | `bool` |
| `def isValidAddressDisable(_regId: uint256) -> bool` | `1` | `view` | `bool` |
| `def isValidAddressUpdate(_regId: uint256, _newAddr: address) -> bool` | `2` | `view` | `bool` |
| `def isValidNewAddress(_addr: address) -> bool` | `1` | `view` | `bool` |
| `def isValidRegId(_regId: uint256) -> bool` | `1` | `view` | `bool` |
| `def isValidRegistryTimeLock(_numBlocks: uint256) -> bool` | `1` | `view` | `bool` |
| `def maxRegistryTimeLock() -> uint256` | `0` | `view` | `uint256` |
| `def minRegistryTimeLock() -> uint256` | `0` | `view` | `uint256` |
| `def setRegistryTimeLock(_numBlocks: uint256) -> bool` | `1` | `nonpayable` | `bool` |
| `def setRegistryTimeLockAfterSetup(_numBlocks: uint256 = 0) -> bool` | `0–1` | `nonpayable` | `bool` |

### Source-declared call forms

Each row is one source-level call form permitted by the declaration's trailing defaults. These signatures use Vyper source notation; they are not canonical ABI signatures or selector-hash preimages. Without a tracked compiled ABI, this table does not claim the exact runtime selector surface.

| Source call form | Mutability | Returns |
| --- | --- | --- |
| `getAddr(uint256 _regId)` | `view` | `address` |
| `getAddrDescription(uint256 _regId)` | `view` | `String[64]` |
| `getAddrInfo(uint256 _regId)` | `view` | `AddressInfo` |
| `getLastAddr()` | `view` | `address` |
| `getLastRegId()` | `view` | `uint256` |
| `getNumAddrs()` | `view` | `uint256` |
| `getRegId(address _addr)` | `view` | `uint256` |
| `getRegistryDescription()` | `view` | `String[28]` |
| `isValidAddr(address _addr)` | `view` | `bool` |
| `isValidAddressDisable(uint256 _regId)` | `view` | `bool` |
| `isValidAddressUpdate(uint256 _regId, address _newAddr)` | `view` | `bool` |
| `isValidNewAddress(address _addr)` | `view` | `bool` |
| `isValidRegId(uint256 _regId)` | `view` | `bool` |
| `isValidRegistryTimeLock(uint256 _numBlocks)` | `view` | `bool` |
| `maxRegistryTimeLock()` | `view` | `uint256` |
| `minRegistryTimeLock()` | `view` | `uint256` |
| `setRegistryTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` |

### Compiler-generated public getters

| Getter | Mutability | Source return type |
| --- | --- | --- |
| `addrInfo(uint256 key1)` | `view` | `AddressInfo` |
| `addrToRegId(address key1)` | `view` | `uint256` |
| `numAddrs()` | `view` | `uint256` |
| `pendingAddrDisable(uint256 key1)` | `view` | `PendingAddressDisable` |
| `pendingAddrUpdate(uint256 key1)` | `view` | `PendingAddressUpdate` |
| `pendingNewAddr(address key1)` | `view` | `PendingNewAddress` |
| `registryChangeTimeLock()` | `view` | `uint256` |

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

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `already set`
- `invalid addy`
- `invalid disable`
- `invalid time lock`
- `invalid update`
- `no pending`
- `no perms`
- `time lock not reached`

<!-- END GENERATED API REFERENCE: AddressRegistry -->
