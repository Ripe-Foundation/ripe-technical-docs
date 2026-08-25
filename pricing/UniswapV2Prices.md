# UniswapV2Prices

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/UniswapV2Prices.vy)

## Status and purpose

`UniswapV2Prices` is a **monitoring-only** reader for a canonical 18-decimal RIPE/WETH Uniswap V2 pair. It implements the `PriceSource` compatibility interface but intentionally exposes no usable feed and must not be configured as an ordinary PriceDesk source. Its reserve-derived values are informational and must not be used for collateral, debt, liquidation, or accounting decisions.

The contract mirrors the monitoring and inert compatibility behavior of `AeroRipePrices`, but discovers the pair through the Uniswap V2 `token0()`, `token1()`, and `getReserves()` interface.

## Constructor binding

```text
__init__(ripeHq, ripeWethPool, ripeToken, wethToken)
```

The constructor rejects zero addresses, identical token addresses, a pair that is not exactly RIPE/WETH, or tokens that do not both report 18 decimals. `RIPE_IS_TOKEN0` records pair order so reserve results are always returned RIPE first.

## Monitoring views

- `isMonitoringOnly()` always returns `true`.
- `getRipePoolState()` returns `(ripeReserve, wethReserve, lastUpdate)`, or all zeros when successfully returned reserve data exceeds the contract's conservative `uint112`/`uint32` sanity bounds.
- `getRipeWethMonitoringPrice()` returns `wethReserve * 1e18 / ripeReserve`, or zero for invalid/empty reserves.
- `getRipeUsdMonitoringPrice()` multiplies the reserve ratio by a non-raising WETH/USD read from RipeHq's current PriceDesk registry entry. Missing registration, missing price, invalid reserves, or arithmetic overflow returns zero.

The USD view resolves PriceDesk on every call so a registry rotation does not stale the monitor. This dynamic dependency does not make the result a registered feed.

Returned but out-of-range reserve data fails soft. A reverting or
ABI-incompatible pair, RipeHq, or PriceDesk dependency can still propagate a
revert from a direct monitoring call.

## Inert `PriceSource` compatibility surface

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

There is no feed configuration, snapshot history, TWAP, or governance-controlled price lifecycle.

## Integration and safety guidance

- Do not register this contract with PriceDesk.
- AddressRegistry can technically register it, but it would remain an inert
  `(0, false)` no-feed candidate.
- Treat a zero result as unavailable.
- A pair reserve ratio is manipulable and is not evidence of executable liquidity.

<!-- BEGIN GENERATED API REFERENCE: UniswapV2Prices -->
## Exact API reference

> Generated from `contracts/priceSources/UniswapV2Prices.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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

<!-- END GENERATED API REFERENCE: UniswapV2Prices -->
