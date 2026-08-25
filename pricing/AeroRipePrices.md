# AeroRipePrices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/AeroRipePrices.vy)

## Status and purpose

`AeroRipePrices` is a **monitoring-only** reader for the canonical 18-decimal RIPE/WETH Aerodrome Classic pool. It implements the `PriceSource` compatibility interface but intentionally exposes no usable feed and must not be configured as an ordinary PriceDesk source. Its reserve-derived values cannot be used for collateral, borrowing, liquidation, or accounting.

Every feed-facing method is deliberately inert. The useful surface consists of reserve and indicative-price views for dashboards and monitoring.

## Constructor binding

The constructor takes:

```text
__init__(ripeHq, ripeWethPool, ripeToken, wethToken)
```

Construction rejects:

- any zero address;
- identical RIPE and WETH token addresses;
- a pool whose two tokens are not exactly the supplied RIPE/WETH pair; or
- a RIPE or WETH token whose `decimals()` result is not 18.

The contract records `RIPE_IS_TOKEN0` so all returned reserve values use RIPE-first ordering regardless of the pool's native token order.

## Monitoring views

### `isMonitoringOnly()`

Always returns `true`. Integrators should use this as an explicit capability signal and should still treat all monitoring values as informational.

### `getRipePoolState()`

Returns `(ripeReserve, wethReserve, lastUpdate)`. Returned reserve values above `uint112` or an update value above `uint32` fail soft to `(0, 0, 0)` as conservative sanity bounds. A reverting or ABI-incompatible pool dependency still propagates a revert.

Aerodrome's reserve return types are wider than these bounds; the checks are monitor policy, not a claim about the pool's storage layout.

### `getRipeWethMonitoringPrice()`

Returns an 18-decimal spot ratio:

```text
wethReserve * 1e18 / ripeReserve
```

It returns zero if reserve data is invalid or either reserve is zero. This is a reserve ratio, not a TWAP and not a manipulation-resistant oracle.

### `getRipeUsdMonitoringPrice()`

Reads the current PriceDesk address dynamically from RipeHq's canonical PriceDesk registry slot, asks it for the non-raising WETH/USD price, and multiplies that value by the RIPE/WETH reserve ratio. It returns zero when:

- pool data is invalid;
- a reserve is zero;
- PriceDesk is not registered;
- PriceDesk has no usable WETH price; or
- checked multiplication would overflow.

Resolving PriceDesk dynamically prevents a registry rotation from leaving the monitor pointed at an obsolete address. Neither the lookup nor the result creates a RIPE price feed.

A reverting or ABI-incompatible RipeHq or PriceDesk dependency can propagate a
revert. The zero-result cases above describe values returned successfully by
those dependencies, not universal dependency-failure isolation.

### `getAeroRipePrice(asset)`

USD monitoring alias that returns zero unless `asset` is the configured RIPE
token. `getRipeUsdMonitoringPrice()` provides the same view without an asset
argument.

## Inert `PriceSource` compatibility surface

The following behavior is intentional:

| Method family | Result |
| --- | --- |
| `getPrice(...)` | `0` |
| `getPriceAndHasFeed(...)` | `(0, false)` |
| `hasPriceFeed(...)`, `hasPendingPriceFeedUpdate(...)` | `false` |
| `getPricedAssets()` | empty list |
| `addPriceSnapshot`, `confirmNewPriceFeed`, `cancelNewPendingPriceFeed`, `confirmPriceFeedUpdate`, `cancelPriceFeedUpdate`, `disablePriceFeed`, `confirmDisablePriceFeed`, `cancelDisablePriceFeed` | `false` |
| timelock getters | `0` or `false` |
| timelock setters | `false` |
| `isPaused()` | `false` |
| `pause(...)`, `recoverFunds(...)`, `recoverFundsMany(...)` | revert with `monitoring only` |

There is no `PriceConfig`, snapshot history, weighted price, configuration validation, or active governance lifecycle in this contract.

## Integration and safety guidance

- Never submit this contract as a PriceDesk source.
- AddressRegistry can technically register the contract, but it would remain an
  inert `(0, false)` no-feed candidate.
- Never use its reserve ratio as a protocol oracle or as proof of executable liquidity.
- Treat zero as “unavailable,” not as a zero-dollar RIPE valuation.
- Prefer the explicit monitoring views; the inert compatibility functions exist only to satisfy a shared interface.

<!-- BEGIN GENERATED API REFERENCE: AeroRipePrices -->
## Exact API reference

> Generated from `contracts/priceSources/AeroRipePrices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _ripeWethPool, address _ripeToken, address _wethToken)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `getPrice(address _asset, uint256 _staleTime, address _oracleRegistry)` | `1–3` | `_staleTime = 0`, `_oracleRegistry = empty(address)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _oracleRegistry)` | `1–3` | `_staleTime = 0`, `_oracleRegistry = empty(address)` |
| `setActionTimeLockAfterSetup(uint256 _numBlocks)` | `0–1` | `_numBlocks = 0` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `RIPE_HQ()` | `view` | `address` | — |
| `RIPE_IS_TOKEN0()` | `view` | `bool` | — |
| `RIPE_TOKEN()` | `view` | `address` | — |
| `RIPE_WETH_POOL()` | `view` | `address` | — |
| `WETH_TOKEN()` | `view` | `address` | — |
| `actionTimeLock()` | `view` | `uint256` | `uint256` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` | `bool` |
| `cancelDisablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `cancelNewPendingPriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `cancelPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmDisablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmNewPriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `confirmPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` | `bool` |
| `disablePriceFeed(address _asset)` | `nonpayable` | `bool` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | `uint256` |
| `getAeroRipePrice(address _asset)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _oracleRegistry)` | `view` | `uint256` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _oracleRegistry)` | `view` | `(uint256, bool)` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `address[]` | `DynArray[address, 50]` |
| `getRipePoolState()` | `view` | `(uint256, uint256, uint256)` | `(uint256, uint256, uint256)` |
| `getRipeUsdMonitoringPrice()` | `view` | `uint256` | `uint256` |
| `getRipeWethMonitoringPrice()` | `view` | `uint256` | `uint256` |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | `bool` |
| `hasPendingPriceFeedUpdate(address _asset)` | `view` | `bool` | `bool` |
| `hasPriceFeed(address _asset)` | `view` | `bool` | `bool` |
| `isMonitoringOnly()` | `view` | `bool` | `bool` |
| `isPaused()` | `view` | `bool` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` | `bool` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid monitoring config`
- `invalid monitoring tokens`
- `invalid ripe decimals`
- `invalid weth decimals`
- `monitoring only`
- `not ripe weth pool`

<!-- END GENERATED API REFERENCE: AeroRipePrices -->
