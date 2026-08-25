# BondRoom

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/BondRoom.vy)

## Purpose

`BondRoom` sells RIPE for an approved payment asset under an epoch-based price schedule. [Teller](../core/Teller.md) is the only caller of `purchaseRipeBond`; Teller supplies the actual user/caller identities and enforces the user's `minRipePayout` after BondRoom returns.

## Purchase flow

The execution path verifies that bonding is enabled, the payment asset matches current configuration, the recipient is eligible, and third-party bonding is permitted. When the recipient differs from the caller, the configured public permission or current Underscore-owner relationship must authorize the action.

BondRoom refreshes an expired epoch before reading its available capacity. The purchase block must satisfy `epochStart <= block.number < epochEnd`. The RIPE-per-unit rate increases from the configured minimum toward the maximum as the epoch progresses.

Payment is denominated in whole units of the payment token:

```text
one unit = 10 ** paymentToken.decimals()
```

The amount is capped by user input, actual BondRoom custody, and remaining epoch capacity, then rounded down to whole units. Any excess or fractional remainder is returned to the actual caller. Successful proceeds go to EndaomentFunds.

## Payout, boosts, and locks

The base RIPE payout may receive:

- a user-specific BondBooster bonus, subject to remaining booster units; and
- a lock-duration bonus derived from current bond configuration.

If a booster is used, its minimum lock duration is applied before the lock bonus is calculated, subject to the bond configuration's maximum. A nonzero final lock deposits the payout into MissionControl's current core RipeGov vault; an unlocked payout is minted directly to the recipient. The implementation does not assume that the current governance vault has a fixed numeric ID.

When protocol bad debt exists, the purchase can allocate some RIPE/payment value to debt clearing before recording the user's net bond allocation. Epoch capacity is reduced by the payment consumed regardless of that allocation.

Teller's bond interface includes the payment amount and `minRipePayout`. Its
trailing defaults are zero requested lock duration, `msg.sender` as recipient,
and zero minimum payout. A caller must pass a nonzero minimum to obtain
payout-slippage protection and must select a lock or recipient explicitly when
the defaults are not intended.

## Epoch lifecycle and previews

`previewRipeBondPayout` is a limited estimate of epoch pricing, the
epoch-payment cap, rounding, booster, and lock-bonus arithmetic. It does not
check recipient eligibility, caller authority, actual BondRoom payment custody,
payment-asset identity, or Ledger's available RIPE bond budget, so it can return
a nonzero value when execution would revert. It can also revert when an epoch
has been scheduled for a future start because the preview subtracts that start
from the current block. It is neither a reservation nor an execution guarantee.
With only `_recipient` supplied, the preview uses zero requested lock duration
and `max_value(uint256)` requested payment, which is then capped by remaining
epoch payment capacity. It does not quote against the caller's token balance or
custody.
`previewNextEpoch`, `getLatestEpochBlockTimes`, and `refreshBondEpoch` expose
epoch projections/state transitions. Switchboard can choose the booster and
schedule an epoch start; registered Ripe addresses may refresh an elapsed epoch
under the configured rules.

An epoch length and amount must be nonzero. The end block is exclusive. When remaining capacity is smaller than one payment unit and auto-restart is enabled, BondRoom schedules the next epoch using the configured restart delay.

The principal purchase event is `RipeBondPurchased`; `BondBoosterSet` records booster replacement.

<!-- BEGIN GENERATED API REFERENCE: BondRoom -->
## Exact API reference

> Generated from `contracts/core/BondRoom.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _bondBooster)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `previewRipeBondPayout(address _recipient, uint256 _lockDuration, uint256 _paymentAmount)` | `1–3` | `_lockDuration`, `_paymentAmount` |
| `purchaseRipeBond(address _recipient, address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _caller, Addys _a)` | `5–6` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `bondBooster()` | `view` | `address` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getLatestEpochBlockTimes(uint256 _prevStartBlock, uint256 _prevEndBlock, uint256 _epochLength)` | `view` | `(uint256, uint256, bool)` |
| `getRipeHq()` | `view` | `address` |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `previewNextEpoch()` | `view` | `(uint256, uint256)` |
| `previewRipeBondPayout(address _recipient)` | `view` | `uint256` |
| `previewRipeBondPayout(address _recipient, uint256 _lockDuration)` | `view` | `uint256` |
| `previewRipeBondPayout(address _recipient, uint256 _lockDuration, uint256 _paymentAmount)` | `view` | `uint256` |
| `purchaseRipeBond(address _recipient, address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _caller)` | `nonpayable` | `uint256` |
| `purchaseRipeBond(address _recipient, address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _caller, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `refreshBondEpoch()` | `nonpayable` | `(uint256, uint256)` |
| `setBondBooster(address _bondBooster)` | `nonpayable` | — |
| `startBondEpochAtBlock(uint256 _block)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `BondBoosterSet` | `address bondBooster` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `RipeBondPurchased` | `address recipient indexed, address paymentAsset indexed, uint256 paymentAmount, uint256 lockDuration, uint256 ripePerUnit, uint256 totalRipePayout, uint256 baseRipePayout, uint256 ripeLockBonus, uint256 ripeBoostBonus, uint256 ripeForBadDebt, uint256 epochProgress, uint256 refundAmount, uint256 epochStart, uint256 epochEnd, address caller indexed` |

### Structs declared by this source

- `PurchaseRipeBondConfig(asset: address, amountPerEpoch: uint256, canBond: bool, minRipePerUnit: uint256, maxRipePerUnit: uint256, maxRipePerUnitLockBonus: uint256, epochLength: uint256, shouldAutoRestart: bool, restartDelayBlocks: uint256, minLockDuration: uint256, maxLockDuration: uint256, canAnyoneBondForUser: bool, isUserAllowed: bool)`
- `RipeBondData(paymentAmountAvailInEpoch: uint256, ripeAvailForBonds: uint256, badDebt: uint256)`

<!-- END GENERATED API REFERENCE: BondRoom -->
