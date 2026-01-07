# Teller Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/Teller.vy)

## Overview

Teller is the primary gateway to the Ripe Protocol, serving as a unified interface for all user operations. Like a comprehensive banking teller, it orchestrates complex multi-contract operations while providing user-friendly
interfaces and robust permission management.

**Unified Operations**:
- **Asset Management**: Deposits, withdrawals with automatic vault selection, configurable limits, and batch operations
- **Credit Services**: Borrowing against collateral and debt repayment with support for both Green and Savings Green tokens
- **Market Participation**: Liquidations, auction purchases, stability pool interactions, and collateral redemption
- **Rewards & Governance**: Loot claiming, Ripe bond purchases, and governance vault management
- **Delegation System**: Comprehensive permissions allowing authorized proxy operations with Underscore wallet integration

The contract abstracts protocol complexity through automatic vault selection, batch processing for gas efficiency, flexible payment handling, sophisticated permission hierarchies, and comprehensive event logging while maintaining security through thoughtful validation layers. It interfaces with [CreditEngine](CreditEngine.md) for borrowing operations, [VaultBook](../registries/VaultBook.md) for vault validation, and [Lootbox](../treasury-rewards/Lootbox.md) for rewards coordination.

## Architecture & Modules

Teller is built using a modular architecture with the following components:

### Addys Module
- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Key Features**:
  - Access to all protocol contract addresses
  - Validation of caller permissions
  - Centralized address management
- **Exported Interface**: Address utilities via `addys.__interface__`

### DeptBasics Module
- **Location**: `contracts/modules/DeptBasics.vy`
- **Purpose**: Provides department-level functionality
- **Documentation**: See [DeptBasics Technical Documentation](../shared-modules/DeptBasics.md)
- **Key Features**:
  - Pause mechanism for emergency stops
  - No minting capabilities (Teller is interface only)
- **Exported Interface**: Department basics via `deptBasics.__interface__`

### Module Initialization
```vyper
initializes: addys
initializes: deptBasics[addys := addys]
```

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                         Teller Contract                                |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    User Interface Layer                          |  |
|  |                                                                  |  |
|  |  Single Entry Point for All User Operations:                    |  |
|  |  - Deposits & Withdrawals                                        |  |
|  |  - Borrowing & Repayment                                         |  |
|  |  - Liquidations & Auctions                                       |  |
|  |  - Stability Pool Operations                                     |  |
|  |  - Reward Claims & Bond Purchases                                |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                   Permission & Validation                        |  |
|  |                                                                  |  |
|  |  Access Controls:                                                |  |
|  |  - User ownership verification                                   |  |
|  |  - Delegation system support                                     |  |
|  |  - Underscore wallet integration                                 |  |
|  |  - Operation-specific permissions                                |  |
|  |                                                                  |  |
|  |  Validation Logic:                                               |  |
|  |  - Deposit limits (per-user, global)                            |  |
|  |  - Asset compatibility checks                                    |  |
|  |  - Vault capacity validation                                     |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                      Operation Routing                          |  |
|  |                                                                  |  |
|  |  Smart Contract Orchestration:                                   |  |
|  |  - Automatic vault selection                                     |  |
|  |  - Multi-contract operation coordination                         |  |
|  |  - Batch processing optimization                                 |  |
|  |  - Event emission & logging                                      |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| Vault System     |    | CreditEngine      |    | AuctionHouse     |
| * Asset storage  |    | * Borrowing       |    | * Liquidations   |
| * User deposits  |    | * Debt management |    | * Auctions       |
| * Yield tracking |    | * Collateral calc |    | * Price discover |
+------------------+    +-------------------+    +------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| StabVault        |    | Lootbox           |    | BondRoom         |
| * Stability pool |    | * Reward claims   |    | * Bond sales     |
| * Green claims   |    | * Points tracking |    | * Ripe purchase  |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### TellerDepositConfig Struct
Deposit validation configuration:
```vyper
struct TellerDepositConfig:
    canDepositGeneral: bool          # Global deposits enabled
    canDepositAsset: bool            # Asset deposits enabled
    doesVaultSupportAsset: bool      # Vault-asset compatibility
    isUserAllowed: bool              # User whitelist check
    perUserDepositLimit: uint256     # Per-user deposit cap
    globalDepositLimit: uint256      # Protocol-wide cap
    perUserMaxAssetsPerVault: uint256  # Asset diversity limit
    perUserMaxVaults: uint256        # Vault count limit
    canAnyoneDeposit: bool           # Allow proxy deposits
    minDepositBalance: uint256       # Minimum position size
```

### TellerWithdrawConfig Struct
Withdrawal validation configuration:
```vyper
struct TellerWithdrawConfig:
    canWithdrawGeneral: bool         # Global withdrawals enabled
    canWithdrawAsset: bool           # Asset withdrawals enabled
    isUserAllowed: bool              # User whitelist check
    canWithdrawForUser: bool         # Allow proxy withdrawals
    minDepositBalance: uint256       # Minimum remaining balance
```

### DepositAction Struct
Batch deposit specification:
```vyper
struct DepositAction:
    asset: address                   # Asset to deposit
    amount: uint256                  # Amount to deposit
    vaultAddr: address               # Target vault address
    vaultId: uint256                 # Target vault ID
```

### WithdrawalAction Struct
Batch withdrawal specification:
```vyper
struct WithdrawalAction:
    asset: address                   # Asset to withdraw
    amount: uint256                  # Amount to withdraw
    vaultAddr: address               # Source vault address
    vaultId: uint256                 # Source vault ID
```

## State Variables

### Constants
- `MAX_BALANCE_ACTION: uint256 = 20` - Batch operation limit
- `MAX_CLAIM_USERS: uint256 = 25` - Batch claim limit
- `MAX_COLLATERAL_REDEMPTIONS: uint256 = 20` - Redemption batch limit
- `MAX_AUCTION_PURCHASES: uint256 = 20` - Auction batch limit
- `MAX_LIQ_USERS: uint256 = 50` - Liquidation batch limit
- `MAX_STAB_CLAIMS: uint256 = 15` - Stability pool claim limit
- `MAX_STAB_REDEMPTIONS: uint256 = 15` - Stability pool redemption limit
- `MAX_DELEVERAGE_USERS: uint256 = 25` - Deleverage batch limit
- `MAX_DELEVERAGE_ASSETS: uint256 = 25` - Assets per deleverage limit
- `STABILITY_POOL_ID: uint256 = 1` - Stability pool vault ID
- `RIPE_GOV_VAULT_ID: uint256 = 2` - Governance vault ID
- `CURVE_PRICES_ID: uint256 = 2` - Curve prices registry ID

### Inherited State Variables
From [DeptBasics](../shared-modules/DeptBasics.md):
- `isPaused: bool` - Department pause state

## Constructor

### `__init__`

Initializes Teller as the protocol's user interface layer.

```vyper
@deploy
def __init__(_ripeHq: address, _shouldPause: bool):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_ripeHq` | `address` | RipeHq contract address |
| `_shouldPause` | `bool` | Whether to start paused |

#### Returns

*Constructor does not return any values*

#### Access

Called only during deployment

#### Example Usage
```python
# Deploy Teller
teller = boa.load(
    "contracts/core/Teller.vy",
    ripe_hq.address,
    False  # Don't start paused
)
```

**Example Output**: Contract deployed as protocol interface layer

## Deposit Functions

### `deposit`

Deposits assets into vaults with automatic vault selection.

```vyper
@nonreentrant
@external
def deposit(
    _asset: address,
    _amount: uint256 = max_value(uint256),
    _user: address = msg.sender,
    _vaultAddr: address = empty(address),
    _vaultId: uint256 = 0,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to deposit |
| `_amount` | `uint256` | Amount to deposit (max for all balance) |
| `_user` | `address` | Recipient user (defaults to caller) |
| `_vaultAddr` | `address` | Specific vault address (optional) |
| `_vaultId` | `uint256` | Specific vault ID (optional) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Actual amount deposited |

#### Access

Public function with permission checks

#### Events Emitted

- `TellerDeposit` - Complete deposit details including user, depositor, asset, amount, and vault info

#### Example Usage
```python
# Simple deposit - auto-selects vault
amount_deposited = teller.deposit(
    usdc.address,
    1000_000000  # 1000 USDC
)

# Deposit for another user (if permitted)
amount_deposited = teller.deposit(
    weth.address,
    5_000000000000000000,  # 5 ETH
    recipient.address,
    vault_addr,
    vault_id
)
```

**Example Output**: Validates permissions, transfers tokens, updates vault balances

### `depositMany`

Batch deposits multiple assets/amounts in single transaction.

```vyper
@nonreentrant
@external
def depositMany(_user: address, _deposits: DynArray[DepositAction, MAX_BALANCE_ACTION]) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | Recipient user |
| `_deposits` | `DynArray[DepositAction, 20]` | Deposit specifications |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Number of deposits executed |

#### Access

Public function with permission checks

#### Example Usage
```python
# Batch deposit multiple assets
deposits = [
    DepositAction(usdc.address, 1000_000000, vault1, 0),
    DepositAction(weth.address, 5e18, vault2, 0),
    DepositAction(wbtc.address, 2e8, vault3, 0)
]
count = teller.depositMany(user.address, deposits)
```

### `depositFromTrusted`

Internal deposit function for protocol contracts.

```vyper
@external
def depositFromTrusted(
    _user: address,
    _vaultId: uint256,
    _asset: address,
    _amount: uint256,
    _lockDuration: uint256,
    _a: addys.Addys = empty(addys.Addys),
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User receiving deposit |
| `_vaultId` | `uint256` | Target vault ID |
| `_asset` | `address` | Asset to deposit |
| `_amount` | `uint256` | Amount to deposit |
| `_lockDuration` | `uint256` | Lock duration (for governance vault) |
| `_a` | `addys.Addys` | Cached addresses (optional) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount deposited |

#### Access

Only callable by valid Ripe addresses

## Withdrawal Functions

### `withdraw`

Withdraws assets from vaults with health checks.

```vyper
@nonreentrant
@external
def withdraw(
    _asset: address,
    _amount: uint256 = max_value(uint256),
    _user: address = msg.sender,
    _vaultAddr: address = empty(address),
    _vaultId: uint256 = 0,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to withdraw |
| `_amount` | `uint256` | Amount to withdraw (max for all) |
| `_user` | `address` | User to withdraw from |
| `_vaultAddr` | `address` | Specific vault address (optional) |
| `_vaultId` | `uint256` | Specific vault ID (optional) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Actual amount withdrawn |

#### Access

Public function with permission checks

#### Events Emitted

- `TellerWithdrawal` - Complete withdrawal details including depletion status

#### Example Usage
```python
# Withdraw USDC
amount_withdrawn = teller.withdraw(
    usdc.address,
    500_000000  # 500 USDC
)

# Withdraw all of an asset
amount_withdrawn = teller.withdraw(
    weth.address,
    sender=user.address
)
```

### `withdrawMany`

Batch withdrawals in single transaction.

```vyper
@nonreentrant
@external
def withdrawMany(_user: address, _withdrawals: DynArray[WithdrawalAction, MAX_BALANCE_ACTION]) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User to withdraw from |
| `_withdrawals` | `DynArray[WithdrawalAction, 20]` | Withdrawal specifications |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Number of withdrawals executed |

#### Access

Public function with permission checks

## Rebalance Functions

### `rebalance`

Swaps collateral by depositing one asset and withdrawing another while maintaining debt health.

```vyper
@external
def rebalance(
    _depositAsset: address,
    _depositVaultId: uint256,
    _withdrawAsset: address,
    _withdrawVaultId: uint256,
    _depositAmount: uint256 = max_value(uint256),
    _withdrawAmount: uint256 = max_value(uint256),
    _user: address = msg.sender,
) -> (uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_depositAsset` | `address` | Asset to deposit |
| `_depositVaultId` | `uint256` | Vault ID to deposit into |
| `_withdrawAsset` | `address` | Asset to withdraw |
| `_withdrawVaultId` | `uint256` | Vault ID to withdraw from |
| `_depositAmount` | `uint256` | Amount to deposit (max for all) |
| `_withdrawAmount` | `uint256` | Amount to withdraw (max for all) |
| `_user` | `address` | User to rebalance for |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256)` | (withdrawnAmount, depositedAmount) |

#### Access

Public function with permission checks

#### Events Emitted

- `TellerRebalance` - Rebalance details including both deposit and withdrawal info

#### Example Usage
```python
# Rebalance from WETH to USDC
withdrawn, deposited = teller.rebalance(
    usdc.address,     # Deposit USDC
    1,                # Into vault 1
    weth.address,     # Withdraw WETH
    1,                # From vault 1
    1000e6,           # Deposit 1000 USDC
    1e18,             # Withdraw 1 WETH
    user.address
)
```

## Credit Functions

### `borrow`

Borrows Green tokens against collateral.

```vyper
@nonreentrant
@external
def borrow(
    _greenAmount: uint256 = max_value(uint256),
    _user: address = msg.sender,
    _wantsSavingsGreen: bool = True,
    _shouldEnterStabPool: bool = False,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_greenAmount` | `uint256` | Amount to borrow (max = maximum borrowable) |
| `_user` | `address` | User to borrow for (default: caller) |
| `_wantsSavingsGreen` | `bool` | Receive as sGreen (default: True) |
| `_shouldEnterStabPool` | `bool` | Auto-deposit to stability pool |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount borrowed after fees |

#### Access

Public function with permission checks

#### Example Usage
```python
# Borrow max Green tokens as sGreen (defaults)
amount_borrowed = teller.borrow()

# Borrow specific amount
amount_borrowed = teller.borrow(
    1000e18,       # 1000 Green
    user.address,
    True,          # Want sGreen
    False          # Don't enter stability pool
)
```

### `repay`

Repays debt using Green or Savings Green tokens.

```vyper
@nonreentrant
@external
def repay(
    _paymentAmount: uint256 = max_value(uint256),
    _user: address = msg.sender,
    _isPaymentSavingsGreen: bool = False,
    _shouldRefundSavingsGreen: bool = True,
) -> bool:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_paymentAmount` | `uint256` | Amount to repay (max = full debt) |
| `_user` | `address` | User whose debt to repay (default: caller) |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGreen |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGreen (default: True) |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if debt health restored |

#### Access

Public function with permission checks

## Liquidation Functions

### `liquidateUser`

Liquidates a single unhealthy position. The caller (msg.sender) acts as the keeper and receives the liquidation rewards.

```vyper
@nonreentrant
@external
def liquidateUser(
    _liqUser: address,
    _wantsSavingsGreen: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_liqUser` | `address` | User to liquidate |
| `_wantsSavingsGreen` | `bool` | Receive rewards as sGreen (default: True) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Keeper rewards received |

#### Access

Public function

#### Example Usage
```python
# Liquidate unhealthy position (caller is keeper)
keeper_rewards = teller.liquidateUser(
    underwater_user.address,
    True  # Want sGreen rewards
)

# Liquidate with default sGreen rewards
keeper_rewards = teller.liquidateUser(underwater_user.address)
```

### `liquidateManyUsers`

Batch liquidates multiple positions. The caller (msg.sender) acts as the keeper and receives the liquidation rewards.

```vyper
@nonreentrant
@external
def liquidateManyUsers(
    _liqUsers: DynArray[address, MAX_LIQ_USERS],
    _wantsSavingsGreen: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_liqUsers` | `DynArray[address, 50]` | Users to liquidate |
| `_wantsSavingsGreen` | `bool` | Receive rewards as sGreen (default: True) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total keeper rewards |

#### Access

Public function

## Auction Functions

### `buyFungibleAuction`

Purchases collateral from liquidation auction.

```vyper
@nonreentrant
@external
def buyFungibleAuction(
    _liqUser: address,
    _vaultId: uint256,
    _asset: address,
    _paymentAmount: uint256 = max_value(uint256),
    _isPaymentSavingsGreen: bool = False,
    _shouldTransferBalance: bool = False,
    _shouldRefundSavingsGreen: bool = True,
    _recipient: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_liqUser` | `address` | User being liquidated |
| `_vaultId` | `uint256` | Vault containing asset |
| `_asset` | `address` | Asset to purchase |
| `_paymentAmount` | `uint256` | Max Green/sGreen to spend (default: max available) |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGreen (default: False) |
| `_shouldTransferBalance` | `bool` | Transfer balance vs withdraw to recipient (default: False) |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGreen (default: True) |
| `_recipient` | `address` | Collateral recipient (default: msg.sender) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Green spent on purchase |

#### Access

Public function

### `buyManyFungibleAuctions`

Batch purchases from multiple auctions.

```vyper
@nonreentrant
@external
def buyManyFungibleAuctions(
    _purchases: DynArray[FungAuctionPurchase, MAX_AUCTION_PURCHASES],
    _paymentAmount: uint256 = max_value(uint256),
    _isPaymentSavingsGreen: bool = False,
    _shouldTransferBalance: bool = False,
    _shouldRefundSavingsGreen: bool = True,
    _recipient: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_purchases` | `DynArray[FungAuctionPurchase, 20]` | Auction purchase specs |
| `_paymentAmount` | `uint256` | Total Green/sGreen budget (default: max available) |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGreen (default: False) |
| `_shouldTransferBalance` | `bool` | Transfer balance vs withdraw to recipient (default: False) |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGreen (default: True) |
| `_recipient` | `address` | Collateral recipient (default: msg.sender) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total Green spent |

#### Access

Public function

## Stability Pool Functions

### `convertToSavingsGreenAndDepositIntoStabPool`

Converts Green tokens to Savings Green and deposits into the stability pool.

```vyper
@nonreentrant
@external
def convertToSavingsGreenAndDepositIntoStabPool(
    _user: address,
    _greenAmount: uint256,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User to deposit for |
| `_greenAmount` | `uint256` | Amount of Green to convert and deposit |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount of Savings Green deposited |

#### Access

Public function with permission checks

#### Example Usage
```python
# Convert 1000 Green to sGreen and deposit into stability pool
amount_deposited = teller.convertToSavingsGreenAndDepositIntoStabPool(
    user.address,
    1000_000000000000000000  # 1000 Green
)
```

### `claimFromStabilityPool`

Claims rewards from a single stability pool position.

```vyper
@nonreentrant
@external
def claimFromStabilityPool(
    _vaultId: uint256,
    _stabAsset: address,
    _claimAsset: address,
    _maxUsdValue: uint256 = max_value(uint256),
    _user: address = msg.sender,
    _shouldAutoDeposit: bool = False,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_vaultId` | `uint256` | Stability pool vault ID |
| `_stabAsset` | `address` | Stability asset (GREEN/sGREEN) |
| `_claimAsset` | `address` | Asset to claim |
| `_maxUsdValue` | `uint256` | Maximum USD value to claim |
| `_user` | `address` | User claiming rewards |
| `_shouldAutoDeposit` | `bool` | Auto-deposit claimed assets |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | USD value of assets claimed |

#### Access

Public function with permission checks

#### Example Usage
```python
# Claim stability pool rewards
claim_value = teller.claimFromStabilityPool(
    1,                # Vault ID
    sgreen.address,   # Stability asset
    weth.address,     # Claim WETH
    1000e18,          # Max $1000
    user.address,
    False             # Don't auto-deposit
)
```

### `claimManyFromStabilityPool`

Batch claims rewards from a stability pool position.

```vyper
@nonreentrant
@external
def claimManyFromStabilityPool(
    _vaultId: uint256,
    _claims: DynArray[StabPoolClaim, MAX_STAB_CLAIMS],
    _user: address = msg.sender,
    _shouldAutoDeposit: bool = False,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_vaultId` | `uint256` | Stability pool vault ID |
| `_claims` | `DynArray[StabPoolClaim, 15]` | List of claim specifications |
| `_user` | `address` | User claiming rewards |
| `_shouldAutoDeposit` | `bool` | Auto-deposit claimed assets |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total USD value of assets claimed |

#### Access

Public function with permission checks

#### Example Usage
```python
# Claim multiple assets from stability pool
claims = [
    StabPoolClaim(sgreen.address, weth.address, 500e18),
    StabPoolClaim(sgreen.address, usdc.address, 500e18),
]
total_value = teller.claimManyFromStabilityPool(
    1,          # Vault ID
    claims,
    user.address,
    False       # Don't auto-deposit
)
```

### `redeemFromStabilityPool`

Redeems collateral from liquidations using GREEN tokens.

```vyper
@nonreentrant
@external
def redeemFromStabilityPool(
    _vaultId: uint256,
    _claimAsset: address,
    _paymentAmount: uint256 = max_value(uint256),
    _recipient: address = msg.sender,
    _shouldAutoDeposit: bool = False,
    _isPaymentSavingsGreen: bool = False,
    _shouldRefundSavingsGreen: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_vaultId` | `uint256` | Stability pool vault ID |
| `_claimAsset` | `address` | Collateral asset to redeem |
| `_paymentAmount` | `uint256` | GREEN payment amount |
| `_recipient` | `address` | Collateral recipient |
| `_shouldAutoDeposit` | `bool` | Auto-deposit collateral |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGREEN |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGREEN |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | GREEN spent on redemption |

#### Access

Public function with permission checks

#### Example Usage
```python
# Redeem collateral from stability pool
green_spent = teller.redeemFromStabilityPool(
    1,                # Vault ID
    weth.address,     # Claim WETH
    500e18,           # 500 GREEN budget
    user.address,     # Recipient
    False,            # Don't auto-deposit
    False,            # Pay with GREEN
    True              # Refund as sGREEN
)
```

### `redeemManyFromStabilityPool`

Batch redeems collateral from stability pools.

```vyper
@nonreentrant
@external
def redeemManyFromStabilityPool(
    _vaultId: uint256,
    _redemptions: DynArray[StabPoolRedemption, MAX_STAB_REDEMPTIONS],
    _paymentAmount: uint256 = max_value(uint256),
    _recipient: address = msg.sender,
    _shouldAutoDeposit: bool = False,
    _isPaymentSavingsGreen: bool = False,
    _shouldRefundSavingsGreen: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_vaultId` | `uint256` | Stability pool vault ID |
| `_redemptions` | `DynArray[StabPoolRedemption, 15]` | Redemption specs |
| `_paymentAmount` | `uint256` | GREEN payment amount |
| `_recipient` | `address` | Collateral recipient |
| `_shouldAutoDeposit` | `bool` | Auto-deposit collateral |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGREEN |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGREEN |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total GREEN spent on redemptions |

#### Access

Public function with permission checks

## Collateral Redemption Functions

### `redeemCollateral`

Redeems collateral from unhealthy positions using Green tokens.

```vyper
@nonreentrant
@external
def redeemCollateral(
    _user: address,
    _vaultId: uint256,
    _asset: address,
    _paymentAmount: uint256 = max_value(uint256),
    _isPaymentSavingsGreen: bool = False,
    _shouldTransferBalance: bool = False,
    _shouldRefundSavingsGreen: bool = True,
    _recipient: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User with unhealthy position to redeem from |
| `_vaultId` | `uint256` | Vault containing collateral |
| `_asset` | `address` | Collateral asset to redeem |
| `_paymentAmount` | `uint256` | Max Green/sGreen to spend (default: max available) |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGreen (default: False) |
| `_shouldTransferBalance` | `bool` | Transfer balance vs withdraw to recipient (default: False) |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGreen (default: True) |
| `_recipient` | `address` | Collateral recipient (default: msg.sender) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Green amount used for redemption |

#### Access

Public function

#### Example Usage
```python
# Redeem ETH from unhealthy position
green_spent = teller.redeemCollateral(
    unhealthy_user.address,
    1,  # Vault ID
    weth.address,
    500_000000000000000000,  # 500 Green budget
    False,  # Paying with Green
    False,  # Withdraw collateral
    True,   # Refund excess as sGreen
    redeemer.address
)
```

### `redeemCollateralFromMany`

Batch redeems collateral from multiple unhealthy positions.

```vyper
@nonreentrant
@external
def redeemCollateralFromMany(
    _redemptions: DynArray[CollateralRedemption, MAX_COLLATERAL_REDEMPTIONS],
    _paymentAmount: uint256 = max_value(uint256),
    _isPaymentSavingsGreen: bool = False,
    _shouldTransferBalance: bool = False,
    _shouldRefundSavingsGreen: bool = True,
    _recipient: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_redemptions` | `DynArray[CollateralRedemption, 20]` | Redemption specifications |
| `_paymentAmount` | `uint256` | Total Green/sGreen budget (default: max available) |
| `_isPaymentSavingsGreen` | `bool` | Paying with sGreen (default: False) |
| `_shouldTransferBalance` | `bool` | Transfer balance vs withdraw to recipient (default: False) |
| `_shouldRefundSavingsGreen` | `bool` | Refund excess as sGreen (default: True) |
| `_recipient` | `address` | Collateral recipient (default: msg.sender) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total Green spent |

#### Access

Public function

#### Example Usage
```python
# Redeem from multiple positions
redemptions = [
    CollateralRedemption(user1.address, 1, weth.address, 100e18),
    CollateralRedemption(user2.address, 1, wbtc.address, 50e18)
]
total_spent = teller.redeemCollateralFromMany(
    redemptions,
    1000_000000000000000000,  # 1000 Green budget
    True,   # Paying with sGreen
    False,  # Withdraw
    True,   # Refund as sGreen
    redeemer.address
)
```

## Deleverage Functions

The deleverage functions allow users to reduce their debt by liquidating their own collateral. See [Deleverage](./Deleverage.md) for detailed documentation.

### `deleverageUser`

Deleverages a single user's position.

```vyper
@external
def deleverageUser(
    _user: address = msg.sender,
    _targetRepayAmount: uint256 = max_value(uint256)
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User to deleverage |
| `_targetRepayAmount` | `uint256` | Target debt reduction (max for all available) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Actual amount repaid |

#### Access

Public function

#### Example Usage
```python
# Deleverage own position
repaid = teller.deleverageUser(user.address, 500e18)
```

### `deleverageManyUsers`

Batch deleverages multiple users.

```vyper
@external
def deleverageManyUsers(
    _users: DynArray[DeleverageUserRequest, MAX_DELEVERAGE_USERS]
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_users` | `DynArray[DeleverageUserRequest, 25]` | Users and target amounts |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total amount repaid |

### `deleverageWithSpecificAssets`

Deleverages using specific assets in a specified order. Requires trusted caller or delegation.

```vyper
@external
def deleverageWithSpecificAssets(
    _assets: DynArray[DeleverageAsset, MAX_DELEVERAGE_ASSETS],
    _user: address = msg.sender
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_assets` | `DynArray[DeleverageAsset, 25]` | Ordered list of assets to use |
| `_user` | `address` | User to deleverage |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total amount repaid |

#### Access

Public function - requires user to be caller or have delegation

## Permission Management Functions

### `setUserConfig`

Sets user's general permission configuration.

```vyper
@external
def setUserConfig(
    _user: address,
    _canAnyoneDeposit: bool,
    _canAnyoneRepayDebt: bool,
    _canAnyoneBondForUser: bool,
):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User to configure |
| `_canAnyoneDeposit` | `bool` | Allow proxy deposits |
| `_canAnyoneRepayDebt` | `bool` | Allow proxy debt repayment |
| `_canAnyoneBondForUser` | `bool` | Allow proxy bond purchases |

#### Access

Only callable by user or authorized delegates

#### Events Emitted

- `UserConfigSet` - New configuration details

### `setUserDelegation`

Sets operation-specific delegation permissions.

```vyper
@external
def setUserDelegation(
    _user: address,
    _delegate: address,
    _canWithdraw: bool,
    _canBorrow: bool,
    _canClaimFromStabPool: bool,
    _canClaimLoot: bool,
):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User granting permissions |
| `_delegate` | `address` | Delegate receiving permissions |
| `_canWithdraw` | `bool` | Allow withdrawal operations |
| `_canBorrow` | `bool` | Allow borrowing operations |
| `_canClaimFromStabPool` | `bool` | Allow stability pool claims |
| `_canClaimLoot` | `bool` | Allow reward claims |

#### Access

Only callable by user or authorized delegates

#### Events Emitted

- `UserDelegationSet` - Delegation configuration details

## Utility Functions

### `performHousekeeping`

Performs protocol housekeeping tasks for a user. This includes checking/updating the user's last touch timestamp, updating the Curve price snapshot, and optionally updating the user's debt position.

```vyper
@external
def performHousekeeping(
    _isHigherRisk: bool,
    _user: address,
    _shouldUpdateDebt: bool,
    _a: addys.Addys = empty(addys.Addys),
):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_isHigherRisk` | `bool` | Whether the operation is higher risk (affects last touch and debt health checks) |
| `_user` | `address` | User to perform housekeeping for |
| `_shouldUpdateDebt` | `bool` | Whether to update the user's debt position |
| `_a` | `addys.Addys` | Cached addresses (optional) |

#### Returns

*No return value*

#### Access

Only callable by valid Ripe protocol addresses (trusted contracts)

#### Notes

- Higher risk operations enforce stricter validation (one-action-per-block for non-Underscore wallets)
- Updates the GREEN reference pool snapshot via CurvePrices
- When `_shouldUpdateDebt` is True and `_isHigherRisk` is True, asserts that debt health is maintained
- This function is called internally by most Teller operations but is also exposed for other protocol contracts

### `isUnderscoreWalletOwner`

Checks if caller owns an Underscore smart wallet.

```vyper
@view
@external
def isUnderscoreWalletOwner(_user: address, _caller: address, _mc: address = empty(address)) -> bool:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | Smart wallet address |
| `_caller` | `address` | Potential owner |
| `_mc` | `address` | MissionControl address (optional) |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if caller owns the wallet |

#### Access

Public view function

## Reward Claiming Functions

### `claimLoot`

Claims RIPE token rewards from the Lootbox contract.

```vyper
@nonreentrant
@external
def claimLoot(
    _user: address = msg.sender,
    _shouldStake: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User claiming rewards |
| `_shouldStake` | `bool` | Auto-stake RIPE to governance vault |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total RIPE rewards claimed |

#### Access

Public function with permission checks

#### Example Usage
```python
# Claim and auto-stake RIPE
ripe_rewards = teller.claimLoot(user.address, True)

# Claim without staking
ripe_rewards = teller.claimLoot(user.address, False)
```

### `claimLootForManyUsers`

Batch claims RIPE token rewards for multiple users.

```vyper
@nonreentrant
@external
def claimLootForManyUsers(
    _users: DynArray[address, MAX_CLAIM_USERS],
    _shouldStake: bool = True,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_users` | `DynArray[address, 25]` | Users to claim for |
| `_shouldStake` | `bool` | Auto-stake RIPE to governance vault |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Total RIPE rewards claimed for all users |

#### Access

Public function with permission checks for each user

#### Example Usage
```python
# Claim and stake for multiple users
users = [user1.address, user2.address, user3.address]
total_ripe = teller.claimLootForManyUsers(users, True)
```

## Ripe Governance Vault Functions

### `depositIntoGovVault`

Deposits assets into the governance vault with an optional lock duration.

```vyper
@nonreentrant
@external
def depositIntoGovVault(
    _asset: address,
    _amount: uint256,
    _lockDuration: uint256,
    _user: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to deposit (typically RIPE) |
| `_amount` | `uint256` | Amount to deposit |
| `_lockDuration` | `uint256` | Lock duration in seconds |
| `_user` | `address` | User to deposit for |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount deposited |

#### Access

Public function with permission checks

#### Example Usage
```python
# Deposit RIPE with 1 year lock
amount = teller.depositIntoGovVault(
    ripe.address,
    1000e18,              # 1000 RIPE
    365 * 24 * 60 * 60,   # 1 year lock
    user.address
)
```

### `adjustLock`

Adjusts lock duration for a specific asset in the governance vault.

```vyper
@nonreentrant
@external
def adjustLock(
    _asset: address,
    _newLockDuration: uint256,
    _user: address = msg.sender,
):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to adjust lock for |
| `_newLockDuration` | `uint256` | New lock duration in seconds |
| `_user` | `address` | User adjusting lock |

#### Returns

*No return value*

#### Access

Public function with permission checks

#### Example Usage
```python
# Extend lock to 1 year duration
teller.adjustLock(
    ripe.address,
    365 * 24 * 60 * 60,  # 1 year
    user.address
)
```

### `releaseLock`

Releases unlocked tokens from the governance vault.

```vyper
@nonreentrant
@external
def releaseLock(
    _asset: address,
    _user: address = msg.sender,
):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to release |
| `_user` | `address` | User releasing lock |

#### Returns

*No return value*

#### Access

Public function with permission checks

#### Example Usage
```python
# Release all unlocked RIPE
teller.releaseLock(
    ripe.address,
    user.address
)
```

## Bond Purchase Functions

### `purchaseRipeBond`

Purchases Ripe bonds from the BondRoom with optional lock duration.

```vyper
@nonreentrant
@external
def purchaseRipeBond(
    _paymentAsset: address,
    _paymentAmount: uint256 = max_value(uint256),
    _lockDuration: uint256 = 0,
    _recipient: address = msg.sender,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_paymentAsset` | `address` | Asset to pay with (GREEN or sGREEN) |
| `_paymentAmount` | `uint256` | Amount to spend (max for all balance) |
| `_lockDuration` | `uint256` | Lock duration for purchased RIPE (0 for no lock) |
| `_recipient` | `address` | Recipient of RIPE tokens |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | RIPE tokens received from bond |

#### Access

Public function with permission checks

#### Example Usage
```python
# Purchase Ripe bond with Green
ripe_received = teller.purchaseRipeBond(
    green.address,
    1000e18,                 # 1000 GREEN
    365 * 24 * 60 * 60,      # 1 year lock
    user.address
)

# Purchase with sGREEN, no lock
ripe_received = teller.purchaseRipeBond(
    sgreen.address,
    500e18,
    0,
    user.address
)
```

## Underscore Wallet Utilities

### `setUndyLegoAccess`

Utility function for Underscore smart wallets to grant full protocol access to a Lego strategy contract. This function sets both user config (allowing anyone to deposit, repay debt, and bond) and delegation permissions (withdraw, borrow, claim from stability pool, claim loot) for the specified Lego address.

```vyper
@external
def setUndyLegoAccess(_legoAddr: address) -> bool:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoAddr` | `address` | Lego strategy contract address to grant access |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if access was granted successfully, False if validation failed |

#### Access

Only callable by Underscore smart wallets (msg.sender must be a valid Underscore wallet or vault)

#### Notes

- This function fails gracefully (returns False) rather than reverting to avoid bricking Underscore wallets
- Returns False if MissionControl address is empty, if `_legoAddr` is empty, or if caller is not an Underscore wallet/vault
- Automatically sets user config to allow anyone to deposit, repay debt, and bond for the caller
- Automatically grants full delegation to the Lego address (withdraw, borrow, claim from stability pool, claim loot)

#### Example Usage
```python
# Called from within an Underscore smart wallet to grant Lego access
# The wallet grants permissions for itself to the specified Lego contract
success = teller.setUndyLegoAccess(lego_contract.address)
```

## Key Validation Logic

### Deposit Limits

The contract enforces multiple deposit limits:

1. **Per-User Limits**: Maximum deposit per user per asset
2. **Global Limits**: Protocol-wide deposit caps per asset
3. **Vault Limits**: Maximum assets per vault, maximum vaults per user
4. **Minimum Balance**: Ensures positions meet minimum thresholds

### Permission Hierarchy

Access control follows this hierarchy:

1. **Direct User**: Always has full permissions
2. **Ripe Departments**: Trusted protocol contracts bypass most limits
3. **Delegated Users**: Specific operation permissions
4. **Underscore Owners**: Smart wallet ownership verification
5. **General Permissions**: Configurable proxy permissions

### Automatic Vault Selection

When no vault is specified:

```
vaultId = getFirstVaultIdForAsset(asset)
vaultAddr = getAddr(vaultId)
```

This provides seamless UX by automatically routing to appropriate vaults.