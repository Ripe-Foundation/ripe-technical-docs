# UndyVaultPrices Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/priceSources/UndyVaultPrices.vy)

## Overview

UndyVaultPrices is a price source for Underscore Protocol vault tokens in Ripe Protocol. It provides manipulation-resistant pricing for yield-bearing vault tokens using time-weighted average price per share calculations with configurable parameters.

**Core Features**:
- **Multi-Vault Support**: Can price multiple Underscore vault tokens
- **TWAP Mechanism**: Uses weighted average of price-per-share snapshots
- **Total Supply Weighting**: Weights snapshots by vault total supply
- **Manipulation Resistance**: Throttles upside movements and uses minimum of spot/TWAP
- **Dynamic Feed Management**: Add, update, and disable price feeds with time locks

## Architecture & Modules

UndyVaultPrices uses the standard price source architecture:

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

Configuration for each vault token's price feed:

```vyper
struct PriceConfig:
    underlyingAsset: address      # Underlying token of the vault
    underlyingDecimals: uint256   # Decimals of underlying
    vaultTokenDecimals: uint256   # Decimals of vault token
    minSnapshotDelay: uint256     # Min time between snapshots
    maxNumSnapshots: uint256      # Max snapshots for TWAP
    maxUpsideDeviation: uint256   # Max upside % per snapshot
    staleTime: uint256            # Snapshot expiry time
    lastSnapshot: PriceSnapshot   # Most recent snapshot
    nextIndex: uint256            # Circular buffer index
```

### PriceSnapshot

Individual observation with supply weighting:

```vyper
struct PriceSnapshot:
    totalSupply: uint256    # Vault total supply (normalized)
    pricePerShare: uint256  # Assets per share
    lastUpdate: uint256     # Block timestamp
```

### PendingPriceConfig

Pending configuration change:

```vyper
struct PendingPriceConfig:
    actionId: uint256    # Time lock action ID
    config: PriceConfig  # Proposed configuration
```

## Events

### NewPriceConfigPending / NewPriceConfigAdded / NewPriceConfigCancelled

Track new feed lifecycle.

### PriceConfigUpdatePending / PriceConfigUpdated / PriceConfigUpdateCancelled

Track feed update lifecycle.

### DisablePriceConfigPending / DisablePriceConfigConfirmed / DisablePriceConfigCancelled

Track feed removal lifecycle.

### PricePerShareSnapshotAdded

Emitted when a snapshot is recorded:

```vyper
event PricePerShareSnapshotAdded:
    asset: indexed(address)
    underlyingAsset: indexed(address)
    totalSupply: uint256
    pricePerShare: uint256
```

## State Variables

### Public Variables

- `priceConfigs: HashMap[address, PriceConfig]` - Vault token configurations
- `snapShots: HashMap[address, HashMap[uint256, PriceSnapshot]]` - Snapshots per vault
- `pendingPriceConfigs: HashMap[address, PendingPriceConfig]` - Pending changes

### Constants

- `HUNDRED_PERCENT: constant(uint256) = 100_00` - 100% in basis points
- `UNDERSCORE_VAULT_REGISTRY_ID: constant(uint256) = 10` - Registry ID for vault validation

## Constructor

### `__init__`

Initializes UndyVaultPrices.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _tempGov: address,
    _minPriceChangeTimeLock: uint256,
    _maxPriceChangeTimeLock: uint256,
):
```

#### Parameters

| Name                      | Type      | Description                           |
| ------------------------- | --------- | ------------------------------------- |
| `_ripeHq`                 | `address` | RipeHq contract address               |
| `_tempGov`                | `address` | Temporary governance address          |
| `_minPriceChangeTimeLock` | `uint256` | Minimum blocks for time-locked actions|
| `_maxPriceChangeTimeLock` | `uint256` | Maximum blocks for time-locked actions|

## Core Functions

### `getPrice`

Returns the vault token price.

```vyper
@view
@external
def getPrice(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> uint256:
```

#### Returns

| Type      | Description                                        |
| --------- | -------------------------------------------------- |
| `uint256` | Price in 18-decimal USD (0 if no feed configured)  |

#### Calculation

```
vaultPrice = underlyingPrice * min(weightedPricePerShare, currentPricePerShare) / 10^underlyingDecimals
```

### `getPriceAndHasFeed`

Returns price and feed status.

```vyper
@view
@external
def getPriceAndHasFeed(_asset: address, _staleTime: uint256 = 0, _priceDesk: address = empty(address)) -> (uint256, bool):
```

### `hasPriceFeed`

Checks if vault has configured price feed.

```vyper
@view
@external
def hasPriceFeed(_asset: address) -> bool:
```

### `hasPendingPriceFeedUpdate`

Checks for pending updates.

```vyper
@view
@external
def hasPendingPriceFeedUpdate(_asset: address) -> bool:
```

### `getWeightedPrice`

Returns TWAP price per share.

```vyper
@view
@external
def getWeightedPrice(_asset: address) -> uint256:
```

## Feed Management Functions

### `addNewPriceFeed`

Initiates adding a new vault price feed (time-locked).

```vyper
@external
def addNewPriceFeed(
    _asset: address,
    _minSnapshotDelay: uint256 = 60 * 5,  # 5 minutes
    _maxNumSnapshots: uint256 = 20,
    _maxUpsideDeviation: uint256 = 10_00, # 10%
    _staleTime: uint256 = 0,
) -> bool:
```

#### Access

Only callable by governance

#### Validation

- Asset must be a registered Underscore earn vault
- Underlying asset must have a price in PriceDesk
- Vault must implement `convertToAssetsSafe` with valid return
- Config parameters must be within bounds

### `confirmNewPriceFeed`

Confirms a pending new feed after time lock.

```vyper
@external
def confirmNewPriceFeed(_asset: address) -> bool:
```

### `cancelNewPendingPriceFeed`

Cancels a pending new feed.

```vyper
@external
def cancelNewPendingPriceFeed(_asset: address) -> bool:
```

### `updatePriceConfig`

Initiates config update for existing feed.

```vyper
@external
def updatePriceConfig(
    _asset: address,
    _minSnapshotDelay: uint256 = 60 * 5,
    _maxNumSnapshots: uint256 = 20,
    _maxUpsideDeviation: uint256 = 10_00,
    _staleTime: uint256 = 0,
) -> bool:
```

### `confirmPriceFeedUpdate` / `cancelPriceFeedUpdate`

Confirm or cancel pending config updates.

### `disablePriceFeed`

Initiates feed removal (time-locked).

```vyper
@external
def disablePriceFeed(_asset: address) -> bool:
```

### `confirmDisablePriceFeed` / `cancelDisablePriceFeed`

Confirm or cancel pending disable.

## Snapshot Functions

### `addPriceSnapshot`

Adds a new price per share snapshot.

```vyper
@external
def addPriceSnapshot(_asset: address) -> bool:
```

#### Access

Only callable by valid Ripe protocol addresses

#### Behavior

1. Returns false if no config for asset
2. Checks minimum delay since last snapshot
3. Gets current `convertToAssetsSafe` value
4. Throttles upside if exceeds max deviation
5. Stores snapshot with normalized total supply
6. Emits `PricePerShareSnapshotAdded` event

### `getLatestSnapshot`

Returns the most recent snapshot data.

```vyper
@view
@external
def getLatestSnapshot(_asset: address) -> PriceSnapshot:
```

## Price Calculation

### Weighted Price Per Share (TWAP)

```
1. For each valid (non-stale) snapshot:
   numerator += totalSupply * pricePerShare
   denominator += totalSupply
2. weightedPricePerShare = numerator / denominator
3. If no valid snapshots, use lastSnapshot.pricePerShare
```

Total supply weighting gives more influence to snapshots taken when vault had more deposits.

### Final Price

```
1. Get weighted price per share from TWAP
2. Get current price per share from vault
3. Use minimum (conservative approach)
4. Multiply by underlying asset USD price
5. Adjust for decimals
```

## Validation

### `isValidNewFeed`

Validates parameters for new feed.

```vyper
@view
@external
def isValidNewFeed(
    _asset: address,
    _minSnapshotDelay: uint256,
    _maxNumSnapshots: uint256,
    _maxUpsideDeviation: uint256,
    _staleTime: uint256,
) -> bool:
```

### `isValidUpdateConfig`

Validates parameters for config update.

```vyper
@view
@external
def isValidUpdateConfig(_asset: address, _maxNumSnapshots: uint256, _staleTime: uint256) -> bool:
```

### `isValidDisablePriceFeed`

Validates feed can be disabled.

```vyper
@view
@external
def isValidDisablePriceFeed(_asset: address) -> bool:
```

## Security Considerations

1. **Vault Validation**: Only accepts registered Underscore earn vaults
2. **Safe Price Function**: Uses `convertToAssetsSafe` which should handle edge cases
3. **TWAP Protection**: Historical average smooths manipulation attempts
4. **Supply Weighting**: Larger vault states have more influence
5. **Upside Throttling**: Limits rapid price increases
6. **Conservative Pricing**: Uses minimum of spot and TWAP
7. **Time-Locked Changes**: All feed changes require time lock
8. **Re-validation**: Validates again at confirmation time

## Integration Points

### Depends On:
- **Underscore Registry**: To validate vault registration
- **Underscore Vaults**: For `convertToAssetsSafe` function
- **PriceDesk**: For underlying asset prices
- **MissionControl**: For Underscore registry address

### Used By:
- **PriceDesk**: Registered as price source for vault tokens
