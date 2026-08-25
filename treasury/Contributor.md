# Contributor

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/modules/Contributor.vy)

## Purpose

`Contributor` is the blueprint used by HumanResources to create an individual vesting agreement. Each instance stores its owner, manager, total compensation, vesting/cliff/unlock schedule, governance-vault deposit lock, claimed amount, and delayed key actions.

The initial economic schedule is set at construction. HumanResources revalidates proposed terms both when an action is initiated and when it is confirmed; a later authorized paycheck cancellation can reduce compensation and end the schedule early.

## Vesting and paychecks

`cashRipeCheck` calculates the currently vested but unclaimed amount. A zero amount or frozen contributor fails soft and returns zero. Otherwise HumanResources mints the RIPE and deposits it for the contributor into the dynamically selected current core RipeGov vault using the agreement's lock duration.

Vesting uses quotient-and-remainder arithmetic so the full compensation becomes vested at the terminal timestamp without permanently losing division dust. Terminal duration views return zero safely. The source constrains vesting length to preserve arithmetic safety.

## Transferring the governance-vault position

After the agreement unlock time, the owner or manager may call `initiateRipeTransfer(shouldCashCheck, vaultId)`. A zero vault ID resolves through HumanResources; a supplied ID must be a currently recognized current/historical RipeGov ID. The selected vault ID is stored with the pending action so confirmation transfers the same position that was approved.

Confirmation is available after the configurable key-action delay and transfers the contributor's in-vault RIPE position to the recorded owner while preserving the agreement's lock duration. The pending action is then cleared. Transfer initiation/confirmation cannot overlap a pending ownership change, and a frozen instance cannot initiate or confirm.

## Ownership and management

Ownership changes use a separate delayed initiate/confirm/cancel lifecycle. They cannot overlap a pending RIPE transfer. The owner can replace the manager and set the key-action delay within the constructor's minimum/maximum bounds; Switchboard can also replace the manager through the HumanResources modification hook. The ownership flow rejects invalid or redundant recipients and tracks completed changes with overflow-safe accounting.

The owner may establish supported governance delegation; the owner or manager may remove delegation. Switchboard can use the HumanResources modification hook to cancel sensitive actions, freeze/unfreeze the instance, or cancel the remaining paycheck under the contract's authority rules.

## Cancellation

`cancelPaycheck` ends the unpaid compensation path through HumanResources.
HumanResources returns the safely creditable reserve amount, can withdraw or
burn the contributor position when required, and updates reward and debt
housekeeping.

## Key events

- `RipeCheckCashed`
- `RipeTransferInitiated`, `RipeTransferConfirmed`, `RipeTransferCancelled`
- `OwnershipChangeInitiated`, `OwnershipChangeConfirmed`, `OwnershipChangeCancelled`
- `ManagerModified`, `KeyActionDelaySet`
- `DelegationModified`, `DelegationRemoved`
- `FreezeModified`, `RipePaycheckCancelled`

<!-- BEGIN GENERATED API REFERENCE: Contributor -->
## Exact API reference

> Generated from `contracts/modules/Contributor.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _owner, address _manager, uint256 _compensation, uint256 _startDelay, uint256 _vestingLength, uint256 _cliffLength, uint256 _unlockLength, uint256 _depositLockDuration, uint256 _minKeyActionDelay, uint256 _maxKeyActionDelay)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `confirmRipeTransfer(bool _shouldCashCheck)` | `0–1` | `_shouldCashCheck` |
| `initiateRipeTransfer(bool _shouldCashCheck, uint256 _vaultId)` | `0–2` | `_shouldCashCheck`, `_vaultId` |
| `removeDelegationFor(address _govAddr, address _recipient)` | `1–2` | `_recipient` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `cancelOwnershipChange()` | `nonpayable` | — |
| `cancelPaycheck()` | `nonpayable` | — |
| `cancelRipeTransfer()` | `nonpayable` | — |
| `cashRipeCheck()` | `nonpayable` | `uint256` |
| `changeOwnership(address _newOwner)` | `nonpayable` | — |
| `cliffTime()` | `view` | `uint256` |
| `compensation()` | `view` | `uint256` |
| `confirmOwnershipChange()` | `nonpayable` | — |
| `confirmRipeTransfer()` | `nonpayable` | — |
| `confirmRipeTransfer(bool _shouldCashCheck)` | `nonpayable` | — |
| `delegateTo(address _govAddr, address _recipient, uint256 _ratio)` | `nonpayable` | — |
| `depositLockDuration()` | `view` | `uint256` |
| `endTime()` | `view` | `uint256` |
| `getClaimable()` | `view` | `uint256` |
| `getRemainingUnlockLength()` | `view` | `uint256` |
| `getRemainingVestingLength()` | `view` | `uint256` |
| `getTotalVested()` | `view` | `uint256` |
| `getUnvestedComp()` | `view` | `uint256` |
| `hasPendingOwnerChange()` | `view` | `bool` |
| `hasPendingRipeTransfer()` | `view` | `bool` |
| `initiateRipeTransfer()` | `nonpayable` | — |
| `initiateRipeTransfer(bool _shouldCashCheck)` | `nonpayable` | — |
| `initiateRipeTransfer(bool _shouldCashCheck, uint256 _vaultId)` | `nonpayable` | — |
| `isFrozen()` | `view` | `bool` |
| `keyActionDelay()` | `view` | `uint256` |
| `manager()` | `view` | `address` |
| `numOwnerChanges()` | `view` | `uint256` |
| `owner()` | `view` | `address` |
| `pendingOwner()` | `view` | `(address,uint256,uint256)` |
| `pendingRipeTransfer()` | `view` | `(address,uint256,uint256)` |
| `pendingRipeTransferVaultId()` | `view` | `uint256` |
| `removeDelegationFor(address _govAddr)` | `nonpayable` | — |
| `removeDelegationFor(address _govAddr, address _recipient)` | `nonpayable` | — |
| `setIsFrozen(bool _shouldFreeze)` | `nonpayable` | `bool` |
| `setKeyActionDelay(uint256 _numBlocks)` | `nonpayable` | — |
| `setManager(address _newManager)` | `nonpayable` | — |
| `startTime()` | `view` | `uint256` |
| `totalClaimed()` | `view` | `uint256` |
| `unlockTime()` | `view` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `DelegationModified` | `address govAddr indexed, address recipient indexed, uint256 ratio` |
| `DelegationRemoved` | `address govAddr indexed, address recipient indexed` |
| `FreezeModified` | `bool isFrozen` |
| `KeyActionDelaySet` | `uint256 numBlocks` |
| `ManagerModified` | `address newManager indexed, address changedBy indexed` |
| `OwnershipChangeCancelled` | `address cancelledOwner indexed, address cancelledBy indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `OwnershipChangeConfirmed` | `address prevOwner indexed, address newOwner indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `OwnershipChangeInitiated` | `address prevOwner indexed, address newOwner indexed, uint256 confirmBlock` |
| `RipeCheckCashed` | `address owner indexed, address cashedBy indexed, uint256 amount` |
| `RipePaycheckCancelled` | `address owner indexed, uint256 forfeitedAmount, bool didReachCliff` |
| `RipeTransferCancelled` | `address recipient indexed, address cancelledBy indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `RipeTransferConfirmed` | `address recipient indexed, uint256 amount, address confirmedBy indexed, uint256 initiatedBlock` |
| `RipeTransferInitiated` | `address owner indexed, uint256 confirmBlock, address initiatedBy indexed` |

### Structs declared by this source

- `PendingRipeTransfer(recipient: address, initiatedBlock: uint256, confirmBlock: uint256)`
- `PendingOwnerChange(newOwner: address, initiatedBlock: uint256, confirmBlock: uint256)`

<!-- END GENERATED API REFERENCE: Contributor -->
