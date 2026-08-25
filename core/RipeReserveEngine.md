# RipeReserveEngine

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/RipeReserveEngine.vy)

`RipeReserveEngine` exchanges a configured ERC-20 payment asset for RIPE
allocations whose settlement is recorded by `RipeReserveVesting`. It snapshots
each epoch's payout and vesting terms, applies a bounded utilization controller,
and mints RIPE only when vested claims are settled.

## Construction and authority

Construction binds RipeHq, validates and scales the payment token, validates the
initial engine configuration, and initializes the department paused with RIPE
mint capability but no GREEN mint capability. Registered Switchboards control
engine configuration, acquisition enablement, start/stop, payment-token changes,
and one-shot rate overrides. The intended governance surface is
[`SwitchboardFoxtrot`](../governance/configuration/SwitchboardFoxtrot.md).

Mint readiness is version-bound. The engine must still occupy RipeHq ID 26; the
vesting contract at ID 27 must be a contract, unpaused, and bound to the same
RipeHq; RipeHq must authorize this engine to mint RIPE; and the current RIPE
token must be a contract bound to that RipeHq and unpaused. Acquisition also
requires a valid EndaomentFunds contract.

## Acquisition and quoting

`previewAcquireRipe` derives the candidate epoch and payout without committing
state. Its `available` flag also checks the current pause, acquisition, budget,
and mint-readiness gates, but a preview is not a reservation. Callers pass the
expected epoch and resolved vesting length, minimum RIPE output, and a deadline
back to `acquireRipe`; movement of any protected value causes the transaction to
revert.

An acquisition must fit the epoch's remaining payment capacity and minimum
payment, and its total allocation must fit the vesting contract's current
remaining allocation budget. The requested vesting length is clamped to the
snapshot's minimum and maximum. RIPE output is the base payout plus a linearly
scaled vesting bonus. The engine transfers the exact payment amount directly to
EndaomentFunds and verifies its balance increased by exactly that amount, so
fee-on-transfer payment assets are incompatible.

The first successful acquisition in an epoch commits that epoch's snapshot.
Subsequent acquisitions use the committed terms and add accepted payment and
payment-weighted lateness. Configuration changes do not rewrite a committed
snapshot.

## Epoch controller and overrides

The controller uses the previous committed epoch's utilization. Strong demand
reduces RIPE paid per payment-token unit; weak demand increases it. Empty skipped
epochs apply bounded decay toward the configured all-in payout ceiling. Timing
affects the strong-demand adjustment only when the prior epoch has meaningful
timing data.

A rate override targets one uncommitted epoch. A target of zero resolves to the
earliest epoch that has not already accepted an acquisition. The override
changes the effective payout rate for that epoch without replacing the
controller's independently derived rate. It is consumed as applied or missed
when an epoch is committed, and configuration changes, start/stop resets, or an
explicit cancellation invalidate or clear it.

## Claims

Claims may contain one position or up to `MAX_BATCH_CLAIMS` positions. Each row
is recorded by the current vesting contract; any invalid or zero-claimable row
reverts the whole batch. Settlement then either mints RIPE directly to the
beneficiary or mints to the engine and deposits the exact amount through Teller
into MissionControl's current core RipeGov vault with the requested lock.

Engine pause and `canAcquireRipe` gate new acquisitions, not vested claims.
Claims instead depend on the mint-readiness checks above and beneficiary
blacklist status. Position updates and RIPE settlement are atomic.

## Configuration and lifecycle

The configuration validator enforces nonzero and ordered utilization bands,
bounded controller steps and decay, payment and overflow safety, a valid epoch
clock, positive bounded vesting durations, and an all-in payout ceiling. While
an epoch length is installed, `setConfig` cannot change it; `start` is the path
that installs a new valid epoch length. A zero genesis argument starts at the
current native `block.number`. `stop` clears running/genesis state and resets the
committed epoch and any override. The payment token can change only while
stopped and cannot be RIPE.

## Supply-accounting boundary

RIPE tokenomics define a total allocation of one billion RIPE across all chains
under normal operation. Official protocol policy permits RIPE Bonds issued to
cover bad debt to mint beyond the normal allocation, and the contracts do not
enforce an aggregate one-billion hard cap. This engine is instead bounded by
its configured payout rules and the vesting contract's replaceable allocation
budget. Reserve allocation and claim counters are program accounting, not
aggregate token-supply accounting.

<!-- BEGIN GENERATED API REFERENCE: RipeReserveEngine -->
## Exact API reference

> Generated from `contracts/core/RipeReserveEngine.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _paymentToken, (uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _config)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `MAX_BATCH_CLAIMS()` | `view` | `uint256` | — |
| `MAX_VESTING_LENGTH()` | `view` | `uint256` | — |
| `RATE_SOURCE_CONTROLLER()` | `view` | `uint256` | — |
| `RATE_SOURCE_OVERRIDE()` | `view` | `uint256` | — |
| `RATE_SOURCE_SEED()` | `view` | `uint256` | — |
| `acquireRipe(uint256 _paymentAmount, uint256 _requestedVestingLength, uint256 _expectedVestingLength, uint256 _expectedEpoch, uint256 _minRipeOut, uint256 _deadlineBlock)` | `nonpayable` | `uint256` | `uint256` |
| `canAcquireRipe()` | `view` | `bool` | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `cancelRateOverride()` | `nonpayable` | — | — |
| `claimVestedRipe(uint256 _positionId, bool _autoDeposit, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `claimVestedRipeMany(uint256[] _positionIds, bool _autoDeposit, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `engineConfig()` | `view` | `(uint256 paymentCapPerEpoch, uint256 minPaymentAmount, uint256 maxAllInPayoutRate, uint256 seedBasePayoutRate, uint256 uHighBps, uint256 uLowBps, uint256 minUpBps, uint256 maxUpBps, uint256 minDownBps, uint256 maxDownBps, uint256 decayBps, uint256 maxDecayEpochs, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 epochLength)` | — |
| `epochLength()` | `view` | `uint256` | `uint256` |
| `epochState()` | `view` | `(uint256 epoch, uint256 controllerBasePayoutRate, uint256 basePayoutRate, uint256 rateSource, uint256 paymentCap, uint256 minPaymentAmount, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 acceptedPayment, uint256 weightedLateness, bool timingEligible)` | — |
| `genesisBlock()` | `view` | `uint256` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getEpochSnapshot()` | `view` | `(uint256 epoch, uint256 controllerBasePayoutRate, uint256 basePayoutRate, uint256 rateSource, uint256 paymentCap, uint256 minPaymentAmount, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 acceptedPayment, uint256 weightedLateness, bool timingEligible)` | `EpochSnapshot` |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | — |
| `isRunning()` | `view` | `bool` | — |
| `isValidConfig((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _config)` | `view` | `bool` | `bool` |
| `isValidEpochLength(uint256 _epochLength)` | `view` | `bool` | `bool` |
| `isValidPaymentToken(address _token)` | `view` | `bool` | `bool` |
| `isValidRateOverride(uint256 _targetBasePayoutRate, uint256 _targetEpoch)` | `view` | `bool` | `bool` |
| `overrideTargetBasePayoutRate()` | `view` | `uint256` | — |
| `overrideTargetEpoch()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `paymentScale()` | `view` | `uint256` | — |
| `paymentToken()` | `view` | `address` | — |
| `previewAcquireRipe(uint256 _paymentAmount, uint256 _requestedVestingLength)` | `view` | `(bool available, uint256 epoch, uint256 controllerBasePayoutRate, uint256 basePayoutRate, uint256 rateSource, uint256 remainingPayment, uint256 minPaymentAmount, uint256 budgetRemaining, uint256 baseRipe, uint256 bonusRatio, uint256 bonusRipe, uint256 vestingLength, uint256 creationBlock, uint256 claimStartBlock, uint256 maturityBlock, uint256 totalRipe)` | `ReserveEngineQuote` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `setCanAcquireRipe(bool _canAcquireRipe)` | `nonpayable` | — | — |
| `setConfig((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _newConfig)` | `nonpayable` | — | — |
| `setPaymentToken(address _token)` | `nonpayable` | — | — |
| `setRateOverride(uint256 _targetBasePayoutRate, uint256 _targetEpoch)` | `nonpayable` | `uint256` | `uint256` |
| `start(uint256 _genesisBlock, uint256 _epochLength)` | `nonpayable` | — | — |
| `stop()` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `CanAcquireRipeSet` | `bool canAcquireRipe` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `EpochInitialized` | `uint256 epoch indexed, uint256 controllerBasePayoutRate, uint256 basePayoutRate, uint256 rateSource, uint256 paymentCap, uint256 minPaymentAmount, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, bool timingEligible` |
| `EpochRolled` | `uint256 fromEpoch indexed, uint256 toEpoch indexed, uint256 oldBasePayoutRate, uint256 controllerBasePayoutRate, uint256 newBasePayoutRate, uint256 rateSource, uint256 newPaymentCap, uint256 newMinPaymentAmount, uint256 newMaxVestingBonus, uint256 newMinVestingLength, uint256 newMaxVestingLength, uint256 previousAcceptedPayment, uint256 previousPaymentCap, uint256 previousWeightedLateness, bool previousTimingEligible, uint256 utilizationBps, uint256 effectiveAdjustmentBps, uint256 decaySteps` |
| `PaymentTokenSet` | `address token indexed, uint8 decimals, uint256 scale` |
| `RateOverrideApplied` | `uint256 fromEpoch indexed, uint256 toEpoch indexed, uint256 targetBasePayoutRate, uint256 controllerBasePayoutRate` |
| `RateOverrideCancelled` | `uint256 targetEpoch indexed, uint256 targetBasePayoutRate` |
| `RateOverrideInstalled` | `uint256 targetEpoch indexed, uint256 targetBasePayoutRate` |
| `RateOverrideInvalidated` | `uint256 targetEpoch indexed, uint256 targetBasePayoutRate` |
| `RateOverrideMissed` | `uint256 targetEpoch indexed, uint256 committedEpoch indexed, uint256 targetBasePayoutRate, uint256 controllerBasePayoutRate` |
| `ReserveEngineConfigSet` | `uint256 paymentCapPerEpoch, uint256 minPaymentAmount, uint256 maxAllInPayoutRate, uint256 seedBasePayoutRate, uint256 uHighBps, uint256 uLowBps, uint256 minUpBps, uint256 maxUpBps, uint256 minDownBps, uint256 maxDownBps, uint256 decayBps, uint256 maxDecayEpochs, uint256 maxVestingBonus, uint256 minVestingLength, uint256 maxVestingLength, uint256 epochLength` |
| `ReserveEngineStarted` | `uint256 genesisBlock, uint256 epochLength` |
| `ReserveEngineStopped` | `uint256 epochLength` |
| `RipeAllocated` | `address acquirer indexed, uint256 positionId indexed, uint256 paymentAmount, uint256 baseRipe, uint256 bonusRipe, uint256 bonusRatio, uint256 vestingLength, uint256 creationBlock, uint256 claimStartBlock, uint256 maturityBlock, uint256 totalRipe, uint256 controllerBasePayoutRate, uint256 basePayoutRate, uint256 rateSource, uint256 epoch indexed` |
| `VestedRipeClaimed` | `address beneficiary indexed, uint256 positionId indexed, uint256 amountClaimed, uint256 totalClaimedForPosition, uint256 ripeAllocation, bool autoDeposited, uint256 requestedLockDuration` |

### Structs declared by this source

- `ReserveEngineConfig(paymentCapPerEpoch: uint256, minPaymentAmount: uint256, maxAllInPayoutRate: uint256, seedBasePayoutRate: uint256, uHighBps: uint256, uLowBps: uint256, minUpBps: uint256, maxUpBps: uint256, minDownBps: uint256, maxDownBps: uint256, decayBps: uint256, maxDecayEpochs: uint256, maxVestingBonus: uint256, minVestingLength: uint256, maxVestingLength: uint256, epochLength: uint256)`
- `ReserveEngineQuote(available: bool, epoch: uint256, controllerBasePayoutRate: uint256, basePayoutRate: uint256, rateSource: uint256, remainingPayment: uint256, minPaymentAmount: uint256, budgetRemaining: uint256, baseRipe: uint256, bonusRatio: uint256, bonusRipe: uint256, vestingLength: uint256, creationBlock: uint256, claimStartBlock: uint256, maturityBlock: uint256, totalRipe: uint256)`
- `RateTransition(controllerBasePayoutRate: uint256, utilizationBps: uint256, effectiveAdjustmentBps: uint256, decaySteps: uint256)`
- `EpochSnapshot(epoch: uint256, controllerBasePayoutRate: uint256, basePayoutRate: uint256, rateSource: uint256, paymentCap: uint256, minPaymentAmount: uint256, maxVestingBonus: uint256, minVestingLength: uint256, maxVestingLength: uint256, acceptedPayment: uint256, weightedLateness: uint256, timingEligible: bool)`
- `CalculatedPayout(baseRipe: uint256, bonusRatio: uint256, bonusRipe: uint256, vestingLength: uint256, totalRipe: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `allocation budget`
- `already running`
- `before genesis`
- `below minimum payment`
- `beneficiary blacklisted`
- `claim not ready`
- `deposit mismatch`
- `disabled`
- `empty positions`
- `epoch moved`
- `exceeds available amount`
- `expired`
- `invalid config`
- `invalid epoch length`
- `invalid payment token`
- `invalid rate override`
- `invalid ripe gov vault`
- `mint failed`
- `mint not ready`
- `no change`
- `no override`
- `no perms`
- `not configured`
- `not running`
- `paused`
- `payment failed`
- `payment receipt mismatch`
- `ripe approval failed`
- `ripe receipt mismatch`
- `ripe settlement mismatch`
- `running`
- `slippage`
- `vesting length moved`

<!-- END GENERATED API REFERENCE: RipeReserveEngine -->
