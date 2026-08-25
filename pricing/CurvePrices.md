# CurvePrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/priceSources/CurvePrices.vy)

## Overview

`CurvePrices` prices supported Curve LP tokens and two-coin pool assets, derives sGREEN from the GREEN price, and maintains a separate GREEN reference-pool monitor used by debt-rate and Endaoment stabilizer logic.

## Curve registry binding

The constructor resolves the MetaRegistry and supported registry/factory handlers from a supplied Curve Address Provider. It stores the GREEN and Savings GREEN token addresses and governance/timelock bounds.

`getCurvePoolConfig(pool)` snapshots:

```text
pool
lpToken
numUnderlying
underlying[4]
poolType
hasEcoToken
```

Supported pool flags are StableSwap NG, TwoCrypto NG, Tricrypto NG, legacy TwoCrypto, MetaPool, and the fallback Crypto type. A feed rejects a pool with more than four underlyings; only the first four are represented.

## Price routes

### Stable and MetaPool LP tokens

For an LP token in StableSwap NG or MetaPool, the source asks PriceDesk for every underlying and selects the lowest price. It returns:

```text
lowestUnderlyingUsdPrice * pool.get_virtual_price() / 1e18
```

Any missing underlying price or zero virtual price makes the result zero.

### Crypto LP tokens

Other supported LP routes use:

```text
PriceDesk price of underlying[0] * pool.lp_price() / 1e18
```

Both inputs must be nonzero.

### Two-coin single assets

Only a pool with exactly two underlyings can price one of its component assets. The source combines the pool's price oracle with PriceDesk's price for the other asset. StableSwap NG uses `price_oracle(0)`; other types use `price_oracle()`.

### Savings GREEN

sGREEN does not have an independent Curve config. Requests canonicalize sGREEN to the GREEN feed, then multiply the GREEN price by `sGREEN.convertToAssets(1e18) / 1e18`. Governance cannot add a direct `curveConfig[sGREEN]` feed.

The shared price-source `staleTime` parameter is not used by CurvePrices. Freshness is provided by the component prices selected through PriceDesk and, separately, by block-based reference-pool policy.

## Dependency graph safety

Curve routes can recurse through PriceDesk when an LP or alternate asset is itself priced by CurvePrices. Admission therefore constructs the proposed route's dependency edges and walks the active Curve graph.

The source rejects:

- a direct self-dependency;
- an LP whose underlying canonicalizes to that same LP;
- same-pool, cross-pool, or transitive cycles;
- a cycle hidden by GREEN/sGREEN aliases; and
- inconsistent active graph indices or a walk that cannot be represented within the candidate plus 50 active Curve assets.

Stable/MetaPool LPs depend on all underlyings. Crypto LPs depend on index zero. A two-coin single-asset route depends on the alternate asset. Graph checks model only dependencies that can recurse into active Curve configs; other PriceDesk sources terminate the Curve graph.

## Feed lifecycle and qualification

Governance controls timelocked add, update, and disable actions while unpaused. Initiation snapshots the exact MetaRegistry-derived config. Confirmation requires that a fresh MetaRegistry snapshot still matches it and that all structural/cycle checks still pass.

An ecosystem-token LP may be proposed before it has supply, but it cannot be activated until `totalSupply()` is nonzero.

At add or update confirmation, the source temporarily stages the exact pending config and asks PriceDesk's `qualifyCallerPriceSource(asset)` to execute it with PriceDesk's production calldata and gas stipend. Activation requires a nonzero price and source status `1`. Any failure reverts staging, timelock confirmation, and pending-state mutation atomically.

The lifecycle selectors are distinct: `addNewPriceFeed(asset, pool)` confirms
with `confirmNewPriceFeed(asset)`, while `updatePriceFeed(asset, pool)` confirms
with `confirmPriceFeedUpdate(asset)`. A pending disable confirms through
`confirmDisablePriceFeed(asset)`.

`addPriceSnapshot(asset)` returns false; ordinary Curve price feeds do not keep local snapshots.

## GREEN reference-pool configuration

The reference pool is a distinct two-coin Curve pool containing GREEN and one alternate asset. The configuration stores:

```text
pool
lpToken
greenIndex
altAsset
altAssetDecimals
maxNumSnapshots
dangerTrigger
staleBlocks
stabilizerAdjustWeight
stabilizerMaxPoolDebt
```

Configuration validation binds exact pool/LP/coin identity, requires exactly two underlyings, and requires alternate decimals at most 18. Other bounds are:

- 1 through 100 snapshots;
- danger trigger from 50.00% through 99.99%;
- nonzero `staleBlocks` whose deadline is representable;
- stabilizer adjustment weight from 0.01% through 100%; and
- nonzero maximum pool debt no greater than 25 million GREEN.

The current pool observation must also be usable. Confirmation revalidates MetaRegistry identity and the alternate token's decimals.

Pool identity or ring-capacity changes clear and reseed the ring. A capacity-only change preserves accumulated danger blocks after the new seed. A danger-trigger or stale-block change preserves history but creates a policy boundary at confirmation; elapsed time before that boundary is not silently reclassified under the new rule.

## Reference-pool observations

`getCurvePoolData` reads the raw GREEN balance and the alternate balance normalized to 18 decimals, then computes:

```text
greenRatio = greenBalance / (greenBalance + normalizedAltBalance)
```

An empty pool reports a neutral 50% ratio. A stored snapshot requires nonzero GREEN balance and nonzero ratio and records block number, ratio, and whether the ratio meets the danger trigger.

Only a valid Ripe address may call `addGreenRefPoolSnapshot`. A paused source returns false rather than reverting. At most one snapshot may be recorded per block.

Every reference-pool timestamp and `staleBlocks` interval uses native EVM
`block.number`. CurvePrices does not read Ledger's `ACTION_BLOCK_SOURCE`; the
reference-pool clock and Ledger's action clock are independent.

## Weighted ratio and danger continuity

The weighted ratio uses only **closed intervals** between consecutive valid observations. It gives no live-tail weight from the newest observation through the current block. The newest observation must nevertheless be no more than `staleBlocks` old or the result is unavailable.

For a valid interval no longer than `staleBlocks`, its ratio is:

```text
min(previousRatio, currentRatio)
```

That conservative endpoint rule prevents an isolated high tick from creating danger time. Intervals with missing, future, non-monotonic, or stale endpoints are excluded or fail closed as defined by the ring checks.

`numBlocksInDanger` increases only when both endpoints are dangerous. Recovery credit likewise requires both endpoints to be safe. Mixed intervals neither add danger time nor erase it. A complete safe recovery interval of `staleBlocks`, which may accumulate across matching safe observations, resets danger blocks. Policy-boundary classification follows the same matching-endpoint principle.

## Stabilizer data

`getGreenStabilizerConfig()` returns the exact eight-field tuple:

```text
pool
lpToken
greenBalance
greenRatio
greenIndex
stabilizerAdjustWeight
stabilizerMaxPoolDebt
altBalance
```

`altBalance` is normalized to 18 decimals. The tuple does not contain a field named `greenPrice`. Callers should compare normalized balances and use `greenRatio` for the current imbalance measure.

## Integration requirements

- Treat zero as unavailable.
- Do not configure more than four underlyings or construct recursive Curve price graphs.
- Do not infer active feeds from source-supported pool types.
- Keep ordinary price freshness separate from the GREEN monitor's block-based snapshot policy.

<!-- BEGIN GENERATED API REFERENCE: CurvePrices -->
## Exact API reference

> Generated from `contracts/priceSources/CurvePrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, address _curveAddressProvider, address _green, address _savingsGreen, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getSingleTokenPrice(address _pool, address _targetAsset, address[2] _coins, uint256 _poolType)` | `3–4` | `_poolType` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `CURVE_META_REGISTRY()` | `view` | `address` |
| `CURVE_REGISTRIES()` | `view` | `(address,address,address,address,address)` |
| `GREEN()` | `view` | `address` |
| `SGREEN()` | `view` | `address` |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `addGreenRefPoolSnapshot()` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _pool)` | `nonpayable` | `bool` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` |
| `assets(uint256 arg0)` | `view` | `address` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelGreenRefPoolConfig(uint256 _aid)` | `nonpayable` | `bool` |
| `cancelNewPendingPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `confirmDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `confirmGreenRefPoolConfig(uint256 _aid)` | `nonpayable` | `bool` |
| `confirmNewPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `curveConfig(address arg0)` | `view` | `(address,address,uint256,address[4],uint256,bool)` |
| `disablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `expiration()` | `view` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getCryptoLpPrice(address _pool, address _firstAsset)` | `view` | `uint256` |
| `getCurrentGreenPoolStatus()` | `view` | `(uint256,uint256,uint256)` |
| `getCurvePoolConfig(address _pool)` | `view` | `(address,address,uint256,address[4],uint256,bool)` |
| `getCurvePoolData()` | `view` | `(uint256, uint256)` |
| `getGovernors()` | `view` | `address[]` |
| `getGreenStabilizerConfig()` | `view` | `(address,address,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` |
| `getRipeHq()` | `view` | `address` |
| `getRipeHqFromGov()` | `view` | `address` |
| `getSingleTokenPrice(address _pool, address _targetAsset, address[2] _coins)` | `view` | `uint256` |
| `getSingleTokenPrice(address _pool, address _targetAsset, address[2] _coins, uint256 _poolType)` | `view` | `uint256` |
| `getStableLpPrice(address _pool, address[4] _coins)` | `view` | `uint256` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `greenRefPoolConfig()` | `view` | `(address,address,uint256,address,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `greenRefPoolData()` | `view` | `((uint256,uint256,uint256,bool),uint256,uint256)` |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` |
| `hasPendingGovChange()` | `view` | `bool` |
| `hasPendingPriceFeedUpdate(address _asset)` | `view` | `bool` |
| `hasPriceFeed(address _asset)` | `view` | `bool` |
| `indexOfAsset(address arg0)` | `view` | `uint256` |
| `isExpired(uint256 _actionId)` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidDisablePriceFeed(address _asset)` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidNewFeed(address _asset, address _pool)` | `view` | `bool` |
| `isValidUpdateFeed(address _asset, address _newPool)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingGreenRefPoolConfig(uint256 arg0)` | `view` | `(address,address,uint256,address,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `pendingUpdates(address arg0)` | `view` | `(uint256,(address,address,uint256,address[4],uint256,bool))` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setGreenRefPoolConfig(address _pool, uint256 _maxNumSnapshots, uint256 _dangerTrigger, uint256 _staleBlocks, uint256 _stabilizerAdjustWeight, uint256 _stabilizerMaxPoolDebt)` | `nonpayable` | `uint256` |
| `snapShots(uint256 arg0)` | `view` | `(uint256,uint256,uint256,bool)` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |
| `updatePriceFeed(address _asset, address _pool)` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `CurvePriceConfigUpdateCancelled` | `address asset indexed, address pool indexed, address prevPool indexed` |
| `CurvePriceConfigUpdatePending` | `address asset indexed, address pool indexed, address prevPool indexed, uint256 confirmationBlock, uint256 actionId` |
| `CurvePriceConfigUpdated` | `address asset indexed, address pool indexed, address prevPool indexed` |
| `CurvePriceDisabled` | `address asset indexed, address prevPool indexed` |
| `DisableCurvePriceCancelled` | `address asset indexed, address prevPool indexed` |
| `DisableCurvePricePending` | `address asset indexed, address prevPool indexed, uint256 confirmationBlock, uint256 actionId` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `GreenRefPoolConfigPending` | `address pool indexed, uint256 maxNumSnapshots, uint256 dangerTrigger, uint256 staleBlocks, uint256 stabilizerAdjustWeight, uint256 stabilizerMaxPoolDebt, uint256 confirmationBlock, uint256 actionId` |
| `GreenRefPoolConfigUpdateCancelled` | `address pool indexed, uint256 maxNumSnapshots, uint256 dangerTrigger, uint256 staleBlocks, uint256 stabilizerAdjustWeight, uint256 stabilizerMaxPoolDebt` |
| `GreenRefPoolConfigUpdated` | `address pool indexed, uint256 maxNumSnapshots, uint256 dangerTrigger, uint256 staleBlocks, uint256 stabilizerAdjustWeight, uint256 stabilizerMaxPoolDebt` |
| `GreenRefPoolSnapshotAdded` | `address pool indexed, uint256 greenBalance, uint256 greenRatio, bool inDanger` |
| `NewCurvePriceAdded` | `address asset indexed, address pool indexed` |
| `NewCurvePriceCancelled` | `address asset indexed, address pool indexed` |
| `NewCurvePricePending` | `address asset indexed, address pool indexed, uint256 confirmationBlock, uint256 actionId` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `CurvePriceConfig(pool: address, lpToken: address, numUnderlying: uint256, underlying: address[4], poolType: PoolType, hasEcoToken: bool)`
- `PendingCurvePrice(actionId: uint256, config: CurvePriceConfig)`
- `CurveRegistries(StableSwapNg: address, TwoCryptoNg: address, TricryptoNg: address, TwoCrypto: address, MetaPool: address)`
- `GreenRefPoolConfig(pool: address, lpToken: address, greenIndex: uint256, altAsset: address, altAssetDecimals: uint256, maxNumSnapshots: uint256, dangerTrigger: uint256, staleBlocks: uint256, stabilizerAdjustWeight: uint256, stabilizerMaxPoolDebt: uint256)`
- `RefPoolSnapshot(greenBalance: uint256, ratio: uint256, update: uint256, inDanger: bool)`
- `GreenRefPoolData(lastSnapshot: RefPoolSnapshot, numBlocksInDanger: uint256, nextIndex: uint256)`
- `CurrentGreenPoolStatus(weightedRatio: uint256, dangerTrigger: uint256, numBlocksInDanger: uint256)`
- `StabilizerConfig(pool: address, lpToken: address, greenBalance: uint256, greenRatio: uint256, greenIndex: uint256, stabilizerAdjustWeight: uint256, stabilizerMaxPoolDebt: uint256, altBalance: uint256)`

<!-- END GENERATED API REFERENCE: CurvePrices -->
