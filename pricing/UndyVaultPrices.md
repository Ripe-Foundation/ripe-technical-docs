# UndyVaultPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/UndyVaultPrices.vy)

## Overview

`UndyVaultPrices` prices Underscore Earn Vault shares using the vault's underlying asset price plus a guarded, **time-weighted** price-per-share history. It is not supply weighted.

## Admission and metadata binding

The source resolves MissionControl's current Underscore registry, then that registry's canonical vault-registry entry. A candidate must be recognized as an Earn Vault, implement the ERC-4626 metadata/read surface, and have an underlying asset with a nonzero PriceDesk price.

Each configuration snapshots:

```text
underlyingAsset
underlyingDecimals
vaultTokenDecimals
minSnapshotDelay
maxNumSnapshots
maxUpsideDeviation
staleTime
lastSnapshot
nextIndex
```

At confirmation of a new feed or configuration update, the contract re-reads `asset()`, underlying decimals, and vault-token decimals. A metadata mismatch cancels/fails the pending action instead of installing a config based on changed assumptions.

Other bounds are:

- `minSnapshotDelay <= 1 week`;
- `1 <= maxNumSnapshots <= 25`;
- `maxUpsideDeviation <= 100%`; and
- both decimal values in the range 1 through 77.

Governance manages add, update, and disable actions through the source's timelock while unpaused.

## Time-weighted price per share

`PriceSnapshot` records `totalSupply`, `pricePerShare`, and `lastUpdate`. Snapshots are kept in a circular ring.

The weighted value is based on elapsed time:

```text
weightedPps = Σ(pricePerShare_i * duration_i) / Σ(duration_i)
```

Each observation applies from its timestamp until the next valid observation; the newest applies through the current timestamp. `totalSupply` is not a weight. It is retained as snapshot validity/observability data.

Stale or empty observations are skipped. Non-monotonic timestamps, invalid ring state, future observations, or checked-arithmetic failures return zero. A single fresh observation with no elapsed duration may use the fresh `lastSnapshot` value; a stale observation cannot.

This source intentionally ignores the global stale-time argument forwarded through the shared price-source interface. Snapshot eligibility uses the configuration's own `staleTime`.

## Snapshot updates

Only a valid Ripe address may add a snapshot, and the source must be unpaused. A duplicate timestamp, unmet minimum delay, invalid vault conversion, or unconfigured asset returns false.

The current price per share is `convertToAssets(10 ** vaultTokenDecimals)`.
When `maxUpsideDeviation` is nonzero, a new upward value is capped at the prior
value plus that deviation and a downward move is not throttled.
`maxUpsideDeviation == 0` disables upside throttling; it does not mean zero
tolerated upside. The snapshot ring then advances its next write index.

Changing `maxNumSnapshots` resets the ring and seeds it with a new validated observation. An ordinary configuration update with the same ring size preserves snapshot progress made while the action was pending.

## Final vault-share price

The source reads the underlying USD price from PriceDesk and computes the guarded price-per-share as:

```text
selectedPps = min(timeWeightedPps, currentConvertToAssetsPps)
vaultUsdPrice = underlyingUsdPrice * selectedPps / 10 ** underlyingDecimals
```

The current minimum exposes downside immediately. A zero underlying price, zero weighted value, zero current conversion, unsafe decimals, or arithmetic overflow returns zero.

## Integration requirements

- Do not describe or implement supply-weighted snapshot pricing.
- Treat zero as unavailable.
- Re-onboard rather than assuming safety if vault asset/decimal metadata changes.
- Per-vault snapshot cadence, history, upside limit, and stale time are risk parameters, not universal defaults.

<!-- BEGIN GENERATED API REFERENCE: UndyVaultPrices -->
## Exact API reference

> Generated from `contracts/priceSources/UndyVaultPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addNewPriceFeed(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `1–5` | `_minSnapshotDelay = 60 * 5`, `_maxNumSnapshots = 20`, `_maxUpsideDeviation = 10_00`, `_staleTime = 60 * 60 * 24` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime = 0`, `_priceDesk = empty(address)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime = 0`, `_priceDesk = empty(address)` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `1–5` | `_minSnapshotDelay = 60 * 5`, `_maxNumSnapshots = 20`, `_maxUpsideDeviation = 10_00`, `_staleTime = 60 * 60 * 24` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `addNewPriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _minSnapshotDelay)` | `nonpayable` | `bool` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots)` | `nonpayable` | `bool` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation)` | `nonpayable` | `bool` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` | `bool` |
| `assets(uint256 arg0)` | `view` | `address` | — |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `cancelDisablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelNewPendingPriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `cancelPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmDisablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `confirmNewPriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` | `bool` |
| `disablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `expiration()` | `view` | `uint256` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getLatestSnapshot(address _asset)` | `view` | `(uint256 totalSupply, uint256 pricePerShare, uint256 lastUpdate)` | `PriceSnapshot` |
| `getPrice(address _asset)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` | — |
| `getRipeHq()` | `view` | `address` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `getWeightedPrice(address _asset)` | `view` | `uint256` | `uint256` |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `hasPendingPriceFeedUpdate(address _asset)` | `view` | `bool` | `bool` |
| `hasPriceFeed(address _asset)` | `view` | `bool` | `bool` |
| `indexOfAsset(address arg0)` | `view` | `uint256` | — |
| `isExpired(uint256 _actionId)` | `view` | `bool` | — |
| `isPaused()` | `view` | `bool` | — |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidDisablePriceFeed(address _asset)` | `view` | `bool` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidNewFeed(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `view` | `bool` | `bool` |
| `isValidUpdateConfig(address _asset, uint256 _maxNumSnapshots, uint256 _staleTime)` | `view` | `bool` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `numAssets()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingPriceConfigs(address arg0)` | `view` | `(uint256 actionId, (address underlyingAsset, uint256 underlyingDecimals, uint256 vaultTokenDecimals, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, (uint256 totalSupply, uint256 pricePerShare, uint256 lastUpdate) lastSnapshot, uint256 nextIndex) config)` | — |
| `priceConfigs(address arg0)` | `view` | `(address underlyingAsset, uint256 underlyingDecimals, uint256 vaultTokenDecimals, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, (uint256 totalSupply, uint256 pricePerShare, uint256 lastUpdate) lastSnapshot, uint256 nextIndex)` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `snapShots(address arg0, uint256 arg1)` | `view` | `(uint256 totalSupply, uint256 pricePerShare, uint256 lastUpdate)` | — |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `updatePriceConfig(address _asset)` | `nonpayable` | `bool` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay)` | `nonpayable` | `bool` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots)` | `nonpayable` | `bool` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation)` | `nonpayable` | `bool` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DisablePriceConfigCancelled` | `address asset indexed, address underlyingAsset indexed` |
| `DisablePriceConfigConfirmed` | `address asset indexed, address underlyingAsset indexed` |
| `DisablePriceConfigPending` | `address asset indexed, address underlyingAsset indexed, uint256 confirmationBlock, uint256 actionId` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewPriceConfigAdded` | `address asset indexed, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime` |
| `NewPriceConfigCancelled` | `address asset indexed, address underlyingAsset indexed` |
| `NewPriceConfigPending` | `address asset indexed, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceConfigUpdateCancelled` | `address asset indexed, address underlyingAsset indexed` |
| `PriceConfigUpdatePending` | `address asset indexed, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceConfigUpdated` | `address asset indexed, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime` |
| `PricePerShareSnapshotAdded` | `address asset indexed, address underlyingAsset indexed, uint256 totalSupply, uint256 pricePerShare` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `PriceConfig(underlyingAsset: address, underlyingDecimals: uint256, vaultTokenDecimals: uint256, minSnapshotDelay: uint256, maxNumSnapshots: uint256, maxUpsideDeviation: uint256, staleTime: uint256, lastSnapshot: PriceSnapshot, nextIndex: uint256)`
- `PriceSnapshot(totalSupply: uint256, pricePerShare: uint256, lastUpdate: uint256)`
- `PendingPriceConfig(actionId: uint256, config: PriceConfig)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot cancel action`
- `contract paused`
- `invalid asset`
- `invalid config`
- `invalid feed`
- `invalid snapshot`
- `no pending config`
- `no pending disable feed`
- `no perms`
- `time lock not reached`

<!-- END GENERATED API REFERENCE: UndyVaultPrices -->
