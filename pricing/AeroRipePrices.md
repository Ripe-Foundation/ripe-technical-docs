# AeroRipePrices Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/priceSources/AeroRipePrices.vy)

## Overview

AeroRipePrices is a specialized price source for the RIPE token in Ripe Protocol. It calculates RIPE price from Aerodrome liquidity pools using a time-weighted average price (TWAP) mechanism with snapshot-based price smoothing to prevent manipulation.

**Core Features**:
- **Aerodrome Pool Integration**: Derives price from RIPE/WETH Aerodrome Classic pool
- **TWAP Mechanism**: Uses weighted average of historical snapshots
- **Manipulation Resistance**: Throttles upside price movements
- **Configurable Parameters**: Adjustable snapshot delay, count, and deviation limits

## Architecture & Modules

AeroRipePrices uses the standard price source architecture:

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

## Data Structures

### PriceConfig

Configuration for price feed behavior:

```vyper
struct PriceConfig:
    minSnapshotDelay: uint256    # Minimum time between snapshots
    maxNumSnapshots: uint256     # Maximum snapshots for TWAP
    maxUpsideDeviation: uint256  # Max upside % change per snapshot
    staleTime: uint256           # Time after which snapshot is stale
    lastSnapshot: PriceSnapshot  # Most recent snapshot
    nextIndex: uint256           # Next snapshot index (circular)
```

### PriceSnapshot

Individual price observation:

```vyper
struct PriceSnapshot:
    price: uint256       # Price at snapshot time
    lastUpdate: uint256  # Block timestamp
```

### PendingPriceConfig

Pending configuration update:

```vyper
struct PendingPriceConfig:
    actionId: uint256    # Time lock action ID
    config: PriceConfig  # Proposed configuration
```

## Events

### PriceConfigUpdatePending

Emitted when a config update is initiated:

```vyper
event PriceConfigUpdatePending:
    asset: indexed(address)
    minSnapshotDelay: uint256
    maxNumSnapshots: uint256
    maxUpsideDeviation: uint256
    staleTime: uint256
    confirmationBlock: uint256
    actionId: uint256
```

### PriceSnapshotAdded

Emitted when a new price snapshot is recorded:

```vyper
event PriceSnapshotAdded:
    asset: indexed(address)
    price: uint256
    lastUpdate: uint256
```

## State Variables

### Public Variables

- `priceConfigs: HashMap[address, PriceConfig]` - Asset price configurations
- `snapShots: HashMap[address, HashMap[uint256, PriceSnapshot]]` - Price snapshots per asset
- `pendingPriceConfigs: HashMap[address, PendingPriceConfig]` - Pending config updates

### Immutable Variables

- `RIPE_WETH_POOL: immutable(address)` - Aerodrome RIPE/WETH pool
- `RIPE_TOKEN: immutable(address)` - RIPE token address

### Constants

- `HUNDRED_PERCENT: constant(uint256) = 100_00` - 100% in basis points
- `EIGHTEEN_DECIMALS: constant(uint256) = 10 ** 18` - Standard decimal precision

## Constructor

### `__init__`

Initializes AeroRipePrices with pool and token addresses.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _tempGov: address,
    _ripeWethPool: address,
    _ripeToken: address,
    _minPriceChangeTimeLock: uint256,
    _maxPriceChangeTimeLock: uint256,
):
```

#### Parameters

| Name                      | Type      | Description                           |
| ------------------------- | --------- | ------------------------------------- |
| `_ripeHq`                 | `address` | RipeHq contract address               |
| `_tempGov`                | `address` | Temporary governance address          |
| `_ripeWethPool`           | `address` | Aerodrome RIPE/WETH pool address      |
| `_ripeToken`              | `address` | RIPE token address                    |
| `_minPriceChangeTimeLock` | `uint256` | Minimum blocks for time-locked actions|
| `_maxPriceChangeTimeLock` | `uint256` | Maximum blocks for time-locked actions|

#### Default Config

If `_ripeToken` is not empty, initializes with:
- `minSnapshotDelay`: 5 minutes (300 seconds)
- `maxNumSnapshots`: 20
- `maxUpsideDeviation`: 10% (10_00)
- `staleTime`: 0 (no expiry)

## Core Functions

### `getPrice`

Returns the RIPE token price.

```vyper
@view
@external
def getPrice(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> uint256:
```

#### Parameters

| Name         | Type      | Description                                  |
| ------------ | --------- | -------------------------------------------- |
| `_asset`     | `address` | Asset to get price for (must be RIPE_TOKEN)  |
| `_staleTime` | `uint256` | Stale time (not used - config has own value) |
| `_priceDesk` | `address` | Optional PriceDesk address                   |

#### Returns

| Type      | Description                              |
| --------- | ---------------------------------------- |
| `uint256` | Price in 18-decimal USD (0 if not RIPE)  |

#### Behavior

1. Returns 0 if asset is not RIPE_TOKEN
2. Gets current Aerodrome pool price
3. Gets weighted average from snapshots
4. Returns minimum of spot price and TWAP (conservative)

### `getPriceAndHasFeed`

Returns price and feed status.

```vyper
@view
@external
def getPriceAndHasFeed(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> (uint256, bool):
```

### `hasPriceFeed`

Checks if asset has a price feed.

```vyper
@view
@external
def hasPriceFeed(_asset: address) -> bool:
```

### `hasPendingPriceFeedUpdate`

Checks for pending config updates.

```vyper
@view
@external
def hasPendingPriceFeedUpdate(_asset: address) -> bool:
```

### `getAeroRipePrice`

Returns the raw Aerodrome pool spot price.

```vyper
@view
@external
def getAeroRipePrice(_asset: address) -> uint256:
```

### `getWeightedPrice`

Returns the TWAP from snapshots.

```vyper
@view
@external
def getWeightedPrice(_asset: address) -> uint256:
```

## Configuration Functions

### `updatePriceConfig`

Initiates a price config update (time-locked).

```vyper
@external
def updatePriceConfig(
    _minSnapshotDelay: uint256,
    _maxNumSnapshots: uint256,
    _maxUpsideDeviation: uint256,
    _staleTime: uint256,
) -> bool:
```

#### Parameters

| Name                   | Type      | Description                          |
| ---------------------- | --------- | ------------------------------------ |
| `_minSnapshotDelay`    | `uint256` | Min seconds between snapshots        |
| `_maxNumSnapshots`     | `uint256` | Max snapshots for TWAP (1-25)        |
| `_maxUpsideDeviation`  | `uint256` | Max upside % (in basis points)       |
| `_staleTime`           | `uint256` | Snapshot expiry time (0 = no expiry) |

#### Access

Only callable by governance

### `isValidPriceConfig`

Validates proposed configuration.

```vyper
@view
@external
def isValidPriceConfig(
    _minSnapshotDelay: uint256,
    _maxNumSnapshots: uint256,
    _maxUpsideDeviation: uint256,
    _staleTime: uint256,
) -> bool:
```

#### Validation Rules

- `minSnapshotDelay` <= 1 week
- `maxNumSnapshots` between 1 and 25
- `maxUpsideDeviation` <= 100%

## Snapshot Functions

### `addPriceSnapshot`

Adds a new price snapshot.

```vyper
@external
def addPriceSnapshot(_asset: address) -> bool:
```

#### Parameters

| Name     | Type      | Description                    |
| -------- | --------- | ------------------------------ |
| `_asset` | `address` | Asset to snapshot (RIPE_TOKEN) |

#### Access

Only callable by valid Ripe protocol addresses

#### Behavior

1. Returns false if asset is not RIPE_TOKEN
2. Checks minimum delay since last snapshot
3. Gets current Aerodrome price
4. Throttles upside deviation if needed
5. Stores snapshot in circular buffer
6. Emits `PriceSnapshotAdded` event

### `getLatestSnapshot`

Returns the most recent snapshot data.

```vyper
@view
@external
def getLatestSnapshot(_asset: address) -> PriceSnapshot:
```

## Price Calculation

### Aerodrome Pool Price

```
1. Get reserves (reserve0, reserve1) from pool
2. Calculate price of token0 in terms of token1: reserve1 * 1e18 / reserve0
3. Adjust for decimal differences
4. If RIPE is token1, invert the price
5. Multiply by other token's USD price from PriceDesk
```

### Weighted Average (TWAP)

```
1. Sum up: price * weight for all valid (non-stale) snapshots
2. Divide by total weight (number of valid snapshots)
3. If no valid snapshots, use last snapshot price
```

### Final Price

```
finalPrice = min(spotPrice, twapPrice)
```

Using the minimum provides manipulation resistance.

## Security Considerations

1. **TWAP Protection**: Historical average smooths out sudden price spikes
2. **Upside Throttling**: Limits how much price can increase per snapshot
3. **Conservative Pricing**: Uses minimum of spot and TWAP
4. **Time-Locked Config**: Configuration changes require time lock
5. **Circular Buffer**: Fixed memory usage for snapshots
6. **Decimal Handling**: Properly normalizes different token decimals

## Integration Points

### Depends On:
- **Aerodrome Classic Pool**: For reserve data
- **PriceDesk**: For WETH price (or paired token price)

### Used By:
- **PriceDesk**: Registered as price source for RIPE token
