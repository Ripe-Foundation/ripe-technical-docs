# TimeLock

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/modules/TimeLock.vy)

`TimeLock` is the reusable action-delay module inherited by Switchboard
configuration contracts. It assigns one-based action IDs and stores an
initiation block, confirmation block, and expiration block for each action.

> The module is implementation source. The host contract owns action payloads,
> permission checks, execution-time validation, and cancellation events.

## Action window

For a new action:

```text
confirmBlock = block.number + actionTimeLock
expirationBlock = confirmBlock + expiration
```

The action is confirmable when
`confirmBlock <= block.number < expirationBlock`. Reaching the expiration block
makes it expired. Confirmation and cancellation clear the stored
`PendingAction`; payload cleanup remains the host's responsibility.

The module guards both additions against `uint256` overflow before storing the
action.

## Configuration invariants

The constructor fixes immutable minimum and maximum action delays. Current
configuration must satisfy:

- `MIN_ACTION_TIMELOCK <= actionTimeLock <= MAX_ACTION_TIMELOCK`;
- `actionTimeLock <= expiration`;
- `0 < expiration <= MAX_ACTION_TIMELOCK`; and
- a new action delay must differ from the current value.

`setActionTimeLockAfterSetup` is the one-time transition from delay zero to the
supplied valid value or the immutable minimum. Changing the configured delay or
expiration does not rewrite already-created `PendingAction` records.

## Host integration

The host normally stores an action-type tag and payload under the returned
action ID, emits a proposal event using `getActionConfirmationBlock`, and later
calls `_confirmAction`. A host should re-read state and revalidate any
state-sensitive invariant at execution rather than relying only on proposal-time
checks.

Switchboards use this pattern for debt-term rails, current vault pointers,
replacement targets, and irreversible point-accrual disables.

## Clock semantics

All delays use EVM `block.number`, not timestamps or Ledger's configurable
action-block source.

<!-- BEGIN GENERATED API REFERENCE: TimeLock -->
## Exact source-declared API reference

> Generated from declarations in `contracts/modules/TimeLock.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers deployment/module initializers, external functions and their default-argument call forms, compiler-generated public getters inferred from declarations, events, flags, constants, structs, and source-declared revert reasons found in this source. It does not claim a composed host ABI or canonical runtime selector surface.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__(_minActionTimeLock: uint256, _maxActionTimeLock: uint256, _initialTimeLock: uint256, _expiration: uint256)`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def canConfirmAction(_actionId: uint256) -> bool` | `1` | `view` | `bool` |
| `def getActionConfirmationBlock(_actionId: uint256) -> uint256` | `1` | `view` | `uint256` |
| `def hasPendingAction(_actionId: uint256) -> bool` | `1` | `view` | `bool` |
| `def isExpired(_actionId: uint256) -> bool` | `1` | `view` | `bool` |
| `def isValidActionTimeLock(_newTimeLock: uint256) -> bool` | `1` | `view` | `bool` |
| `def maxActionTimeLock() -> uint256` | `0` | `view` | `uint256` |
| `def minActionTimeLock() -> uint256` | `0` | `view` | `uint256` |
| `def setActionTimeLock(_newTimeLock: uint256) -> bool` | `1` | `nonpayable` | `bool` |
| `def setActionTimeLockAfterSetup(_newTimeLock: uint256 = 0) -> bool` | `0–1` | `nonpayable` | `bool` |
| `def setExpiration(_expiration: uint256) -> bool` | `1` | `nonpayable` | `bool` |

### Source-declared call forms

Each row is one source-level call form permitted by the declaration's trailing defaults. These signatures use Vyper source notation; they are not canonical ABI signatures or selector-hash preimages. Without a tracked compiled ABI, this table does not claim the exact runtime selector surface.

| Source call form | Mutability | Returns |
| --- | --- | --- |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` |
| `isExpired(uint256 _actionId)` | `view` | `bool` |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |

### Compiler-generated public getters

| Getter | Mutability | Source return type |
| --- | --- | --- |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `expiration()` | `view` | `uint256` |
| `pendingActions(uint256 key1)` | `view` | `PendingAction` |

### Events declared by this source

- `ActionTimeLockSet(newTimeLock: uint256, prevTimeLock: uint256)`
- `ExpirationSet(expiration: uint256)`

### Structs declared by this source

- `PendingAction(initiatedBlock: uint256, confirmBlock: uint256, expiration: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `action confirmation overflow`
- `action expiration overflow`
- `already set`
- `failed to set initial time lock`
- `invalid expiration`
- `invalid time lock`
- `invalid time lock boundaries`
- `no perms`

<!-- END GENERATED API REFERENCE: TimeLock -->
