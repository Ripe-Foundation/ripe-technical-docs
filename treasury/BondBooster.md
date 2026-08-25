# BondBooster

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/BondBooster.vy)

## Purpose

`BondBooster` stores temporary, user-specific RIPE bond bonuses. A `BoosterConfig` identifies the user, boost ratio, maximum payment units covered, and exclusive expiry block. BondRoom reads the available boost and is the only contract allowed to consume covered units.

## Boost availability

`getBoostRatio(user, units)` returns zero when the grant is missing or expired, or when the requested units plus already used units would exceed the user's allowance. Otherwise it returns the configured ratio. BondRoom independently caps the ratio defensively when calculating a payout.

That excess-capacity path is not universally fail-soft: checked overflow in
`unitsUsed + units` reverts before the allowance comparison. `addNewUnitsUsed`
has the corresponding checked-addition boundary.

`addNewUnitsUsed` is BondRoom-only and increments recorded consumption. It does not repeat the active-grant or allowance check itself; the current BondRoom flow first obtains a nonzero `getBoostRatio` result and consumes units only when that boost is applied. Integrations must treat that sequence, rather than the increment method alone, as the capacity guard.

## Grant lifecycle

Switchboard can set one or up to 50 boosters, remove one or many boosters, and update the global maximum ratio, maximum units, and minimum lock duration.

Reissuing an absent or expired grant starts a fresh grant and resets
`unitsUsed`. Updating an active grant preserves prior usage. Removing a grant
clears both its configuration and its usage. This distinction prevents an
active grant from being refreshed merely to erase consumed capacity.

A proposed grant is valid only when it has a nonzero user, a nonzero ratio within the current global maximum, a future expiry block, and nonzero units within the current global maximum.

## Bond integration

When a boost produces a bonus, BondRoom also applies at least BondBooster's
current minimum lock duration, capped by the current bond configuration's
maximum lock. Booster usage is therefore coupled to an executed bond purchase,
not a preview.

Setters emit `BondBoostModified` for each grant, plus `BondBoostRemoved`,
`MaxBoostAndMaxUnitsSet`, and `MinLockDurationSet` for their respective changes.
`setManyBondBoosters` emits the per-grant event but not the declared
`ManyBondBoostersSet` event, so indexers should follow `BondBoostModified`.

<!-- BEGIN GENERATED API REFERENCE: BondBooster -->
## Exact API reference

> Generated from `contracts/config/BondBooster.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _maxBoostRatio, uint256 _maxUnits, uint256 _minLockDuration)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `addNewUnitsUsed(address _user, uint256 _newUnits)` | `nonpayable` | — | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `config(address arg0)` | `view` | `(address user, uint256 boostRatio, uint256 maxUnitsAllowed, uint256 expireBlock)` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getBoostRatio(address _user, uint256 _units)` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | — |
| `isValidBooster((address,uint256,uint256,uint256) _config)` | `view` | `bool` | `bool` |
| `maxBoostRatio()` | `view` | `uint256` | — |
| `maxUnits()` | `view` | `uint256` | — |
| `minLockDuration()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `removeBondBooster(address _user)` | `nonpayable` | — | — |
| `removeManyBondBoosters(address[] _users)` | `nonpayable` | — | — |
| `setBondBooster((address,uint256,uint256,uint256) _config)` | `nonpayable` | — | — |
| `setManyBondBoosters((address,uint256,uint256,uint256)[] _boosters)` | `nonpayable` | — | — |
| `setMaxBoostAndMaxUnits(uint256 _maxBoostRatio, uint256 _maxUnitsAvail)` | `nonpayable` | — | — |
| `setMinLockDuration(uint256 _minLockDuration)` | `nonpayable` | — | — |
| `unitsUsed(address arg0)` | `view` | `uint256` | — |

### Events

| Event | Fields |
| --- | --- |
| `BondBoostModified` | `address user, uint256 boostRatio, uint256 maxUnitsAllowed, uint256 expireBlock` |
| `BondBoostRemoved` | `address user` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `ManyBondBoostersSet` | `uint256 numBoosters` |
| `MaxBoostAndMaxUnitsSet` | `uint256 maxBoostRatio, uint256 maxUnits` |
| `MinLockDurationSet` | `uint256 minLockDuration` |

### Structs declared by this source

- `BoosterConfig(user: address, boostRatio: uint256, maxUnitsAllowed: uint256, expireBlock: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid booster`
- `invalid max values`
- `invalid user`
- `no boosters`
- `no perms`

<!-- END GENERATED API REFERENCE: BondBooster -->
