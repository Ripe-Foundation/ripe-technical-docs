# PythPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/PythPrices.vy)

## Overview

`PythPrices` maps assets to Pyth feed IDs, normalizes Pyth values to 18 decimals, applies a conservative confidence adjustment, and exposes authorized paid and prepaid batch update routes.

## Feed and price model

Each asset stores:

```text
PythFeedConfig(feedId: bytes32, staleTime: uint256)
```

`getPrice` returns zero for a missing feed or unusable data. `getPriceAndHasFeed` returns `hasFeed = true` for a configured feed even when its current price is zero. `getLastPriceAndLastUpdate` returns the adjusted price and publish time without applying a stale-time bound, while still enforcing all other data checks.

The raw `PythPrice` contains signed `price`, unsigned `confidence`, signed `exponent`, and `publishTime`. The source:

1. rejects nonpositive prices and future publish times;
2. applies the effective freshness policy;
3. scales price and confidence to 18 decimals using the signed exponent;
4. rejects `confidence >= price`;
5. rejects a confidence ratio above `maxConfidenceRatio` when that control is nonzero; and
6. returns `price - confidence`.

The default maximum confidence ratio is 3% (`3_00` basis points). Switchboard may change it while the source is unpaused; the value must remain below 100%. A value of zero disables the ratio ceiling, but the `confidence < price` requirement remains.

## Freshness policy

Only the canonical PriceDesk may forward a nonzero global stale time. A direct call uses zero and lets the source resolve MissionControl when the feed inherits.

- nonzero feed `staleTime` is an absolute override;
- zero feed `staleTime` inherits MissionControl;
- local overrides must be 5 minutes through 7 days; and
- an effective/global nonzero policy above 7 days is invalid.

There is no `min(global, feed)` cap.

## Typed batch updates

Both update routes accept the current batch type:

```text
DynArray[Bytes[2048], 20]
```

Only these typed batch routes are exposed; integrations should encode the payload as `bytes[]`.

### `updatePythPrice(payload)`

This payable route requires a MissionControl-authorized lite-action caller and nonzero `msg.value`. It asks Pyth for the batch fee, pays exactly that fee, emits `PythPriceUpdated(payload, feeAmount, caller)`, and refunds excess ETH to the caller.

### `updatePythPriceNoPay(payload)`

This nonpayable route has the same lite-action authorization. It funds the update from the contract's existing ETH balance and does not refund unused balance to the caller.

Both routes revert if available payment is below Pyth's reported fee. Governance may withdraw the entire ETH balance to a nonzero recipient with `recoverEthBalance`.

## Feed lifecycle

Governance controls timelocked add, update, stale-time update, and disable operations. New and updated configurations must identify an existing Pyth feed and produce a currently valid nonzero adjusted price. Confirmation revalidates the candidate before changing active state.

`updatePriceFeed(asset, feedId, staleTime = 0)` preserves the current local stale-time value when the optional value is omitted. `updateStaleTime` explicitly changes the policy, including setting zero to inherit global policy.

`addPriceSnapshot` returns false; PythPrices has no internal snapshot history.

## Integration requirements

- Encode updates as `bytes[]` with at most 20 elements and each element at most 2,048 bytes.
- Use the canonical typed batch routes shown above.
- Treat feed configuration and a current usable price as separate states.
- Use PriceDesk for protocol price reads.

<!-- BEGIN GENERATED API REFERENCE: PythPrices -->
## Exact API reference

> Generated from `contracts/priceSources/PythPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, address _pythNetwork, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addNewPriceFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `2–3` | `_staleTime = 0` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime = 0`, `_priceDesk = empty(address)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime = 0`, `_priceDesk = empty(address)` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |
| `updatePriceFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `2–3` | `_staleTime = 0` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `PYTH()` | `view` | `address` | — |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `addNewPriceFeed(address _asset, bytes32 _feedId)` | `nonpayable` | `bool` | `bool` |
| `addNewPriceFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |
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
| `feedConfig(address arg0)` | `view` | `(bytes32 feedId, uint256 staleTime)` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getLastPriceAndLastUpdate(address _asset)` | `view` | `(uint256, uint256)` | `(uint256, uint256)` |
| `getPrice(address _asset)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `uint256` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` | — |
| `getRipeHq()` | `view` | `address` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
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
| `isValidNewFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `view` | `bool` | `bool` |
| `isValidStaleTimeUpdate(address _asset, uint256 _staleTime)` | `view` | `bool` | `bool` |
| `isValidUpdateFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `view` | `bool` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxConfidenceRatio()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `numAssets()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingUpdates(address arg0)` | `view` | `(uint256 actionId, (bytes32 feedId, uint256 staleTime) config)` | — |
| `recoverEthBalance(address _recipient)` | `nonpayable` | `bool` | `bool` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setMaxConfidenceRatio(uint256 _newRatio)` | `nonpayable` | `bool` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `updatePriceFeed(address _asset, bytes32 _feedId)` | `nonpayable` | `bool` | `bool` |
| `updatePriceFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |
| `updatePythPrice(bytes[] _payload)` | `payable` | `bool` | `bool` |
| `updatePythPriceNoPay(bytes[] _payload)` | `nonpayable` | `bool` | `bool` |
| `updateStaleTime(address _asset, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DisablePythFeedCancelled` | `address asset indexed, bytes32 feedId` |
| `DisablePythFeedPending` | `address asset indexed, bytes32 feedId, uint256 confirmationBlock, uint256 actionId` |
| `EthRecoveredFromPyth` | `address recipient indexed, uint256 amount` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `MaxConfidenceRatioUpdated` | `uint256 newRatio` |
| `NewPythFeedAdded` | `address asset indexed, bytes32 feedId, uint256 staleTime` |
| `NewPythFeedCancelled` | `address asset indexed, bytes32 feedId` |
| `NewPythFeedPending` | `address asset indexed, bytes32 feedId, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `PythFeedDisabled` | `address asset indexed, bytes32 feedId` |
| `PythFeedUpdateCancelled` | `address asset indexed, bytes32 feedId, bytes32 oldFeedId` |
| `PythFeedUpdatePending` | `address asset indexed, bytes32 feedId, uint256 staleTime, uint256 confirmationBlock, bytes32 oldFeedId, uint256 actionId` |
| `PythFeedUpdated` | `address asset indexed, bytes32 feedId, uint256 staleTime, bytes32 oldFeedId` |
| `PythPriceUpdated` | `bytes[] payload, uint256 feeAmount, address caller indexed` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `PythPrice(price: int64, confidence: uint64, exponent: int32, publishTime: uint64)`
- `PythFeedConfig(feedId: bytes32, staleTime: uint256)`
- `PendingPythFeed(actionId: uint256, config: PythFeedConfig)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot cancel action`
- `contract paused`
- `insufficient payment`
- `invalid asset`
- `invalid feed`
- `invalid pyth network`
- `invalid recipient or balance`
- `no pending disable feed`
- `no pending new feed`
- `no pending update feed`
- `no perms`
- `not authorized`
- `payment required`
- `pending feed action`
- `ratio already set`
- `ratio must be < 100%`
- `time lock not reached`

<!-- END GENERATED API REFERENCE: PythPrices -->
