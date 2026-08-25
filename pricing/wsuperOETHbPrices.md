# wsuperOETHbPrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/priceSources/wsuperOETHbPrices.vy)

## Overview

`wsuperOETHbPrices` is a fixed-purpose adapter for the configured wrapped Super OETH token. It composes the Super OETH USD price from PriceDesk with the wrapper's ERC-4626 conversion rate.

The contract stores `MCBETH` and `VVV` immutable constructor addresses but does
**not** price either asset.

## Constructor

```text
__init__(
  ripeHq,
  mcbeth,
  superOETH,
  wrappedSuperOETH,
  vvv,
  minPriceChangeTimeLock,
  maxPriceChangeTimeLock
)
```

`superOETH` and `wrappedSuperOETH` must be nonzero. They are stored as `SUPER_OETH` and `WRAPPED_SUPER_OETH`, and the wrapped token is added to the source's priced-asset list during construction.

`mcbeth` and `vvv` are stored as public immutables but are not required to be nonzero and do not create feed coverage.

## Price behavior

Only `WRAPPED_SUPER_OETH` has a feed:

```text
wrappedPrice = PriceDesk.getPrice(SUPER_OETH, true)
             * wrapped.convertToAssets(1e18)
             / 1e18
```

The Super OETH read is strict. A PriceDesk failure may therefore revert rather than returning a fallback zero. If the strict call returns zero, the adapter returns zero.

For every other asset, including `MCBETH`, `VVV`, and unwrapped `SUPER_OETH`:

- `getPrice` returns zero;
- `getPriceAndHasFeed` returns `(0, false)`; and
- `hasPriceFeed` returns false.

The shared `staleTime` argument is ignored by this adapter. Freshness is determined by the Super OETH source selected through PriceDesk.

## Fixed configuration surface

This contract has no mutable feed lifecycle:

- `hasPendingPriceFeedUpdate` is always false;
- `addPriceSnapshot` and `disablePriceFeed` return false; and
- the interface-required confirm/cancel feed methods return true without changing state.

Those interface-required return values do not indicate that a feed action
occurred.

## Integration requirements

- Register coverage only for `WRAPPED_SUPER_OETH`.
- Do not infer coverage from the `MCBETH` or `VVV` immutable getters.
- Ensure PriceDesk has a strict, usable `SUPER_OETH` feed.
- Verify the target wrapper implements the expected 18-decimal `convertToAssets(1e18)` behavior.

<!-- BEGIN GENERATED API REFERENCE: wsuperOETHbPrices -->
## Exact API reference

> Generated from `contracts/priceSources/wsuperOETHbPrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _mcbeth, address _superOETH, address _wrappedSuperOETH, address _vvv, uint256 _minPriceChangeTimeLock, uint256 _maxPriceChangeTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getPrice(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _priceDesk)` | `1–3` | `_staleTime`, `_priceDesk` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `MCBETH()` | `view` | `address` |
| `SUPER_OETH()` | `view` | `address` |
| `VVV()` | `view` | `address` |
| `WRAPPED_SUPER_OETH()` | `view` | `address` |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
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
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `PriceSourceFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `PriceSourcePauseModified` | `bool isPaused` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

<!-- END GENERATED API REFERENCE: wsuperOETHbPrices -->
