# wsuperOETHbPrices Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/priceSources/wsuperOETHbPrices.vy)

## Overview

wsuperOETHbPrices is a specialized price source for wrapped superOETHb tokens in Ripe Protocol. It calculates the price of wsuperOETHb by combining the underlying superOETH price with the vault's share-to-asset conversion rate.

**Core Features**:
- **Wrapped Token Pricing**: Prices wsuperOETHb based on underlying superOETH value
- **ERC4626 Integration**: Uses `convertToAssets` for share price calculation
- **PriceDesk Integration**: Fetches underlying asset prices from protocol price oracle
- **Standard Price Source Interface**: Implements the PriceSource interface

## Architecture & Modules

wsuperOETHbPrices uses the standard price source architecture:

### LocalGov Module

- **Location**: `contracts/modules/LocalGov.vy`
- **Purpose**: Provides governance functionality
- **Documentation**: See [LocalGov Technical Documentation](../governance/LocalGov.md)
- **Exported Interface**: Governance utilities via `gov.__interface__`

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../core-modules/Addys.md)
- **Exported Interface**: Address utilities via `addys.__interface__`

### PriceSourceData Module

- **Location**: `contracts/priceSources/modules/PriceSourceData.vy`
- **Purpose**: Provides base price source functionality
- **Documentation**: See [PriceSourceData Technical Documentation](./modules/PriceSourceData.md)
- **Exported Interface**: Price source data via `priceData.__interface__`

### TimeLock Module

- **Location**: `contracts/modules/TimeLock.vy`
- **Purpose**: Provides time-locked action management
- **Documentation**: See [TimeLock Technical Documentation](../governance/TimeLock.md)
- **Exported Interface**: Time lock utilities via `timeLock.__interface__`

### Module Initialization

```vyper
initializes: gov
initializes: addys
initializes: priceData[addys := addys]
initializes: timeLock[gov := gov]
```

## State Variables

### Immutable Variables

- `SUPER_OETH: immutable(address)` - The superOETH token address
- `WRAPPED_SUPER_OETH: immutable(address)` - The wrapped superOETHb token address

## Constructor

### `__init__`

Initializes wsuperOETHbPrices with token addresses and time lock parameters.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _superOETH: address,
    _wrappedSuperOETH: address,
    _minPriceChangeTimeLock: uint256,
    _maxPriceChangeTimeLock: uint256,
):
```

#### Parameters

| Name                      | Type      | Description                         |
| ------------------------- | --------- | ----------------------------------- |
| `_ripeHq`                 | `address` | RipeHq contract address             |
| `_superOETH`              | `address` | superOETH token address             |
| `_wrappedSuperOETH`       | `address` | wsuperOETHb token address           |
| `_minPriceChangeTimeLock` | `uint256` | Minimum blocks for time-locked actions |
| `_maxPriceChangeTimeLock` | `uint256` | Maximum blocks for time-locked actions |

#### Example Usage

```python
# Deploy wsuperOETHbPrices
prices = boa.load(
    "contracts/priceSources/wsuperOETHbPrices.vy",
    ripe_hq.address,
    super_oeth.address,
    wsuperOETHb.address,
    100,  # min time lock blocks
    1000  # max time lock blocks
)
```

## Core Functions

### `getPrice`

Returns the price of wsuperOETHb in 18-decimal USD.

```vyper
@view
@external
def getPrice(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> uint256:
```

#### Parameters

| Name         | Type      | Description                                      |
| ------------ | --------- | ------------------------------------------------ |
| `_asset`     | `address` | Asset to get price for (must be wsuperOETHb)     |
| `_staleTime` | `uint256` | Stale time (unused in this implementation)       |
| `_priceDesk` | `address` | Optional PriceDesk address (uses default if empty)|

#### Returns

| Type      | Description                                  |
| --------- | -------------------------------------------- |
| `uint256` | Price in 18-decimal USD (0 if not wsuperOETHb) |

#### Behavior

1. Returns 0 if asset is not wsuperOETHb
2. Fetches superOETH price from PriceDesk
3. Gets share-to-asset conversion rate from vault
4. Returns: `superOethPrice * pricePerShare / 1e18`

### `getPriceAndHasFeed`

Returns the price and whether a feed exists for the asset.

```vyper
@view
@external
def getPriceAndHasFeed(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> (uint256, bool):
```

#### Parameters

| Name         | Type      | Description                                      |
| ------------ | --------- | ------------------------------------------------ |
| `_asset`     | `address` | Asset to get price for                           |
| `_staleTime` | `uint256` | Stale time (unused)                              |
| `_priceDesk` | `address` | Optional PriceDesk address                       |

#### Returns

| Type      | Description                                  |
| --------- | -------------------------------------------- |
| `uint256` | Price in 18-decimal USD                      |
| `bool`    | True if asset has a price feed               |

### `hasPriceFeed`

Checks if the asset has a price feed configured.

```vyper
@view
@external
def hasPriceFeed(_asset: address) -> bool:
```

#### Parameters

| Name     | Type      | Description           |
| -------- | --------- | --------------------- |
| `_asset` | `address` | Asset to check        |

#### Returns

| Type   | Description                                  |
| ------ | -------------------------------------------- |
| `bool` | True if asset equals WRAPPED_SUPER_OETH      |

### `hasPendingPriceFeedUpdate`

Checks if there's a pending price feed update.

```vyper
@view
@external
def hasPendingPriceFeedUpdate(_asset: address) -> bool:
```

#### Returns

| Type   | Description       |
| ------ | ----------------- |
| `bool` | Always returns False (no pending updates supported) |

## Price Calculation

The price is calculated as:

```
wsuperOETHb_price = superOETH_price * (convertToAssets(1e18) / 1e18)
```

Where:
- `superOETH_price` is fetched from PriceDesk
- `convertToAssets(1e18)` returns how many underlying tokens 1 share is worth

## Interface Functions (No-op)

These functions are implemented to satisfy the PriceSource interface but have no effect:

- `confirmNewPriceFeed` - Returns `True`
- `cancelNewPendingPriceFeed` - Returns `True`
- `confirmPriceFeedUpdate` - Returns `True`
- `cancelPriceFeedUpdate` - Returns `True`
- `confirmDisablePriceFeed` - Returns `True`
- `cancelDisablePriceFeed` - Returns `True`
- `addPriceSnapshot` - Returns `False`
- `disablePriceFeed` - Returns `False`

## Security Considerations

1. **Single Asset**: Only prices the specific wsuperOETHb token
2. **Immutable Addresses**: Token addresses cannot be changed after deployment
3. **PriceDesk Dependency**: Relies on underlying superOETH price from PriceDesk
4. **No State Manipulation**: No complex state that could be exploited
5. **ERC4626 Trust**: Trusts the vault's `convertToAssets` implementation

## Integration Points

### Depends On:
- **PriceDesk**: For underlying superOETH price
- **wsuperOETHb Vault**: For share-to-asset conversion

### Used By:
- **PriceDesk**: Registered as price source for wsuperOETHb
