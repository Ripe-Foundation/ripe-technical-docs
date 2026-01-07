# Deleverage Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/Deleverage.vy)

## Overview

Deleverage is the debt reduction engine of Ripe Protocol, enabling users to reduce their debt positions by liquidating their own collateral in a controlled, prioritized manner. Unlike liquidations which are triggered by external actors when positions become unhealthy, deleveraging is a proactive mechanism that allows users (or authorized callers) to unwind positions gracefully.

**Core Functions**:
- **Prioritized Asset Liquidation**: Processes collateral in a three-phase order (stability pool assets → priority assets → remaining vaults)
- **Batch Operations**: Deleverage multiple users or specific assets in single transactions
- **Collateral Swapping**: Swap collateral between vaults while maintaining debt health
- **Underscore Integration**: Special deleverage support for underscore leverage vaults
- **Volatile Asset Handling**: Dedicated path for volatile collateral that bypasses stability pool logic

Deleverage implements efficient gas optimization through transient storage for caching vault addresses and asset configurations. It works closely with [CreditEngine](./CreditEngine.md) for debt repayment, [AuctionHouse](./AuctionHouse.md) for collateral withdrawal, [Teller](./Teller.md) as the user entry point, and [EndaomentFunds](../treasury/EndaomentFunds.md) as the recipient for transferred assets.

## Architecture & Modules

Deleverage is built using a modular architecture with the following components:

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../core-modules/Addys.md)
- **Key Features**:
  - Access to all protocol contract addresses
  - Validation of caller permissions
  - Centralized address management
- **Exported Interface**: Address utilities via `addys.__interface__`

### DeptBasics Module

- **Location**: `contracts/modules/DeptBasics.vy`
- **Purpose**: Provides department-level functionality
- **Documentation**: See [DeptBasics Technical Documentation](../core-modules/DeptBasics.md)
- **Key Features**:
  - Pause mechanism for emergency stops
  - No Green minting capability
  - No Ripe minting capability
- **Exported Interface**: Department basics via `deptBasics.__interface__`

### Module Initialization

```vyper
initializes: addys
initializes: deptBasics[addys := addys]
```

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                        Deleverage Contract                              |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Three-Phase Deleverage                         |  |
|  |                                                                  |  |
|  |  PHASE 1: Stability Pool Assets                                   |  |
|  |     - GREEN and sGREEN in stability pools                        |  |
|  |     - Burns tokens to reduce debt directly                        |  |
|  |                                                                  |  |
|  |  PHASE 2: Priority Liquidation Assets                             |  |
|  |     - Assets configured for priority in MissionControl           |  |
|  |     - Transfers to EndaomentFunds or burns                        |  |
|  |                                                                  |  |
|  |  PHASE 3: All Other User Vaults                                   |  |
|  |     - Iterates through remaining user positions                   |  |
|  |     - Processes based on asset liquidation config                 |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Asset Handling Logic                           |  |
|  |                                                                  |  |
|  |  shouldBurnAsPayment = true:                                      |  |
|  |     → Burn GREEN/sGREEN directly (debt reduction)                |  |
|  |                                                                  |  |
|  |  shouldTransferToEndaoment = true:                                |  |
|  |     → Transfer to EndaomentFunds (protocol treasury)             |  |
|  |                                                                  |  |
|  |  PSM Yield Position Token:                                        |  |
|  |     → Transfer to EndaomentPSM (special handling)                |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| Teller           |    | CreditEngine      |    | AuctionHouse     |
| * Entry point    |    | * Debt repayment  |    | * Token withdraw |
| * User calls     |    | * Health checks   |    | * Vault access   |
+------------------+    +-------------------+    +------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| MissionControl   |    | EndaomentFunds    |    | PriceDesk        |
| * Asset configs  |    | * Asset custody   |    | * USD pricing    |
| * LTV params     |    | * Protocol vault  |    | * Conversions    |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### DeleverageUserRequest Struct

Request parameters for batch user deleverage:

```vyper
struct DeleverageUserRequest:
    user: address               # User to deleverage
    targetRepayAmount: uint256  # Target debt reduction
```

### DeleverageAsset Struct

Specific asset deleverage parameters:

```vyper
struct DeleverageAsset:
    vaultId: uint256            # Vault containing the asset
    asset: address              # Asset address to liquidate
    targetRepayAmount: uint256  # Target repay for this asset
```

### GenLiqConfig Struct

General liquidation configuration from MissionControl:

```vyper
struct GenLiqConfig:
    canLiquidate: bool                                        # Global liquidation toggle
    keeperFeeRatio: uint256                                   # Keeper reward percentage
    minKeeperFee: uint256                                     # Minimum keeper fee
    maxKeeperFee: uint256                                     # Maximum keeper fee
    ltvPaybackBuffer: uint256                                 # Buffer for LTV calculations
    genAuctionParams: cs.AuctionParams                        # Default auction params
    priorityLiqAssetVaults: DynArray[VaultData, 20]          # Priority liquidation vaults
    priorityStabVaults: DynArray[VaultData, 10]              # Priority stability vaults
```

### AssetLiqConfig Struct

Per-asset liquidation configuration:

```vyper
struct AssetLiqConfig:
    hasConfig: bool                       # Whether config exists
    shouldBurnAsPayment: bool             # Burn asset to reduce debt
    shouldTransferToEndaoment: bool       # Transfer to Endaoment
    shouldSwapInStabPools: bool           # Swap in stability pools
    shouldAuctionInstantly: bool          # Skip auction delay
    customAuctionParams: cs.AuctionParams # Asset-specific auction params
    specialStabPool: VaultData            # Special stability pool
```

### VaultData Struct

Vault reference information:

```vyper
struct VaultData:
    vaultId: uint256    # Registry vault ID
    vaultAddr: address  # Vault contract address
    asset: address      # Primary asset
```

### UserBorrowTerms Struct

Aggregated borrowing parameters:

```vyper
struct UserBorrowTerms:
    collateralVal: uint256      # Total USD collateral value
    totalMaxDebt: uint256       # Maximum borrowing power
    debtTerms: cs.DebtTerms     # Weighted average debt terms
    lowestLtv: uint256          # Lowest LTV across positions
    highestLtv: uint256         # Highest LTV across positions
```

### UserDebt Struct

Current debt state for a user:

```vyper
struct UserDebt:
    amount: uint256             # Total debt (principal + interest)
    principal: uint256          # Original borrowed amount
    debtTerms: cs.DebtTerms     # Current weighted debt terms
    lastTimestamp: uint256      # Last update timestamp
    inLiquidation: bool         # Liquidation status flag
```

## Events

### DeleverageUser

Emitted when a user is deleveraged:

```vyper
event DeleverageUser:
    user: indexed(address)      # User being deleveraged
    caller: indexed(address)    # Caller initiating deleverage
    targetRepayAmount: uint256  # Requested repay amount
    repaidAmount: uint256       # Actual amount repaid
    hasGoodDebtHealth: bool     # Health status after deleverage
```

### StabAssetBurntDuringDeleverage

Emitted when stability pool assets are burned:

```vyper
event StabAssetBurntDuringDeleverage:
    user: indexed(address)      # User being deleveraged
    vaultId: uint256            # Vault containing asset
    stabAsset: indexed(address) # GREEN or sGREEN burned
    amountBurned: uint256       # Amount burned
    usdValue: uint256           # USD value of burned amount
    isDepleted: bool            # Whether position fully depleted
```

### EndaomentTransferDuringDeleverage

Emitted when assets are transferred to Endaoment:

```vyper
event EndaomentTransferDuringDeleverage:
    user: indexed(address)      # User being deleveraged
    vaultId: uint256            # Vault containing asset
    asset: indexed(address)     # Asset transferred
    amountSent: uint256         # Amount transferred
    usdValue: uint256           # USD value transferred
    isDepleted: bool            # Whether position fully depleted
```

### CollateralSwapped

Emitted when collateral is swapped between vaults:

```vyper
event CollateralSwapped:
    user: indexed(address)      # User whose collateral swapped
    caller: indexed(address)    # Caller initiating swap
    withdrawVaultId: uint256    # Source vault ID
    withdrawAsset: indexed(address) # Asset withdrawn
    withdrawAmount: uint256     # Amount withdrawn
    depositVaultId: uint256     # Destination vault ID
    depositAsset: address       # Asset deposited
    depositAmount: uint256      # Amount deposited
    usdValue: uint256           # USD value of swap
```

### DeleverageUserWithVolatileAssets

Emitted when volatile assets are deleveraged:

```vyper
event DeleverageUserWithVolatileAssets:
    user: indexed(address)      # User being deleveraged
    repaidAmount: uint256       # Amount repaid
    hasGoodDebtHealth: bool     # Health status after
```

## State Variables

### Constants

- `UNDERSCORE_LEGOBOOK_ID: uint256 = 3` - Registry ID for underscore lego book
- `UNDERSCORE_VAULT_REGISTRY_ID: uint256 = 10` - Registry ID for underscore vault registry
- `HUNDRED_PERCENT: uint256 = 100_00` - 100.00% in basis points
- `ONE_PERCENT: uint256 = 1_00` - 1.00% in basis points
- `PRIORITY_LIQ_VAULT_DATA: uint256 = 20` - Max priority liquidation vaults
- `MAX_STAB_VAULT_DATA: uint256 = 10` - Max stability pool vaults
- `MAX_DELEVERAGE_USERS: uint256 = 25` - Max users per batch deleverage
- `MAX_DELEVERAGE_ASSETS: uint256 = 25` - Max assets per specific deleverage

### Transient Storage (Cache)

- `vaultAddrs: HashMap[uint256, address]` - Cached vault addresses
- `assetLiqConfig: HashMap[address, AssetLiqConfig]` - Cached asset configs
- `didHandleAsset: HashMap[address, HashMap[uint256, HashMap[address, bool]]]` - Processed asset tracking
- `didHandleVaultId: HashMap[address, HashMap[uint256, bool]]` - Processed vault tracking

### Inherited State Variables

From [DeptBasics](../core-modules/DeptBasics.md):

- `isPaused: bool` - Department pause state

## Constructor

### `__init__`

Initializes Deleverage contract without special minting permissions.

```vyper
@deploy
def __init__(_ripeHq: address):
```

#### Parameters

| Name      | Type      | Description             |
| --------- | --------- | ----------------------- |
| `_ripeHq` | `address` | RipeHq contract address |

#### Example Usage

```python
# Deploy Deleverage
deleverage = boa.load(
    "contracts/core/Deleverage.vy",
    ripe_hq.address
)
```

## Main Deleverage Functions

### `deleverageUser`

Deleverages a single user by liquidating their collateral to repay debt.

```vyper
@external
def deleverageUser(
    _user: address,
    _caller: address,
    _targetRepayAmount: uint256,
    _a: addys.Addys = empty(addys.Addys)
) -> uint256:
```

#### Parameters

| Name                 | Type          | Description                    |
| -------------------- | ------------- | ------------------------------ |
| `_user`              | `address`     | User to deleverage             |
| `_caller`            | `address`     | Original caller address        |
| `_targetRepayAmount` | `uint256`     | Target debt reduction (0=max)  |
| `_a`                 | `addys.Addys` | Cached addresses (optional)    |

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | Actual amount repaid |

#### Access

Only callable by Teller contract

#### Events Emitted

- `DeleverageUser` - Deleverage completion details
- `StabAssetBurntDuringDeleverage` - If stability assets burned
- `EndaomentTransferDuringDeleverage` - If assets transferred

#### Example Usage

```python
# Deleverage user through Teller
repaid = deleverage.deleverageUser(
    user.address,
    caller.address,
    1000e18,  # Target 1000 GREEN repayment
    sender=teller.address
)
```

### `deleverageManyUsers`

Batch deleverages multiple users in a single transaction.

```vyper
@external
def deleverageManyUsers(
    _users: DynArray[DeleverageUserRequest, MAX_DELEVERAGE_USERS],
    _caller: address,
    _a: addys.Addys = empty(addys.Addys)
) -> uint256:
```

#### Parameters

| Name      | Type                                    | Description                 |
| --------- | --------------------------------------- | --------------------------- |
| `_users`  | `DynArray[DeleverageUserRequest, 25]`   | Array of user requests      |
| `_caller` | `address`                               | Original caller address     |
| `_a`      | `addys.Addys`                           | Cached addresses (optional) |

#### Returns

| Type      | Description                |
| --------- | -------------------------- |
| `uint256` | Total amount repaid        |

#### Access

Only callable by Teller contract

#### Example Usage

```python
# Batch deleverage multiple users
requests = [
    DeleverageUserRequest(user1.address, 500e18),
    DeleverageUserRequest(user2.address, 1000e18),
]
total_repaid = deleverage.deleverageManyUsers(
    requests,
    caller.address,
    sender=teller.address
)
```

### `deleverageWithSpecificAssets`

Deleverages a user using specific assets in a specified order. Requires trusted caller or delegation.

```vyper
@external
def deleverageWithSpecificAssets(
    _user: address,
    _assets: DynArray[DeleverageAsset, MAX_DELEVERAGE_ASSETS],
    _caller: address,
    _a: addys.Addys = empty(addys.Addys)
) -> uint256:
```

#### Parameters

| Name      | Type                             | Description                   |
| --------- | -------------------------------- | ----------------------------- |
| `_user`   | `address`                        | User to deleverage            |
| `_assets` | `DynArray[DeleverageAsset, 25]`  | Ordered list of assets        |
| `_caller` | `address`                        | Original caller address       |
| `_a`      | `addys.Addys`                    | Cached addresses (optional)   |

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | Total amount repaid  |

#### Access

Only callable by Teller contract. Caller must be:
- The user themselves
- A valid Ripe address
- An underscore address
- Have borrow delegation from the user

#### Example Usage

```python
# Deleverage specific assets in order
assets = [
    DeleverageAsset(vault1_id, usdc.address, 500e18),
    DeleverageAsset(vault2_id, weth.address, 1000e18),
]
repaid = deleverage.deleverageWithSpecificAssets(
    user.address,
    assets,
    user.address,  # Self-deleverage
    sender=teller.address
)
```

## Special Deleverage Functions

### `deleverageWithVolAssets`

Deleverages volatile collateral assets only, skipping stability pool and endaoment transfer assets.

```vyper
@external
def deleverageWithVolAssets(
    _user: address,
    _assets: DynArray[DeleverageAsset, MAX_DELEVERAGE_ASSETS]
) -> uint256:
```

#### Parameters

| Name      | Type                             | Description             |
| --------- | -------------------------------- | ----------------------- |
| `_user`   | `address`                        | User to deleverage      |
| `_assets` | `DynArray[DeleverageAsset, 25]`  | Volatile assets to use  |

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | Total amount repaid  |

#### Access

Only callable by Switchboard or valid Ripe addresses

#### Events Emitted

- `DeleverageUserWithVolatileAssets` - Completion details

#### Example Usage

```python
# Deleverage volatile assets only
vol_assets = [
    DeleverageAsset(vault_id, weth.address, 500e18),
]
repaid = deleverage.deleverageWithVolAssets(
    user.address,
    vol_assets,
    sender=switchboard.address
)
```

### `swapCollateral`

Swaps collateral from one vault/asset to another while maintaining debt health. The deposit asset must have LTV >= withdraw asset LTV.

```vyper
@external
def swapCollateral(
    _user: address,
    _withdrawVaultId: uint256,
    _withdrawAsset: address,
    _depositVaultId: uint256,
    _depositAsset: address,
    _withdrawAmount: uint256 = max_value(uint256),
) -> (uint256, uint256):
```

#### Parameters

| Name               | Type      | Description                        |
| ------------------ | --------- | ---------------------------------- |
| `_user`            | `address` | User whose collateral to swap      |
| `_withdrawVaultId` | `uint256` | Source vault ID                    |
| `_withdrawAsset`   | `address` | Asset to withdraw                  |
| `_depositVaultId`  | `uint256` | Destination vault ID               |
| `_depositAsset`    | `address` | Asset to deposit                   |
| `_withdrawAmount`  | `uint256` | Amount to withdraw (max=all)       |

#### Returns

| Type      | Description         |
| --------- | ------------------- |
| `uint256` | Amount withdrawn    |
| `uint256` | Amount deposited    |

#### Access

Only callable by valid Ripe addresses or governance

#### Events Emitted

- `CollateralSwapped` - Swap details

#### Example Usage

```python
# Swap WETH collateral to USDC
withdrawn, deposited = deleverage.swapCollateral(
    user.address,
    vault1_id,      # WETH vault
    weth.address,
    vault2_id,      # USDC vault
    usdc.address,
    10e18,          # Swap 10 WETH worth
    sender=governance.address
)
```

### `deleverageForWithdrawal`

Special deleverage triggered by underscore vaults to maintain utilization ratio when users withdraw.

```vyper
@external
def deleverageForWithdrawal(
    _user: address,
    _vaultId: uint256,
    _asset: address,
    _amount: uint256
) -> bool:
```

#### Parameters

| Name       | Type      | Description                     |
| ---------- | --------- | ------------------------------- |
| `_user`    | `address` | User withdrawing                |
| `_vaultId` | `uint256` | Vault ID (0 to auto-detect)     |
| `_asset`   | `address` | Asset being withdrawn           |
| `_amount`  | `uint256` | Withdrawal amount               |

#### Returns

| Type   | Description                        |
| ------ | ---------------------------------- |
| `bool` | True if deleverage was successful  |

#### Access

Only callable by underscore addresses or valid Ripe addresses

#### Key Logic

Uses a weighted LTV formula to calculate required repayment:
```
requiredRepayment = (debt × lostCapacity) / (capacity - debt × effectiveLtv)
```

Applies a 1% buffer and caps at max deleveragable amount.

#### Example Usage

```python
# Deleverage to allow withdrawal
success = deleverage.deleverageForWithdrawal(
    user.address,
    vault_id,
    weth.address,
    5e18,  # Withdrawing 5 WETH
    sender=underscore_vault.address
)
```

## View Functions

### `getDeleverageInfo`

Returns the maximum deleveragable USD value and effective weighted LTV for a user.

```vyper
@view
@external
def getDeleverageInfo(_user: address) -> (uint256, uint256):
```

#### Parameters

| Name    | Type      | Description   |
| ------- | --------- | ------------- |
| `_user` | `address` | User to check |

#### Returns

| Type      | Description                    |
| --------- | ------------------------------ |
| `uint256` | Max deleveragable USD value    |
| `uint256` | Effective weighted LTV         |

#### Example Usage

```python
# Get deleverage info
max_deleverage, weighted_ltv = deleverage.getDeleverageInfo(user.address)
# Returns: (5000e18, 7500)  # $5000 deleveragable at 75% weighted LTV
```

### `getMaxDeleverageAmount`

Returns the maximum amount an untrusted caller can deleverage for a user.

```vyper
@view
@external
def getMaxDeleverageAmount(_user: address) -> uint256:
```

#### Parameters

| Name    | Type      | Description   |
| ------- | --------- | ------------- |
| `_user` | `address` | User to check |

#### Returns

| Type      | Description                  |
| --------- | ---------------------------- |
| `uint256` | Maximum repayable amount     |

#### Access

Public view function

#### Key Logic

Only returns non-zero if:
- User has debt
- User is not in liquidation
- User has collateral
- Collateral value is below redemption threshold

Applies LTV payback buffer to be conservative.

#### Example Usage

```python
# Get max deleverage amount for untrusted caller
max_amount = deleverage.getMaxDeleverageAmount(user.address)
# Returns: 1000e18 (can deleverage up to 1000 GREEN)
```

## Key Mathematical Functions

### Three-Phase Deleverage Algorithm

The contract processes assets in a specific priority order:

1. **Phase 1 - Stability Pool Assets**: Burns GREEN/sGREEN directly from stability pools
2. **Phase 2 - Priority Liquidation Assets**: Processes assets marked as priority in MissionControl
3. **Phase 3 - All User Vaults**: Iterates through remaining user positions

### Amount to Pay Calculation

For untrusted callers, the maximum repayable amount is calculated to bring the position back to a safe LTV:

```
collValueAdjusted = collateralValue × targetLtv / 100%

if debtAmount <= collValueAdjusted:
    return debtAmount  # Full repayment needed

debtToRepay = (debtAmount - collValueAdjusted) × 100% / (100% - targetLtv)
return min(debtToRepay, debtAmount)
```

### Deleverage Eligibility Check

```
redemptionThreshold = debtAmount × 100% / redemptionThresholdPercent
canDeleverage = collateralValue <= redemptionThreshold
```

### Withdrawal Deleverage Formula

For underscore vault withdrawals:
```
lostCapacity = withdrawUsdValue × assetLtv / 100%
numerator = debt × lostCapacity
denominator = totalMaxDebt - (debt × effectiveLtv / 100%)
requiredRepayment = numerator / denominator × 101%  # 1% buffer
```

## Security Considerations

1. **Access Control**: Main functions only callable by Teller; special functions by Switchboard/Ripe/governance
2. **Transient Storage**: Uses EIP-1153 transient storage for gas-efficient caching within transactions
3. **Delegation Checks**: Specific asset ordering requires trusted caller or borrow delegation
4. **LTV Validation**: Collateral swaps validate that deposit asset LTV >= withdraw asset LTV
5. **Reentrancy Protection**: External calls follow checks-effects-interactions pattern
6. **Buffer Application**: 1% buffer applied to withdrawal deleverage calculations
7. **Pause Mechanism**: All functions respect `isPaused` flag for emergency stops
8. **Cap Enforcement**: Maximum users (25) and assets (25) per batch to prevent gas exhaustion
