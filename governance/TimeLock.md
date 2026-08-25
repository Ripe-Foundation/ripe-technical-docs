# TimeLock

`TimeLock` is the reusable action-delay module inherited by Switchboard
configuration contracts. It assigns one-based action IDs and stores an
initiation block, confirmation block, and expiration block for each action.

> The module is implementation source. The host contract owns action payloads,
> permission checks, execution-time validation, and cancellation events.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/modules/TimeLock.vy)

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
## Exact API reference

> Generated from declarations in `contracts/modules/TimeLock.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def canConfirmAction(_actionId: uint256) -> bool`
- `def getActionConfirmationBlock(_actionId: uint256) -> uint256`
- `def hasPendingAction(_actionId: uint256) -> bool`
- `def isExpired(_actionId: uint256) -> bool`
- `def isValidActionTimeLock(_newTimeLock: uint256) -> bool`
- `def maxActionTimeLock() -> uint256`
- `def minActionTimeLock() -> uint256`
- `def setActionTimeLock(_newTimeLock: uint256) -> bool`
- `def setActionTimeLockAfterSetup(_newTimeLock: uint256 = 0) -> bool`
- `def setExpiration(_expiration: uint256) -> bool`

### Events declared by this source

- `ActionTimeLockSet(newTimeLock: uint256, prevTimeLock: uint256)`
- `ExpirationSet(expiration: uint256)`

### Structs declared by this source

- `PendingAction(initiatedBlock: uint256, confirmBlock: uint256, expiration: uint256)`

<!-- END GENERATED API REFERENCE: TimeLock -->
