# LocalGov

`LocalGov` is the governance module inherited by RipeHq, Departments, and
Switchboard configuration contracts. It supports a local governor, optional
fallback authority from the root RipeHq governor, and a block-based governance
transfer process.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/modules/LocalGov.vy)

## Authority model

For a child contract, `getGovernors()` can return two addresses:

1. the child's local `governance`; and
2. the current `governance()` read from its immutable RipeHq.

Either is accepted by `canGovern`. The RipeHq contract itself has no parent and
therefore exposes only its own governor.

Child local governance may be relinquished to zero, leaving RipeHq governance
as the remaining authority. Top-level RipeHq governance cannot be set to zero or
relinquished.

## Governance transfer

`startGovernanceChange` records a proposed governor and confirmation block.
Nonzero successors must be contracts and must not already be one of the current
governors. Once the delay has elapsed, a nonzero successor must confirm its own
appointment. For a permitted child relinquishment, an existing governor
confirms the zero-address change.

Pending transfers may be cancelled by a current governor. The governance-change
delay cannot be changed while a transfer is pending, and every new delay must be
different from the current value and within the immutable bounds.

## One-time RipeHq setup

RipeHq begins with a temporary setup governor and no governance-change delay.
Its first transition must use `finishRipeHqSetup`, which:

- requires the temporary governor;
- requires a nonzero contract as the permanent governor;
- can run only while `numGovChanges == 0`; and
- installs either the supplied valid delay or the immutable minimum.

The module rejects an ordinary `startGovernanceChange` for top-level RipeHq
before this setup transition. This prevents bypassing the one-time setup path
and leaving the root delay uninitialized.

## Clock and operational cautions

Governance delays use EVM `block.number`; their elapsed wall-clock time depends
on the chain. A change to RipeHq's governor immediately changes the fallback
governor observed by every child `LocalGov` module.

<!-- BEGIN GENERATED API REFERENCE: LocalGov -->
## Exact API reference

> Generated from `contracts/modules/LocalGov.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _initialGov, uint256 _minTimeLock, uint256 _maxTimeLock, uint256 _initialTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getGovernors()` | `view` | `address[]` |
| `getRipeHqFromGov()` | `view` | `address` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `hasPendingGovChange()` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `relinquishGov()` | `nonpayable` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `PendingGovernance(newGov: address, initiatedBlock: uint256, confirmBlock: uint256)`

<!-- END GENERATED API REFERENCE: LocalGov -->
