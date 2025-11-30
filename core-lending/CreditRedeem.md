# CreditRedeem Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/CreditRedeem.vy)

## Overview

CreditRedeem handles collateral redemption in Ripe Protocol, allowing GREEN token holders to claim collateral from users whose positions have fallen below the redemption threshold. This creates a market-based mechanism for maintaining system solvency without full liquidation.

**Core Functions**:
- **Collateral Redemption**: Burn GREEN to claim collateral from distressed positions
- **Batch Operations**: Process multiple redemptions in a single transaction
- **Position Protection**: Ensures redeemed positions maintain minimum health
- **Configurable Access**: Per-asset and per-user redemption permissions

Unlike [Deleverage](./Deleverage.md) where users reduce their own debt, CreditRedeem allows external parties to reduce another user's debt by burning GREEN and receiving their collateral. This provides an alternative to full liquidation for mildly distressed positions.

## Architecture & Modules

CreditRedeem is built using a modular architecture:

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Exported Interface**: Address utilities via `addys.__interface__`

### DeptBasics Module

- **Location**: `contracts/modules/DeptBasics.vy`
- **Purpose**: Provides department-level functionality
- **Documentation**: See [DeptBasics Technical Documentation](../shared-modules/DeptBasics.md)
- **Key Features**:
  - Pause mechanism for emergency stops
  - No GREEN minting capability (burns GREEN)
  - No RIPE minting capability
- **Exported Interface**: Department basics via `deptBasics.__interface__`

### Module Initialization

```vyper
initializes: addys
initializes: deptBasics[addys := addys]
```

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                        CreditRedeem Contract                            |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Redemption Flow                                |  |
|  |                                                                  |  |
|  |  1. Caller provides GREEN + redemption targets                    |  |
|  |  2. For each target:                                              |  |
|  |     a. Validate user is below redemption threshold               |  |
|  |     b. Calculate max redeemable (based on lowest LTV)            |  |
|  |     c. Withdraw/transfer collateral to caller                    |  |
|  |     d. Burn GREEN equivalent                                      |  |
|  |     e. Reduce user's debt                                         |  |
|  |  3. Refund unused GREEN to caller                                 |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Eligibility Criteria                           |  |
|  |                                                                  |  |
|  |  User must be below redemption threshold:                        |  |
|  |  collateralValue <= (debt × 100%) / redemptionThreshold          |  |
|  |                                                                  |  |
|  |  Example: 110% threshold, $100 debt                              |  |
|  |  → collateral must be ≤ $90.91 for redemption                    |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| Teller           |    | CreditEngine      |    | Ledger           |
| * Entry point    |    | * Debt repayment  |    | * Debt data      |
| * GREEN transfer |    | * Collateral xfer |    | * User vaults    |
+------------------+    +-------------------+    +------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| MissionControl   |    | PriceDesk         |    | GreenToken       |
| * Redemption cfg |    | * Asset pricing   |    | * Burn GREEN     |
| * LTV buffer     |    | * USD conversion  |    |                  |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### CollateralRedemption Struct

Individual redemption request parameters:

```vyper
struct CollateralRedemption:
    user: address           # User whose collateral to redeem
    vaultId: uint256        # Vault containing the collateral
    asset: address          # Asset to redeem
    maxGreenAmount: uint256 # Maximum GREEN to spend on this redemption
```

### RedeemCollateralConfig Struct

Configuration for redemption permissions:

```vyper
struct RedeemCollateralConfig:
    canRedeemCollateralGeneral: bool  # Global redemption toggle
    canRedeemCollateralAsset: bool    # Asset-specific redemption
    isUserAllowed: bool               # Recipient allowed to receive
    ltvPaybackBuffer: uint256         # Buffer for LTV calculations
    canAnyoneDeposit: bool            # Whether anyone can deposit for recipient
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

Current debt state:

```vyper
struct UserDebt:
    amount: uint256             # Total debt (principal + interest)
    principal: uint256          # Original borrowed amount
    debtTerms: cs.DebtTerms     # Current weighted debt terms
    lastTimestamp: uint256      # Last update timestamp
    inLiquidation: bool         # Liquidation status flag
```

### RepayDataBundle Struct

Bundled data for repayment:

```vyper
struct RepayDataBundle:
    userDebt: UserDebt          # User's debt state
    numUserVaults: uint256      # Number of user's vaults
```

## Events

### CollateralRedeemed

Emitted when collateral is successfully redeemed:

```vyper
event CollateralRedeemed:
    user: indexed(address)      # User whose collateral was redeemed
    vaultId: uint256            # Vault the collateral came from
    asset: indexed(address)     # Asset redeemed
    amount: uint256             # Amount of asset redeemed
    recipient: indexed(address) # Who received the collateral
    caller: address             # Who initiated the redemption
    repayValue: uint256         # GREEN burned / debt reduced
    hasGoodDebtHealth: bool     # Whether user has healthy position after
```

## State Variables

### Constants

- `HUNDRED_PERCENT: uint256 = 100_00` - 100.00% in basis points
- `MAX_COLLATERAL_REDEMPTIONS: uint256 = 20` - Maximum redemptions per batch
- `STABILITY_POOL_ID: uint256 = 1` - Stability pool vault ID
- `UNDERSCORE_VAULT_REGISTRY_ID: uint256 = 10` - Underscore vault registry ID

### Inherited State Variables

From [DeptBasics](../shared-modules/DeptBasics.md):

- `isPaused: bool` - Department pause state

## Constructor

### `__init__`

Initializes CreditRedeem without minting permissions.

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
# Deploy CreditRedeem
credit_redeem = boa.load(
    "contracts/core/CreditRedeem.vy",
    ripe_hq.address
)
```

## Redemption Functions

### `redeemCollateralFromMany`

Batch redeems collateral from multiple user positions by burning GREEN.

```vyper
@external
def redeemCollateralFromMany(
    _redemptions: DynArray[CollateralRedemption, MAX_COLLATERAL_REDEMPTIONS],
    _greenAmount: uint256,
    _recipient: address,
    _caller: address,
    _shouldTransferBalance: bool,
    _shouldRefundSavingsGreen: bool,
    _a: addys.Addys = empty(addys.Addys),
) -> uint256:
```

#### Parameters

| Name                        | Type                                  | Description                      |
| --------------------------- | ------------------------------------- | -------------------------------- |
| `_redemptions`              | `DynArray[CollateralRedemption, 20]`  | Array of redemption requests     |
| `_greenAmount`              | `uint256`                             | Total GREEN budget for redemptions|
| `_recipient`                | `address`                             | Collateral recipient             |
| `_caller`                   | `address`                             | Original transaction initiator   |
| `_shouldTransferBalance`    | `bool`                                | Transfer to vault vs withdraw    |
| `_shouldRefundSavingsGreen` | `bool`                                | Refund unused GREEN as sGREEN    |
| `_a`                        | `addys.Addys`                         | Cached addresses (optional)      |

#### Returns

| Type      | Description            |
| --------- | ---------------------- |
| `uint256` | Total GREEN spent      |

#### Access

Only callable by Teller contract

#### Events Emitted

- `CollateralRedeemed` - For each successful redemption

#### Example Usage

```python
# Redeem collateral from multiple users
redemptions = [
    CollateralRedemption(user1, vault1_id, weth, 500e18),
    CollateralRedemption(user2, vault1_id, usdc, 300e18),
]

# Through Teller
green_spent = credit_redeem.redeemCollateralFromMany(
    redemptions,
    1000e18,           # GREEN budget
    recipient.address,
    caller.address,
    False,             # Withdraw (not transfer)
    True,              # Refund as sGREEN
    sender=teller.address
)
```

#### Redemption Logic

For each redemption request:

1. **Validation Checks**:
   - Valid addresses and amounts
   - Recipient cannot be the user (prevents self-redemption abuse)
   - Vault exists and user has balance
   - User is not an underscore vault
   - Asset redemption is enabled in MissionControl
   - Recipient is allowed to receive

2. **Eligibility Check**:
   - User must be below redemption threshold
   - User must have debt and not be in liquidation

3. **Calculation**:
   - Target LTV = lowestLtv × (100% - ltvPaybackBuffer)
   - Max redeemable based on bringing position back to target LTV
   - Cap by available GREEN and asset-specific limit

4. **Execution**:
   - Withdraw/transfer collateral from user to recipient
   - Burn GREEN equivalent to repay value
   - Update user's debt via CreditEngine

5. **Cleanup**:
   - Refund unused GREEN to caller (optionally as sGREEN)

## View Functions

### `getMaxRedeemValue`

Returns the maximum GREEN value that can be redeemed from a user's position.

```vyper
@view
@external
def getMaxRedeemValue(_user: address) -> uint256:
```

#### Parameters

| Name    | Type      | Description            |
| ------- | --------- | ---------------------- |
| `_user` | `address` | User position to check |

#### Returns

| Type      | Description                      |
| --------- | -------------------------------- |
| `uint256` | Maximum GREEN redeemable (in USD)|

#### Access

Public view function

#### Example Usage

```python
# Check max redeemable from user
max_value = credit_redeem.getMaxRedeemValue(user.address)
# Returns: 500e18 (can redeem up to $500 worth)
```

#### Returns Zero When:
- User has no debt
- User is in liquidation
- User has no collateral
- User is above redemption threshold

## Key Mathematical Functions

### Redemption Eligibility Check

```
redemptionThreshold = debtAmount × 100% / redemptionThresholdPercent
canRedeem = collateralValue ≤ redemptionThreshold
```

Example with 110% threshold, $100 debt:
```
threshold = $100 × 100% / 110% = $90.91
If collateral = $85, can redeem (85 ≤ 90.91)
If collateral = $95, cannot redeem (95 > 90.91)
```

### Maximum Redemption Calculation

```
collValueAdjusted = collateralValue × targetLtv / 100%

if debtAmount ≤ collValueAdjusted:
    maxRedeem = debtAmount  # Full debt redemption

else:
    debtToRepay = (debtAmount - collValueAdjusted) × 100% / (100% - targetLtv)
    maxRedeem = min(debtToRepay, debtAmount)
```

### Target LTV with Buffer

```
targetLtv = lowestLtv × (100% - ltvPaybackBuffer) / 100%
```

Example with 80% lowest LTV and 5% buffer:
```
targetLtv = 80% × 95% / 100% = 76%
```

## Differences from Deleverage

| Aspect | CreditRedeem | Deleverage |
|--------|--------------|------------|
| **Who initiates** | External party (redeemer) | User or delegated caller |
| **Who receives collateral** | Redeemer | EndaomentFunds or burned |
| **Payment method** | Burn GREEN | Burn user's collateral |
| **Threshold** | Redemption threshold | Redemption threshold |
| **Permission** | Asset must allow redemption | User must allow deleverage |
| **Purpose** | Allow GREEN holders to claim collateral | Help users reduce debt |

## Security Considerations

1. **Self-Redemption Prevention**: Recipient cannot be the user being redeemed
2. **Underscore Protection**: Cannot redeem from underscore vaults
3. **Graceful Failures**: Batch redemptions fail gracefully for individual items
4. **Access Control**: Only Teller can call redemption function
5. **Pause Mechanism**: Respects `isPaused` flag
6. **LTV Buffer**: Conservative buffer ensures positions remain healthy
7. **Per-Asset Config**: Each asset can enable/disable redemptions independently
8. **Allowlist Support**: Recipients can be restricted via MissionControl

## Integration with CreditEngine

CreditRedeem relies on CreditEngine for:
- `getUserBorrowTermsWithNumVaults()` - Get user's borrowing terms
- `getLatestUserDebtWithInterest()` - Get current debt with interest
- `transferOrWithdrawViaRedemption()` - Move collateral to recipient
- `repayFromDept()` - Reduce user's debt
