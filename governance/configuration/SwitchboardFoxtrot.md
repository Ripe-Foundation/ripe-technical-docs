# SwitchboardFoxtrot

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/SwitchboardFoxtrot.vy)

`SwitchboardFoxtrot` is the governance adapter for `RipeReserveEngine` and
`RipeReserveVesting`. It resolves those contracts through RipeHq IDs 26 and 27,
respectively, and refuses zero or non-contract targets.

## Construction and authority

Construction binds RipeHq and accepts a temporary local-governor address. Zero
is allowed, in which case only the current RipeHq governor is initially active.
It initializes local governance by inheriting RipeHq's immutable minimum and
maximum governance-delay bounds; because the supplied local initial delay is
zero, `LocalGov` clamps the installed `govChangeTimeLock` to that inherited
minimum. The separate Foxtrot action timelock uses the supplied minimum and
maximum, starts with an action delay of zero, and sets expiration to the
maximum.

The inherited ABI exposes `finishRipeHqSetup`, but that route is permanently
inapplicable to Foxtrot because its `LocalGov` module is initialized with a
nonzero parent RipeHq; the route is usable only on a top-level `LocalGov` host
(`RIPE_HQ_FOR_GOV == 0`). Local-governor replacement uses the ordinary
`startGovernanceChange`/`confirmGovernanceChange` flow and the installed
governance-change delay.

Every Foxtrot action requires `canGovern`, so either its current local governor
or the current RipeHq governor may act under the inherited authority rules. The
engine and vesting contract separately require Foxtrot to remain a registered
Switchboard for their respective writes.

## Timelocked changes

Two changes use pending action IDs:

- a complete `ReserveEngineConfig`, validated both when proposed and immediately
  before execution; and
- replacement of `RipeReserveVesting.remainingAllocationBudget`, including a
  zero budget.

`executePendingAction` returns false while an action is immature. If it is
expired, execution cancels the stored payload and returns false. A confirmed
action dispatches according to its recorded `ActionType`, clears the payload
and type, and returns true. Governance may also cancel a pending action
explicitly.

## Immediate operational controls

The following governance operations do not create Foxtrot pending actions:

- enable or disable new acquisitions;
- install or cancel a one-epoch payout-rate override;
- start or stop the engine;
- change the payment token while the engine is stopped; and
- cancel an already pending Foxtrot action.

Pause state is managed outside Foxtrot. Resolve RipeHq ID 26 or 27 and pass
that target to
[`SwitchboardCharlie.pause`](SwitchboardCharlie.md#exact-api-reference).
Charlie governance may pause or unpause, while a MissionControl lite signer may
only pause. The target's inherited `DeptBasics.pause` in turn requires Charlie
to be currently registered as a Switchboard.

Foxtrot asks the engine to validate each relevant request before forwarding it.
A zero genesis block passed to `startReserveEngine` is resolved by the engine to
the current native block. A zero override epoch resolves inside the engine to
the earliest uncommitted epoch, and Foxtrot emits the resolved epoch.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardFoxtrot -->
## Exact API reference

> Generated from `contracts/config/SwitchboardFoxtrot.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `actionType(uint256 arg0)` | `view` | `uint256` | — |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `cancelReserveEngineRateOverride()` | `nonpayable` | — | — |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `executePendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `expiration()` | `view` | `uint256` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `isExpired(uint256 _actionId)` | `view` | `bool` | — |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingEngineConfig(uint256 arg0)` | `view` | `(uint256 paymentCapPerEpoch, uint256 minPaymentAmount, uint256 maxAllInPayoutRate, uint256 seedBasePayoutRate, uint256 uHighBps, uint256 uLowBps, uint256 minUpBps, uint256 maxUpBps, uint256 minDownBps, uint256 maxDownBps, uint256 decayBps, uint256 maxDecayEpochs, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 epochLength)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingVestingAllocationBudget(uint256 arg0)` | `view` | `uint256` | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setCanAcquireRipe(bool _canAcquireRipe)` | `nonpayable` | — | — |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setReserveEngineConfig((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _config)` | `nonpayable` | `uint256` | `uint256` |
| `setReserveEnginePaymentToken(address _token)` | `nonpayable` | — | — |
| `setReserveEngineRateOverride(uint256 _targetBasePayoutRate, uint256 _targetEpoch)` | `nonpayable` | `uint256` | `uint256` |
| `setReserveVestingRemainingAllocationBudget(uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `startReserveEngine(uint256 _genesisBlock, uint256 _epochLength)` | `nonpayable` | — | — |
| `stopReserveEngine()` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `PendingReserveEngineConfigSet` | `uint256 actionId, uint256 confirmationBlock, uint256 paymentCapPerEpoch, uint256 minPaymentAmount, uint256 maxAllInPayoutRate, uint256 seedBasePayoutRate, uint256 uHighBps, uint256 uLowBps, uint256 minUpBps, uint256 maxUpBps, uint256 minDownBps, uint256 maxDownBps, uint256 decayBps, uint256 maxDecayEpochs, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 epochLength` |
| `PendingReserveVestingAllocationBudgetSet` | `uint256 actionId, uint256 confirmationBlock, uint256 amount` |
| `ReserveEngineCanAcquireRipeSet` | `bool canAcquireRipe` |
| `ReserveEngineConfigExecuted` | `uint256 actionId` |
| `ReserveEnginePaymentTokenSet` | `address token indexed` |
| `ReserveEngineRateOverrideCancelled` | `uint256 targetEpoch indexed, uint256 targetBasePayoutRate` |
| `ReserveEngineRateOverrideSet` | `uint256 targetEpoch indexed, uint256 targetBasePayoutRate` |
| `ReserveEngineStarted` | `uint256 genesisBlock, uint256 epochLength` |
| `ReserveVestingAllocationBudgetExecuted` | `uint256 actionId` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `ReserveEngineConfig(paymentCapPerEpoch: uint256, minPaymentAmount: uint256, maxAllInPayoutRate: uint256, seedBasePayoutRate: uint256, uHighBps: uint256, uLowBps: uint256, minUpBps: uint256, maxUpBps: uint256, minDownBps: uint256, maxDownBps: uint256, decayBps: uint256, maxDecayEpochs: uint256, maxVestingBonus: uint256, minVestingLength: uint256, maxVestingLength: uint256, epochLength: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `already running`
- `cannot cancel action`
- `invalid action`
- `invalid config`
- `invalid engine`
- `invalid epoch length`
- `invalid payment token`
- `invalid rate override`
- `invalid vesting`
- `no change`
- `no perms`
- `no rate override`
- `not configured`
- `not running`

<!-- END GENERATED API REFERENCE: SwitchboardFoxtrot -->
