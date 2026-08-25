# RedStone

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/priceSources/RedStone.vy)

## Overview

`RedStone` manages Chainlink-compatible RedStone feeds and optionally converts an asset/ETH answer through PriceDesk's ETH/USD price. Answers are normalized to 18 decimals and feed changes are timelocked.

## Configuration and reads

Each `RedStoneConfig` stores:

```text
feed: address
decimals: uint256
needsEthToUsd: bool
staleTime: uint256
```

The source validates the familiar round fields: positive answer, nonfuture `updatedAt`, nonzero `roundId`, `answeredInRound >= roundId`, effective freshness, and at most 18 feed decimals. Valid answers are scaled to 18 decimals.

`getPriceAndHasFeed` reports feed configuration separately from price usability. `addPriceSnapshot` returns false; there is no local snapshot history.

## ETH conversion route

When `needsEthToUsd` is true, the source obtains ETH/USD from PriceDesk with a non-raising call and multiplies it by the asset/ETH price. Missing ETH/USD therefore produces zero rather than reverting, which permits pending feed confirmation to follow its retry/cancel lifecycle.

The route rejects recursive or aliased configurations:

- the priced asset cannot itself be ETH;
- the configured ETH feed cannot itself require ETH conversion; and
- the primary feed cannot be the same feed used by the ETH config.

## Freshness policy

Only the canonical PriceDesk may forward a nonzero global stale time. For the primary feed, nonzero local `staleTime` is an absolute override and zero inherits MissionControl. Local bounds are 5 minutes through 7 days; an effective/global nonzero value above 7 days is invalid. The source does not take `min(global, local)`.

The ETH/USD conversion read is a separate PriceDesk read and therefore follows the current policy for the selected ETH source rather than reusing the primary feed's local override.

## Feed lifecycle

Governance controls timelocked add, update, stale-time update, and disable
actions while unpaused. The source snapshots feed decimals when an action is
initiated and confirms that the current decimals still match at execution. It
also revalidates the price route before installing a pending add/update.

An omitted stale-time value in `updatePriceFeed` preserves the current local setting. `updateStaleTime` explicitly changes it, including zero for global inheritance.

## Integration requirements

- Use PriceDesk for protocol reads so source isolation and fallback apply.
- Treat zero as unavailable.
- Establish a safe, direct ETH/USD route before enabling ETH conversion.

<!-- BEGIN GENERATED API REFERENCE: RedStone -->
## Exact API reference

> Generated from `contracts/priceSources/RedStone.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, address _ethAddr, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd)` | `2–4` | `_staleTime`, `_needsEthToUsd` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getRedStoneData(address _feed, uint256 _decimals, uint256 _staleTime)` | `2–3` | `_staleTime` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `updatePriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd)` | `2–4` | `_staleTime`, `_needsEthToUsd` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `ETH()` | `view` | `address` |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `addNewPriceFeed(address _asset, address _newFeed)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd)` | `nonpayable` | `bool` |
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
| `feedConfig(address arg0)` | `view` | `(address,uint256,bool,uint256)` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getGovernors()` | `view` | `address[]` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` |
| `getRedStoneData(address _feed, uint256 _decimals)` | `view` | `uint256` |
| `getRedStoneData(address _feed, uint256 _decimals, uint256 _staleTime)` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `getRipeHqFromGov()` | `view` | `address` |
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
| `isValidNewFeed(address _asset, address _newFeed, uint256 _decimals, bool _needsEthToUsd, uint256 _staleTime)` | `view` | `bool` |
| `isValidStaleTimeUpdate(address _asset, uint256 _staleTime)` | `view` | `bool` |
| `isValidUpdateFeed(address _asset, address _newFeed, uint256 _decimals, bool _needsEthToUsd, uint256 _staleTime)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingUpdates(address arg0)` | `view` | `(uint256,(address,uint256,bool,uint256))` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |
| `updatePriceFeed(address _asset, address _newFeed)` | `nonpayable` | `bool` |
| `updatePriceFeed(address _asset, address _newFeed, uint256 _staleTime)` | `nonpayable` | `bool` |
| `updatePriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd)` | `nonpayable` | `bool` |
| `updateStaleTime(address _asset, uint256 _staleTime)` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DisableRedStoneFeedCancelled` | `address asset indexed, address feed indexed` |
| `DisableRedStoneFeedPending` | `address asset indexed, address feed indexed, uint256 confirmationBlock, uint256 actionId` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewRedStoneFeedAdded` | `address asset indexed, address feed indexed, bool needsEthToUsd, uint256 staleTime` |
| `NewRedStoneFeedCancelled` | `address asset indexed, address feed indexed` |
| `NewRedStoneFeedPending` | `address asset indexed, address feed indexed, bool needsEthToUsd, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RedStoneFeedDisabled` | `address asset indexed, address feed indexed` |
| `RedStoneFeedUpdateCancelled` | `address asset indexed, address feed indexed, address oldFeed indexed` |
| `RedStoneFeedUpdatePending` | `address asset indexed, address feed indexed, bool needsEthToUsd, uint256 staleTime, uint256 confirmationBlock, address oldFeed indexed, uint256 actionId` |
| `RedStoneFeedUpdated` | `address asset indexed, address feed indexed, bool needsEthToUsd, uint256 staleTime, address oldFeed indexed` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `ChainlinkRound(roundId: uint80, answer: int256, startedAt: uint256, updatedAt: uint256, answeredInRound: uint80)`
- `RedStoneConfig(feed: address, decimals: uint256, needsEthToUsd: bool, staleTime: uint256)`
- `PendingRedStoneConfig(actionId: uint256, config: RedStoneConfig)`

<!-- END GENERATED API REFERENCE: RedStone -->
