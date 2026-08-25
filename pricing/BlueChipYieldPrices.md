# BlueChipYieldPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/priceSources/BlueChipYieldPrices.vy)

## Overview

`BlueChipYieldPrices` prices supported lending and ERC-4626-style receipt tokens from an underlying asset price and, where required, a guarded history of price-per-share snapshots.

The snapshot history is **time weighted**, not supply weighted. `totalSupply` is recorded for validation and observability; it is not the weighting term in `getWeightedPrice`.

## Supported protocol flag

`Protocol` is append-only because its numeric values may already be stored:

```text
MORPHO
EULER
MOONWELL
SKY
FLUID
AAVE_V3
COMPOUND_V3
MORPHO_V2
```

`MORPHO_V2` is appended after the earlier enum members. The constructor takes
and stores its factory address as `MORPHO_V2_ADDR`. A Morpho V2 token is
admitted only when that factory reports `isVaultV2(asset)` and the token's
ERC-4626 `asset()` call supplies its underlying.

Implemented price paths are Morpho, Morpho V2, Euler, Fluid, Moonwell, Aave V3,
and Compound V3. The enum's `SKY` member is reserved and has no pricing branch.

## Price configuration

Each asset stores:

```text
protocol
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

`PriceSnapshot` contains `totalSupply`, `pricePerShare`, and `lastUpdate` timestamp. Snapshots live in a circular ring of at most 25 slots.

Configuration validation requires:

- a recognized nonzero underlying and nonzero underlying price from PriceDesk;
- `minSnapshotDelay <= 1 week`;
- `1 <= maxNumSnapshots <= 25`;
- `maxUpsideDeviation <= 100%`; and
- nonzero underlying/vault decimals no greater than 77.

Feed add, configuration update, and disable operations are governance-controlled, paused-aware, and timelocked. Confirmation revalidates the pending configuration. Changing the ring size resets snapshot history for snapshot-based protocols. Aave V3 and Compound V3 do not use snapshots and clear the ring.

## Time-weighted snapshot price

The ring is traversed in chronological order from its next write position. Invalid, empty, or stale observations are skipped. For each adjacent valid pair, the **earlier** observation's price-per-share is multiplied by the time until the later observation. The last valid observation is weighted through `block.timestamp`:

```text
weightedPps = Σ(pricePerShare_i * duration_i) / Σ(duration_i)
```

This formula contains no supply multiplier. A non-monotonic timestamp, an invalid ring index/configuration, or checked-arithmetic failure returns zero.

When one fresh observation exists in its creation timestamp and therefore has zero elapsed duration, the contract falls back to the fresh `lastSnapshot.pricePerShare`. It does not use a stale fallback.

The source does not use MissionControl's global stale-time argument for snapshot history. Each asset's `PriceConfig.staleTime` determines which snapshots remain eligible.

## Snapshot creation and upside throttle

Only a valid Ripe address may call `addPriceSnapshot`, and the source must be unpaused. Snapshotting returns false for unconfigured assets, Aave/Compound paths, a duplicate timestamp, a too-recent request, or an invalid current price-per-share.

A new snapshot reads:

- ERC-20 `totalSupply`, scaled by vault-token decimals; and
- current price per share from ERC-4626 `convertToAssets`, or Moonwell `exchangeRateStored`.

An upward move is capped relative to the previous snapshot by `maxUpsideDeviation`. Downward moves are not throttled. Zero values and checked-arithmetic failures fail soft.

## Final token price

PriceDesk supplies the current underlying USD price.

- Aave V3 and Compound V3 return the underlying price directly.
- ERC-4626 protocols multiply underlying price by guarded price per share and divide by the underlying scale.
- Moonwell uses the same composition with its exchange-rate-derived price per share.

For snapshot-based paths, the selected price per share is:

```text
min(timeWeightedPricePerShare, currentPricePerShare)
```

The minimum makes a current downside visible immediately while snapshot
throttling limits upside. If the current price-per-share read is zero, the
result is zero; the historical value does not mask the failure.

## Protocol admission checks

- Morpho checks either configured MetaMorpho registry.
- Morpho V2 checks the configured V2 factory.
- Euler checks either the proxy or deployment registry.
- Fluid requires membership in the registry's current fToken list.
- Compound V3 requires a nonzero factory for the candidate and uses `baseToken()`.
- Moonwell requires membership in `getAllMarkets()` and uses `underlying()`.
- Aave V3 requires membership in the data provider's aToken list and reads `UNDERLYING_ASSET_ADDRESS()`.

## Integration requirements

- Derive value from the documented underlying-asset conversion and underlying
  price path.
- Treat zero as unavailable and distinguish it from feed configuration.
- Keep the enum append-only and use the exact ABI value for `MORPHO_V2`.
- Snapshot cadence, history length, upside limit, and stale time are per-asset risk parameters.

<!-- BEGIN GENERATED API REFERENCE: BlueChipYieldPrices -->
## Exact API reference

> Generated from `contracts/priceSources/BlueChipYieldPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock, address[2] _morphoAddrs, address[2] _eulerAddrs, address _fluidAddr, address _compoundV3Addr, address _moonwellAddr, address _aaveV3Addr, address _morphoV2Addr)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addNewPriceFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `2–6` | `_minSnapshotDelay`, `_maxNumSnapshots`, `_maxUpsideDeviation`, `_staleTime` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `1–5` | `_minSnapshotDelay`, `_maxNumSnapshots`, `_maxUpsideDeviation`, `_staleTime` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `AAVE_V3_ADDR()` | `view` | `address` |
| `COMPOUND_V3_ADDR()` | `view` | `address` |
| `EULER_ADDRS(uint256 arg0)` | `view` | `address` |
| `FLUID_ADDR()` | `view` | `address` |
| `MOONWELL_ADDR()` | `view` | `address` |
| `MORPHO_ADDRS(uint256 arg0)` | `view` | `address` |
| `MORPHO_V2_ADDR()` | `view` | `address` |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `addNewPriceFeed(address _asset, uint256 _protocol)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `nonpayable` | `bool` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` |
| `assets(uint256 arg0)` | `view` | `address` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelNewPendingPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `confirmDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `confirmNewPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `disablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `expiration()` | `view` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getGovernors()` | `view` | `address[]` |
| `getLatestSnapshot(address _asset)` | `view` | `(uint256,uint256,uint256)` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` |
| `getRipeHq()` | `view` | `address` |
| `getRipeHqFromGov()` | `view` | `address` |
| `getWeightedPrice(address _asset)` | `view` | `uint256` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
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
| `isValidNewFeed(address _asset, uint256 _protocol, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `view` | `bool` |
| `isValidUpdateConfig(address _asset, uint256 _maxNumSnapshots, uint256 _staleTime)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingPriceConfigs(address arg0)` | `view` | `(uint256,(uint256,address,uint256,uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256),uint256))` |
| `priceConfigs(address arg0)` | `view` | `(uint256,address,uint256,uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256),uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `snapShots(address arg0, uint256 arg1)` | `view` | `(uint256,uint256,uint256)` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |
| `updatePriceConfig(address _asset)` | `nonpayable` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay)` | `nonpayable` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots)` | `nonpayable` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation)` | `nonpayable` | `bool` |
| `updatePriceConfig(address _asset, uint256 _minSnapshotDelay, uint256 _maxNumSnapshots, uint256 _maxUpsideDeviation, uint256 _staleTime)` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DisablePriceConfigCancelled` | `address asset indexed, uint256 protocol, address underlyingAsset indexed` |
| `DisablePriceConfigConfirmed` | `address asset indexed, uint256 protocol, address underlyingAsset indexed` |
| `DisablePriceConfigPending` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 confirmationBlock, uint256 actionId` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewPriceConfigAdded` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime` |
| `NewPriceConfigCancelled` | `address asset indexed, uint256 protocol, address underlyingAsset indexed` |
| `NewPriceConfigPending` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceConfigUpdateCancelled` | `address asset indexed, uint256 protocol, address underlyingAsset indexed` |
| `PriceConfigUpdatePending` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceConfigUpdated` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 minSnapshotDelay, uint256 maxNumSnapshots, uint256 maxUpsideDeviation, uint256 staleTime` |
| `PricePerShareSnapshotAdded` | `address asset indexed, uint256 protocol, address underlyingAsset indexed, uint256 totalSupply, uint256 pricePerShare` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `PriceConfig(protocol: Protocol, underlyingAsset: address, underlyingDecimals: uint256, vaultTokenDecimals: uint256, minSnapshotDelay: uint256, maxNumSnapshots: uint256, maxUpsideDeviation: uint256, staleTime: uint256, lastSnapshot: PriceSnapshot, nextIndex: uint256)`
- `PriceSnapshot(totalSupply: uint256, pricePerShare: uint256, lastUpdate: uint256)`
- `PendingPriceConfig(actionId: uint256, config: PriceConfig)`
- `TokenData(symbol: String[32], tokenAddress: address)`

<!-- END GENERATED API REFERENCE: BlueChipYieldPrices -->
