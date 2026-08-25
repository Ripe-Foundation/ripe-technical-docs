# ChainlinkPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/priceSources/ChainlinkPrices.vy)

## Overview

`ChainlinkPrices` maps protocol assets to Chainlink-compatible feeds, normalizes answers to 18 decimals, optionally converts an ETH- or BTC-denominated answer to USD, and manages feed changes through LocalGov and TimeLock.

## Configuration

Each asset has a `ChainlinkConfig`:

```text
feed: address
decimals: uint256
needsEthToUsd: bool
needsBtcToUsd: bool
staleTime: uint256
```

`decimals` is snapshotted when the configuration is admitted. A pending action stores its action ID plus the full proposed config. The constructor binds WETH, ETH, and BTC sentinels and may install direct ETH/USD, WETH/USD, and BTC/USD defaults after validating them.

The source supports at most one conversion leg. Setting both conversion flags is invalid.

## Price reads

`getPrice(asset, staleTime = 0, priceDesk = zero)` returns zero when no feed is configured or any validation fails. `getPriceAndHasFeed` distinguishes “no configured feed” from “configured but currently unusable” by returning the feed Boolean separately.

Chainlink data is usable only when:

- the feed address is nonzero and configured decimals are at most 18;
- `answer` is positive;
- `updatedAt` is not in the future and satisfies the effective freshness policy;
- `roundId` is nonzero; and
- `answeredInRound >= roundId`.

The positive answer is scaled to 18 decimals. Values are not silently accepted when the feed reports more than 18 decimals.

### Conversion routes

An ETH conversion multiplies the primary 18-decimal price by the configured direct ETH/USD anchor. BTC conversion uses the direct BTC/USD anchor. The anchor leg resolves and enforces its own freshness policy; it does not inherit the primary feed's local override.

Routes fail closed when they recurse or alias an anchor, including:

- both conversion flags enabled;
- the priced asset being the chosen anchor;
- the primary feed equal to the anchor feed; or
- an anchor config that itself requests ETH or BTC conversion.

## Freshness policy

A nonzero value forwarded through the price-source interface is accepted only when both `msg.sender` and the supplied registry address are the PriceDesk currently registered in RipeHq. Direct callers may use the zero sentinel but cannot impersonate a protocol-wide freshness policy.

For each primary or anchor leg:

- nonzero feed `staleTime` is an **absolute local override**;
- zero feed `staleTime` inherits MissionControl's global value;
- local override bounds are 5 minutes through 7 days; and
- an effective/global nonzero value above 7 days is invalid.

The contract does not compute `min(global, local)`. A zero or unavailable inherited global policy makes an inheriting feed unusable.

## Feed lifecycle

Governance may initiate add, update, stale-time update, or disable actions while the source is unpaused. Each action occupies the single pending slot for that asset and uses the configured timelock.

Feed admission validates a currently executable nonzero price. Confirmation
revalidates the candidate, including the feed's current `decimals()` value
matching the snapshotted value. If a pending add/update/disable is no longer
valid, confirmation follows the source's cancel-or-false path rather than
installing stale assumptions.

`updatePriceFeed` preserves the current local stale-time policy when its optional stale-time argument is zero. `updateStaleTime` is the explicit way to set a new value, including zero to return to global inheritance.

Feed operations emit the `NewChainlinkFeed*`, `ChainlinkFeedUpdate*`, and `*ChainlinkFeedDisabled*` event families with the proposed/current stale time and relevant old feed.

`addPriceSnapshot` always returns false because this source has no local snapshot history.

## Integration requirements

- Treat a zero price as unavailable, not a valid zero-dollar value.
- Use PriceDesk for protocol reads so fallback, isolation, and global policy are applied.
- Configure conversion anchors as direct USD feeds before depending on converted assets.

<!-- BEGIN GENERATED API REFERENCE: ChainlinkPrices -->
## Exact API reference

> Generated from `contracts/priceSources/ChainlinkPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock, address _wethAddr, address _ethAddr, address _btcAddr, address _ethUsdFeed, address _btcUsdFeed, uint256 _defaultStaleTime)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd, bool _needsBtcToUsd)` | `2–5` | `_staleTime`, `_needsEthToUsd`, `_needsBtcToUsd` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getChainlinkData(address _feed, uint256 _decimals, uint256 _staleTime)` | `2–3` | `_staleTime` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `updatePriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd, bool _needsBtcToUsd)` | `2–5` | `_staleTime`, `_needsEthToUsd`, `_needsBtcToUsd` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `BTC()` | `view` | `address` |
| `ETH()` | `view` | `address` |
| `WETH()` | `view` | `address` |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `addNewPriceFeed(address _asset, address _newFeed)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd)` | `nonpayable` | `bool` |
| `addNewPriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd, bool _needsBtcToUsd)` | `nonpayable` | `bool` |
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
| `feedConfig(address arg0)` | `view` | `(address,uint256,bool,bool,uint256)` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getChainlinkData(address _feed, uint256 _decimals)` | `view` | `uint256` |
| `getChainlinkData(address _feed, uint256 _decimals, uint256 _staleTime)` | `view` | `uint256` |
| `getGovernors()` | `view` | `address[]` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` |
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
| `isValidNewFeed(address _asset, address _newFeed, uint256 _decimals, bool _needsEthToUsd, bool _needsBtcToUsd, uint256 _staleTime)` | `view` | `bool` |
| `isValidStaleTimeUpdate(address _asset, uint256 _staleTime)` | `view` | `bool` |
| `isValidUpdateFeed(address _asset, address _newFeed, uint256 _decimals, bool _needsEthToUsd, bool _needsBtcToUsd, uint256 _staleTime)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingUpdates(address arg0)` | `view` | `(uint256,(address,uint256,bool,bool,uint256))` |
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
| `updatePriceFeed(address _asset, address _newFeed, uint256 _staleTime, bool _needsEthToUsd, bool _needsBtcToUsd)` | `nonpayable` | `bool` |
| `updateStaleTime(address _asset, uint256 _staleTime)` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `ChainlinkFeedDisabled` | `address asset indexed, address feed indexed` |
| `ChainlinkFeedUpdateCancelled` | `address asset indexed, address feed indexed, address oldFeed indexed` |
| `ChainlinkFeedUpdatePending` | `address asset indexed, address feed indexed, bool needsEthToUsd, bool needsBtcToUsd, uint256 staleTime, uint256 confirmationBlock, address oldFeed indexed, uint256 actionId` |
| `ChainlinkFeedUpdated` | `address asset indexed, address feed indexed, bool needsEthToUsd, bool needsBtcToUsd, uint256 staleTime, address oldFeed indexed` |
| `DisableChainlinkFeedCancelled` | `address asset indexed, address feed indexed` |
| `DisableChainlinkFeedPending` | `address asset indexed, address feed indexed, uint256 confirmationBlock, uint256 actionId` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewChainlinkFeedAdded` | `address asset indexed, address feed indexed, bool needsEthToUsd, bool needsBtcToUsd, uint256 staleTime` |
| `NewChainlinkFeedCancelled` | `address asset indexed, address feed indexed` |
| `NewChainlinkFeedPending` | `address asset indexed, address feed indexed, bool needsEthToUsd, bool needsBtcToUsd, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `ChainlinkRound(roundId: uint80, answer: int256, startedAt: uint256, updatedAt: uint256, answeredInRound: uint80)`
- `ChainlinkConfig(feed: address, decimals: uint256, needsEthToUsd: bool, needsBtcToUsd: bool, staleTime: uint256)`
- `PendingChainlinkConfig(actionId: uint256, config: ChainlinkConfig)`

<!-- END GENERATED API REFERENCE: ChainlinkPrices -->
