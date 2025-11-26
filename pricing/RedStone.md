# RedStone Technical Documentation

[View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/priceSources/RedStone.vy)

## Overview

RedStone is a price oracle integration for Ripe Protocol that fetches asset prices from RedStone oracle feeds (Chainlink-compatible interface). It supports ETH-to-USD conversion for assets priced in ETH and includes time-locked governance for feed management.

**Core Functions**:
- **Price Retrieval**: Get USD prices for configured assets
- **Feed Management**: Add, update, and disable price feeds with time-locks
- **Decimal Normalization**: Normalize all prices to 18 decimals
- **ETH Conversion**: Optional ETH-to-USD price conversion for ETH-denominated feeds

## Architecture & Modules

### LocalGov Module

- **Location**: `contracts/modules/LocalGov.vy`
- **Purpose**: Provides 2-tier governance for configuration changes
- **Documentation**: See [LocalGov Technical Documentation](../governance-control/LocalGov.md)
- **Exported Interface**: Governance utilities via `gov.__interface__`

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Exported Interface**: Address utilities via `addys.__interface__`

### PriceSourceData Module

- **Location**: `contracts/priceSources/modules/PriceSourceData.vy`
- **Purpose**: Base price source functionality
- **Documentation**: See [PriceSourceData Technical Documentation](./modules/PriceSourceData.md)
- **Exported Interface**: Price source data via `priceData.__interface__`

### TimeLock Module

- **Location**: `contracts/modules/TimeLock.vy`
- **Purpose**: Time-delayed action execution for security
- **Documentation**: See [TimeLock Technical Documentation](../governance-control/TimeLock.md)
- **Exported Interface**: Time lock utilities via `timeLock.__interface__`

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                         RedStone Contract                               |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Price Retrieval                                |  |
|  |                                                                  |  |
|  |  1. Look up feed config for asset                                |  |
|  |  2. Query Chainlink-compatible interface                         |  |
|  |  3. Validate round data and staleness                            |  |
|  |  4. Normalize decimals to 18                                      |  |
|  |  5. Convert ETH → USD if needed                                  |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Feed Management (Time-Locked)                  |  |
|  |                                                                  |  |
|  |  * Add new price feed: initiate → wait → confirm                 |  |
|  |  * Update existing feed: initiate → wait → confirm               |  |
|  |  * Disable feed: initiate → wait → confirm                       |  |
|  |  * Cancel pending actions at any time                            |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| RedStone Feeds   |    | PriceDesk         |    | MissionControl   |
| * Chainlink API  |    | * ETH/USD price   |    | * Stale time     |
| * Price data     |    | * For conversion  |    | * Config         |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### RedStoneConfig Struct

Configuration for an asset's price feed:

```vyper
struct RedStoneConfig:
    feed: address           # Chainlink-compatible feed address
    decimals: uint256       # Feed decimals (for normalization)
    needsEthToUsd: bool     # Whether to convert ETH → USD
    staleTime: uint256      # Maximum age of price data (seconds)
```

### PendingRedStoneConfig Struct

Pending configuration change:

```vyper
struct PendingRedStoneConfig:
    actionId: uint256       # Time lock action ID
    config: RedStoneConfig  # New configuration
```

### ChainlinkRound Struct

Data from Chainlink-compatible oracle:

```vyper
struct ChainlinkRound:
    roundId: uint80         # Round identifier
    answer: int256          # Price answer
    startedAt: uint256      # Round start timestamp
    updatedAt: uint256      # Last update timestamp
    answeredInRound: uint80 # Round when answered
```

## Events

### Feed Addition Events

```vyper
event NewRedStoneFeedPending:
    asset: indexed(address)
    feed: indexed(address)
    needsEthToUsd: bool
    staleTime: uint256
    confirmationBlock: uint256
    actionId: uint256

event NewRedStoneFeedAdded:
    asset: indexed(address)
    feed: indexed(address)
    needsEthToUsd: bool
    staleTime: uint256

event NewRedStoneFeedCancelled:
    asset: indexed(address)
    feed: indexed(address)
```

### Feed Update Events

```vyper
event RedStoneFeedUpdatePending:
    asset: indexed(address)
    feed: indexed(address)
    needsEthToUsd: bool
    staleTime: uint256
    confirmationBlock: uint256
    oldFeed: indexed(address)
    actionId: uint256

event RedStoneFeedUpdated:
    asset: indexed(address)
    feed: indexed(address)
    needsEthToUsd: bool
    staleTime: uint256
    oldFeed: indexed(address)

event RedStoneFeedUpdateCancelled:
    asset: indexed(address)
    feed: indexed(address)
    oldFeed: indexed(address)
```

### Feed Disable Events

```vyper
event DisableRedStoneFeedPending:
    asset: indexed(address)
    feed: indexed(address)
    confirmationBlock: uint256
    actionId: uint256

event RedStoneFeedDisabled:
    asset: indexed(address)
    feed: indexed(address)

event DisableRedStoneFeedCancelled:
    asset: indexed(address)
    feed: indexed(address)
```

## State Variables

### Configuration

- `feedConfig: HashMap[address, RedStoneConfig]` - Asset → feed configuration
- `pendingUpdates: HashMap[address, PendingRedStoneConfig]` - Asset → pending changes

### Immutables

- `ETH: address` - ETH address for price lookups

### Constants

- `NORMALIZED_DECIMALS: uint256 = 18` - Target decimal precision

## Constructor

### `__init__`

Initializes RedStone with governance and time lock settings.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _tempGov: address,
    _ethAddr: address,
    _minPriceChangeTimeLock: uint256,
    _maxPriceChangeTimeLock: uint256,
):
```

#### Parameters

| Name                      | Type      | Description                    |
| ------------------------- | --------- | ------------------------------ |
| `_ripeHq`                 | `address` | RipeHq contract address        |
| `_tempGov`                | `address` | Temporary governance address   |
| `_ethAddr`                | `address` | ETH address for conversions    |
| `_minPriceChangeTimeLock` | `uint256` | Minimum time lock duration     |
| `_maxPriceChangeTimeLock` | `uint256` | Maximum time lock duration     |

## Price Functions

### `getPrice`

Returns the USD price for an asset.

```vyper
@view
@external
def getPrice(
    _asset: address,
    _staleTime: uint256 = 0,
    _priceDesk: address = empty(address)
) -> uint256:
```

#### Parameters

| Name         | Type      | Description                         |
| ------------ | --------- | ----------------------------------- |
| `_asset`     | `address` | Asset to price                      |
| `_staleTime` | `uint256` | Override stale time (0 = use config)|
| `_priceDesk` | `address` | PriceDesk for ETH conversion        |

#### Returns

| Type      | Description                      |
| --------- | -------------------------------- |
| `uint256` | USD price (18 decimals), 0 if no feed |

### `getPriceAndHasFeed`

Returns price and whether a feed exists.

```vyper
@view
@external
def getPriceAndHasFeed(
    _asset: address,
    _staleTime: uint256 = 0,
    _priceDesk: address = empty(address)
) -> (uint256, bool):
```

### `hasPriceFeed`

Checks if an asset has a configured feed.

```vyper
@view
@external
def hasPriceFeed(_asset: address) -> bool:
```

### `getRedStoneData`

Raw oracle data retrieval with validation.

```vyper
@view
@external
def getRedStoneData(
    _feed: address,
    _decimals: uint256,
    _staleTime: uint256 = 0
) -> uint256:
```

#### Validation Checks

1. Price must be positive
2. Decimals must be ≤ 18
3. Timestamp cannot be in future
4. Round ID must be valid
5. Must be answered in current or later round
6. Price must not be stale

## Feed Management Functions

### Add New Feed

```vyper
@external
def addNewPriceFeed(
    _asset: address,
    _newFeed: address,
    _staleTime: uint256 = 0,
    _needsEthToUsd: bool = False,
) -> bool:

@external
def confirmNewPriceFeed(_asset: address) -> bool:

@external
def cancelNewPendingPriceFeed(_asset: address) -> bool:
```

### Update Feed

```vyper
@external
def updatePriceFeed(
    _asset: address,
    _newFeed: address,
    _staleTime: uint256 = 0,
    _needsEthToUsd: bool = False,
) -> bool:

@external
def confirmPriceFeedUpdate(_asset: address) -> bool:

@external
def cancelPriceFeedUpdate(_asset: address) -> bool:
```

### Disable Feed

```vyper
@external
def disablePriceFeed(_asset: address) -> bool:

@external
def confirmDisablePriceFeed(_asset: address) -> bool:

@external
def cancelDisablePriceFeed(_asset: address) -> bool:
```

All management functions require governance permission and respect the time lock.

## Key Mathematical Functions

### Decimal Normalization

```
if feedDecimals < 18:
    normalizedPrice = rawPrice × 10^(18 - feedDecimals)
```

### ETH to USD Conversion

```
if needsEthToUsd:
    finalPrice = ethDenominatedPrice × ethUsdPrice / 10^18
```

## Security Considerations

1. **Time Lock**: All feed changes require waiting period
2. **Governance Only**: Feed management restricted to governors
3. **Staleness Check**: Rejects prices older than configured threshold
4. **Round Validation**: Validates Chainlink round data integrity
5. **Future Timestamp Check**: Rejects timestamps in the future
6. **Decimal Overflow**: Only accepts feeds with ≤ 18 decimals
7. **Pause Mechanism**: Respects `isPaused` from PriceSourceData

## Testing

For comprehensive test examples, see: [`tests/pricing/test_redstone.py`](../../tests/pricing/test_redstone.py)
