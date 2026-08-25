# StorkPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/StorkPrices.vy)

## Overview

`StorkPrices` maps assets to Stork feed IDs, validates Stork temporal numeric values, and exposes authorized paid and prepaid typed batch-update routes.

## Data types

Each asset stores `StorkFeedConfig(feedId, staleTime)`. Stork price data and update input use the canonical nested structs:

```text
TemporalNumericValue:
  timestampNs: uint64
  quantizedValue: int192

TemporalNumericValueInput:
  temporalNumericValue: TemporalNumericValue
  id: bytes32
  publisherMerkleRoot: bytes32
  valueComputeAlgHash: bytes32
  r: bytes32
  s: bytes32
  v: uint8
```

The update batch is `DynArray[TemporalNumericValueInput, 20]`; integrations must ABI-encode that exact typed array.

## Price validation

Stork quantized values are already 18-decimal prices. The source rejects a nonpositive signed value.

`timestampNs` is converted to whole seconds by integer division by `1_000_000_000`. A zero or future whole-second timestamp is invalid. A sub-second value within the current second truncates to the current second and is accepted if it satisfies the effective freshness policy.

`getPrice` returns zero for missing or invalid data. `getPriceAndHasFeed` returns `hasFeed = true` when a feed is configured even if the current value is unusable.

## Freshness policy

Only the PriceDesk currently registered in RipeHq may forward a nonzero global policy, and it must identify itself in the third call argument.

- a nonzero feed stale time is an absolute override;
- zero inherits MissionControl's global value;
- local overrides must be 5 minutes through 7 days; and
- an effective/global nonzero value above 7 days is invalid.

The source does not take the minimum of local and global values.

## Typed batch updates

### `updateStorkPrice(payload)`

Requires a MissionControl-authorized lite-action caller, nonzero `msg.value`, and sufficient payment for `getUpdateFeeV1(payload)`. It calls `updateTemporalNumericValuesV1`, emits `StorkPriceUpdated` with the full typed payload, fee, and caller, and refunds excess ETH.

### `updateStorkPriceNoPay(payload)`

Uses the contract's existing ETH balance and does not refund the caller. Authorization and fee sufficiency are otherwise the same.

Governance may withdraw the contract's full ETH balance to a nonzero recipient using `recoverEthBalance`.

## Feed lifecycle

Governance controls timelocked add, update, stale-time update, and disable actions. Admission requires a nonzero asset/feed ID and a currently valid positive price. Confirmation revalidates the pending candidate before installing it.

An omitted stale-time argument to `updatePriceFeed` preserves the existing local value. `updateStaleTime` is the explicit policy change, including returning to inheritance with zero.

`addPriceSnapshot` returns false because this source has no internal snapshot history.

## Integration requirements

- ABI-encode the exact nested tuple array; an opaque bytes blob is incompatible.
- Use the canonical typed batch routes shown above.
- Treat zero as unavailable and distinguish it from `hasPriceFeed`.

<!-- BEGIN GENERATED API REFERENCE: StorkPrices -->
## Exact API reference

> Generated from `contracts/priceSources/StorkPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, address _stork, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

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
| `STORK()` | `view` | `address` | — |
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
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `updatePriceFeed(address _asset, bytes32 _feedId)` | `nonpayable` | `bool` | `bool` |
| `updatePriceFeed(address _asset, bytes32 _feedId, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |
| `updateStaleTime(address _asset, uint256 _staleTime)` | `nonpayable` | `bool` | `bool` |
| `updateStorkPrice(((uint64,int192),bytes32,bytes32,bytes32,bytes32,bytes32,uint8)[] _payload)` | `payable` | `bool` | `bool` |
| `updateStorkPriceNoPay(((uint64,int192),bytes32,bytes32,bytes32,bytes32,bytes32,uint8)[] _payload)` | `nonpayable` | `bool` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DisableStorkFeedCancelled` | `address asset indexed, bytes32 feedId` |
| `DisableStorkFeedPending` | `address asset indexed, bytes32 feedId, uint256 confirmationBlock, uint256 actionId` |
| `EthRecoveredFromStork` | `address recipient indexed, uint256 amount` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewStorkFeedAdded` | `address asset indexed, bytes32 feedId, uint256 staleTime` |
| `NewStorkFeedCancelled` | `address asset indexed, bytes32 feedId` |
| `NewStorkFeedPending` | `address asset indexed, bytes32 feedId, uint256 staleTime, uint256 confirmationBlock, uint256 actionId` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `StorkFeedDisabled` | `address asset indexed, bytes32 feedId` |
| `StorkFeedUpdateCancelled` | `address asset indexed, bytes32 feedId, bytes32 oldFeedId` |
| `StorkFeedUpdatePending` | `address asset indexed, bytes32 feedId, uint256 staleTime, uint256 confirmationBlock, bytes32 oldFeedId, uint256 actionId` |
| `StorkFeedUpdated` | `address asset indexed, bytes32 feedId, uint256 staleTime, bytes32 oldFeedId` |
| `StorkPriceUpdated` | `((uint64,int192),bytes32,bytes32,bytes32,bytes32,bytes32,uint8)[] payload, uint256 feeAmount, address caller indexed` |

### Structs declared by this source

- `StorkFeedConfig(feedId: bytes32, staleTime: uint256)`
- `PendingStorkFeed(actionId: uint256, config: StorkFeedConfig)`
- `TemporalNumericValue(timestampNs: uint64, quantizedValue: int192)`
- `TemporalNumericValueInput(temporalNumericValue: TemporalNumericValue, id: bytes32, publisherMerkleRoot: bytes32, valueComputeAlgHash: bytes32, r: bytes32, s: bytes32, v: uint8)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot cancel action`
- `contract paused`
- `insufficient payment`
- `invalid asset`
- `invalid feed`
- `invalid recipient or balance`
- `invalid stork network`
- `no pending disable feed`
- `no pending new feed`
- `no pending update feed`
- `no perms`
- `not authorized`
- `payment required`
- `pending feed action`
- `time lock not reached`

<!-- END GENERATED API REFERENCE: StorkPrices -->
