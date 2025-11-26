# Endaoment Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/Endaoment.vy)

## Overview

Endaoment is the protocol-owned treasury and liquidity management hub for Ripe Protocol, actively managing funds across DeFi strategies while maintaining Green token stability. It serves as the financial nerve center, optimizing
capital efficiency through yield generation and automated market operations.

**Core Functions**:
- **Yield Management**: Deploys funds across modular "Lego" strategies including lending protocols, AMMs, and liquid staking for optimal returns
- **Green Stabilization**: Automated peg maintenance through Curve pool liquidity adjustments based on Green trading ratios
- **Partner Programs**: Facilitates liquidity partnerships with external parties providing assets alongside protocol-minted Green
- **Treasury Operations**: Receives and manages liquidation proceeds, bond sales, fees, and handles ETH/WETH conversions

The contract implements pluggable yield strategies, automated rebalancing, sophisticated AMM management, comprehensive event logging, and debt tracking for leveraged positions while ensuring protocol solvency.

## Architecture & Modules

Endaoment is built using a modular architecture with the following components:

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
  - Green token minting capability (for stabilizer)
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
|                         Endaoment Contract                             |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                  Yield Strategy Management                       |  |
|  |                                                                  |  |
|  |  UndyLego Interface (Pluggable Strategies):                     |  |
|  |  - Lego 1: Aave Lending                                          |  |
|  |  - Lego 2: Compound v3                                          |  |
|  |  - Lego 3: Uniswap v3 LP                                        |  |
|  |  - Lego 4: Curve Pools                                          |  |
|  |  - Lego 5: Liquid Staking                                       |  |
|  |                                                                  |  |
|  |  Operations:                                                     |  |
|  |  1. depositForYield() -> Higher yield                            |  |
|  |  2. withdrawFromYield() -> Retrieve funds                        |  |
|  |  3. rebalanceYieldPosition() -> Switch strategies                |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                   Green Stabilizer System                       |  |
|  |                                                                  |  |
|  |  Automated Peg Maintenance:                                     |  |
|  |  - Monitor Green ratio in Curve pools                            |  |
|  |  - If ratio < 50%: Add Green liquidity                          |  |
|  |  - If ratio > 50%: Remove Green liquidity                       |  |
|  |                                                                  |  |
|  |  Profit Calculation:                                             |  |
|  |  LP Value + Leftover Green - Pool Debt = Net Position           |  |
|  |                                                                  |  |
|  |  Debt Management:                                                |  |
|  |  - Track minted Green for liquidity                             |  |
|  |  - Repay debt when removing liquidity                           |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                  Partner Liquidity Programs                     |  |
|  |                                                                  |  |
|  |  Two Models:                                                     |  |
|  |  1. Mint & Pair: Protocol mints Green, partner provides asset   |  |
|  |     - Equal value pairing                                       |  |
|  |     - Shared IL risk                                            |  |
|  |                                                                  |  |
|  |  2. Add Liquidity: Both sides provide existing tokens           |  |
|  |     - Flexible ratios                                           |  |
|  |     - Existing pool participation                               |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| UndyLego Strats  |    | Curve Pools       |    | Partner Wallets  |
| * Yield farming  |    | * Green/USDC      |    | * External funds |
| * LP management  |    | * Peg maintenance |    | * Shared rewards |
| * Rebalancing    |    | * Debt tracking   |    | * IL sharing     |
+------------------+    +-------------------+    +------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| Ledger           |    | PriceDesk         |    | Green Token      |
| * Pool debt      |    | * USD values      |    | * Mint for liq   |
| * Yield tracking |    | * Profit calc     |    | * Stabilization  |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### StabilizerConfig Struct
Configuration for Green stabilizer (from CurvePrices):
```vyper
struct StabilizerConfig:
    pool: address                    # Curve pool address
    lpToken: address                 # LP token address
    greenBalance: uint256            # Current Green in pool
    greenRatio: uint256              # Green percentage (basis points)
    greenIndex: uint256              # Green token index in pool
    stabilizerAdjustWeight: uint256  # Adjustment aggressiveness
    stabilizerMaxPoolDebt: uint256   # Maximum debt allowed
```

## State Variables

### Immutable Variables
- `WETH: public(immutable(address))` - Wrapped Ether address
- `ETH: public(immutable(address))` - ETH representation address

### Constants
- `HUNDRED_PERCENT: uint256 = 100_00` - 100.00% in basis points
- `FIFTY_PERCENT: uint256 = 50_00` - 50.00% target ratio
- `EIGHTEEN_DECIMALS: uint256 = 10 ** 18` - Standard precision
- `MAX_SWAP_INSTRUCTIONS: uint256 = 5` - Batch swap limit
- `MAX_TOKEN_PATH: uint256 = 5` - Multi-hop path limit
- `MAX_ASSETS: uint256 = 10` - Asset batch limit
- `MAX_LEGOS: uint256 = 10` - Strategy limit
- `LEGO_BOOK_ID: uint256 = 3` - Lego registry ID
- `CURVE_PRICES_ID: uint256 = 2` - Curve prices registry ID
- `MAX_PROOFS: uint256 = 25` - Maximum merkle proofs for incentive claims

### Inherited State Variables
From [DeptBasics](../shared-modules/DeptBasics.md):
- `isPaused: bool` - Department pause state
- `canMintGreen: bool` - Set to `True` for stabilizer

## Constructor

### `__init__`

Initializes Endaoment with Green minting capability and ETH handling.

```vyper
@deploy
def __init__(_ripeHq: address, _weth: address, _eth: address):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_ripeHq` | `address` | RipeHq contract address |
| `_weth` | `address` | WETH token contract |
| `_eth` | `address` | ETH representation address |

#### Returns

*Constructor does not return any values*

#### Access

Called only during deployment

#### Example Usage
```python
# Deploy Endaoment
endaoment = boa.load(
    "contracts/core/Endaoment.vy",
    ripe_hq.address,
    weth.address,
    eth_address
)
```

**Example Output**: Contract deployed with treasury management capabilities

## Transfer Funds Functions

### `transferFundsToGov`

Transfers assets from EndaomentFunds to the governance address.

```vyper
@external
def transferFundsToGov(
    _asset: address,
    _amount: uint256 = max_value(uint256),
) -> (uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_asset` | `address` | Asset to transfer |
| `_amount` | `uint256` | Amount to transfer (max for all) |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256)` | (amount transferred, USD value) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Transfer details (op code 1)

### `transferFundsToVault`

Transfers multiple assets from Endaoment to EndaomentFunds vault.

```vyper
@external
def transferFundsToVault(_assets: DynArray[address, MAX_ASSETS]):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_assets` | `DynArray[address, 10]` | Assets to transfer (empty address = ETH) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Transfer details (op code 1) for each asset

### `transferFundsToEndaomentPSM`

Transfers USDC from EndaomentFunds to EndaomentPSM.

```vyper
@external
def transferFundsToEndaomentPSM(_amount: uint256 = max_value(uint256)) -> (uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_amount` | `uint256` | USDC amount to transfer (max for all) |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256)` | (amount transferred, USD value) |

#### Access

Only callable by Switchboard-registered contracts or Governance

#### Events Emitted

- `WalletAction` - Transfer details (op code 1)

## Yield Strategy Functions

### `depositForYield`

Deposits assets into yield-generating strategies via Lego contracts.

```vyper
@nonreentrant
@external
def depositForYield(
    _legoId: uint256,
    _asset: address,
    _vaultAddr: address = empty(address),
    _amount: uint256 = max_value(uint256),
    _extraData: bytes32 = empty(bytes32),
) -> (uint256, address, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoId` | `uint256` | Strategy ID from registry |
| `_asset` | `address` | Asset to deposit |
| `_vaultAddr` | `address` | Specific vault (optional) |
| `_amount` | `uint256` | Amount to deposit (max for all) |
| `_extraData` | `bytes32` | Strategy-specific data |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, address, uint256, uint256)` | (assetAmount, vaultToken, vaultTokenAmount, usdValue) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Operation details including:
  - Operation code (10 for deposit)
  - Input/output assets and amounts
  - USD value and strategy ID

#### Example Usage
```python
# Deposit USDC into Aave
asset_used, vault_token, vault_amount, usd_val = endaoment.depositForYield(
    1,  # Aave Lego ID
    usdc.address,
    aave_usdc_vault.address,
    1000_000000,  # 1000 USDC
    b"",
    sender=treasury_manager.address
)
```

### `withdrawFromYield`

Withdraws assets from yield strategies.

```vyper
@nonreentrant
@external
def withdrawFromYield(
    _legoId: uint256,
    _vaultToken: address,
    _amount: uint256 = max_value(uint256),
    _extraData: bytes32 = empty(bytes32),
) -> (uint256, address, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoId` | `uint256` | Strategy ID |
| `_vaultToken` | `address` | Vault token to redeem |
| `_amount` | `uint256` | Amount to withdraw |
| `_extraData` | `bytes32` | Strategy-specific data |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, address, uint256, uint256)` | (vaultTokenBurned, underlyingAsset, underlyingAmount, usdValue) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Withdrawal details (op code 11)

## Liquidity Management Functions

### `addLiquidity`

Adds liquidity to AMM pools.

```vyper
@nonreentrant
@external
def addLiquidity(
    _legoId: uint256,
    _pool: address,
    _tokenA: address,
    _tokenB: address,
    _amountA: uint256 = max_value(uint256),
    _amountB: uint256 = max_value(uint256),
    _minAmountA: uint256 = 0,
    _minAmountB: uint256 = 0,
    _minLpAmount: uint256 = 0,
    _extraData: bytes32 = empty(bytes32),
) -> (uint256, uint256, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoId` | `uint256` | AMM strategy ID |
| `_pool` | `address` | Pool address |
| `_tokenA` | `address` | First token |
| `_tokenB` | `address` | Second token |
| `_amountA` | `uint256` | Amount of token A |
| `_amountB` | `uint256` | Amount of token B |
| `_minAmountA` | `uint256` | Minimum token A to use |
| `_minAmountB` | `uint256` | Minimum token B to use |
| `_minLpAmount` | `uint256` | Minimum LP tokens |
| `_extraData` | `bytes32` | Pool-specific data |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256, uint256, uint256)` | (lpReceived, amountAUsed, amountBUsed, usdValue) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Liquidity addition details (op code 30)

### `removeLiquidity`

Removes liquidity from AMM pools.

```vyper
@nonreentrant
@external
def removeLiquidity(
    _legoId: uint256,
    _pool: address,
    _tokenA: address,
    _tokenB: address,
    _lpToken: address,
    _lpAmount: uint256 = max_value(uint256),
    _minAmountA: uint256 = 0,
    _minAmountB: uint256 = 0,
    _extraData: bytes32 = empty(bytes32),
) -> (uint256, uint256, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoId` | `uint256` | AMM strategy ID |
| `_pool` | `address` | Pool address |
| `_tokenA` | `address` | First token |
| `_tokenB` | `address` | Second token |
| `_lpToken` | `address` | LP token address |
| `_lpAmount` | `uint256` | LP tokens to burn |
| `_minAmountA` | `uint256` | Minimum token A |
| `_minAmountB` | `uint256` | Minimum token B |
| `_extraData` | `bytes32` | Pool-specific data |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256, uint256, uint256)` | (amountAReceived, amountBReceived, lpBurned, usdValue) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Liquidity removal details (op code 31)

## Green Stabilizer Functions

### `stabilizeGreenRefPool`

Automatically adjusts Green liquidity to maintain peg stability.

```vyper
@external
def stabilizeGreenRefPool() -> bool:
```

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if adjustment was made |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `StabilizerPoolLiqAdded` - When adding Green liquidity
- `StabilizerPoolLiqRemoved` - When removing Green liquidity

#### Example Usage
```python
# Automated stabilization call
was_adjusted = endaoment.stabilizeGreenRefPool(
    sender=stabilizer_bot.address
)
# Returns: True if pool was rebalanced
```

**Example Output**: Adjusts Green liquidity based on current pool ratio

### `getGreenAmountToAddInStabilizer`

Previews how much Green would be added to stabilizer.

```vyper
@view
@external
def getGreenAmountToAddInStabilizer() -> uint256:
```

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Green amount that would be added |

#### Access

Public view function

#### Example Usage
```python
# Preview stabilizer action
green_to_add = endaoment.getGreenAmountToAddInStabilizer()
# Returns: Amount of Green that would be added to pool
```

### `getGreenAmountToRemoveInStabilizer`

Previews how much Green would be removed from the stabilizer pool.

```vyper
@view
@external
def getGreenAmountToRemoveInStabilizer() -> uint256:
```

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Green amount that would be removed |

#### Access

Public view function

#### Example Usage
```python
# Preview stabilizer removal
green_to_remove = endaoment.getGreenAmountToRemoveInStabilizer()
# Returns: Amount of Green that would be removed from pool
```

## Partner Liquidity Functions

### `mintPartnerLiquidity`

Takes a partner's asset, gets its USD value, and mints an equivalent amount of Green tokens. The partner can be an external wallet or the Endaoment itself.

```vyper
@nonreentrant
@external
def mintPartnerLiquidity(
    _partner: address,
    _asset: address,
    _amount: uint256,
) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_partner` | `address` | Partner wallet providing asset (can be Endaoment itself) |
| `_asset` | `address` | Asset being provided |
| `_amount` | `uint256` | Amount of asset |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount of Green tokens minted |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `PartnerLiquidityMinted` - Contains partner address, asset, amount, and Green minted

#### Special Behavior - Self as Partner

When `_partner` is the Endaoment contract address itself:
- **No token transfer**: Assets are used directly from Endaoment's existing balance
- **Internal operation**: Functions as an internal mint operation using treasury funds
- **Same events**: Events are still emitted with Endaoment as the partner address

#### Example Usage
```python
# External partner provides 10 ETH for liquidity
green_minted = endaoment.mintPartnerLiquidity(
    partner.address,
    weth.address,
    10_000000000000000000,  # 10 ETH
    sender=treasury_manager.address
)
# Returns: Amount of Green minted (e.g., 15000e18 if ETH = $1500)

# Endaoment using its own funds
green_minted = endaoment.mintPartnerLiquidity(
    endaoment.address,  # Self as partner
    usdc.address,
    1000_000000,  # 1000 USDC from treasury
    sender=treasury_manager.address
)
# Returns: 1000e18 Green minted (assuming $1 USDC)
```

### `addPartnerLiquidity`

Takes a partner's asset, mints equivalent Green tokens, and adds both to a liquidity pool. LP tokens are shared between the partner and Endaoment, except when the partner is Endaoment itself.

```vyper
@nonreentrant
@external
def addPartnerLiquidity(
    _legoId: uint256,
    _pool: address,
    _partner: address,
    _asset: address,
    _amount: uint256 = max_value(uint256),
    _minLpAmount: uint256 = 0,
) -> (uint256, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_legoId` | `uint256` | AMM strategy ID |
| `_pool` | `address` | Pool address |
| `_partner` | `address` | Partner wallet address (can be Endaoment itself) |
| `_asset` | `address` | Partner's asset |
| `_amount` | `uint256` | Partner's asset contribution (max = all available) |
| `_minLpAmount` | `uint256` | Minimum LP tokens |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256, uint256)` | (lpAmountReceived, liqAmountA, liqAmountB) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `PartnerLiquidityAdded` - Partnership liquidity details

#### Special Behavior - Self as Partner

When `_partner` is the Endaoment contract address itself:
- **No token transfer**: Assets used directly from Endaoment's balance
- **All LP tokens to Endaoment**: No 50/50 split - all LP tokens remain with Endaoment
- **Same pool debt tracking**: Pool debt is still tracked for newly minted Green tokens
- **Treasury operation**: Functions as an internal treasury liquidity operation

#### Example Usage
```python
# External partner liquidity (50/50 LP split)
lp_tokens, amount_a, amount_b = endaoment.addPartnerLiquidity(
    2,  # Curve Lego ID
    curve_pool.address,
    partner.address,
    usdc.address,
    1000_000000,  # 1000 USDC from partner
    950_000000000000000000,  # Min LP tokens
    sender=treasury_manager.address
)
# LP tokens split: 50% to partner, 50% to Endaoment

# Endaoment self-liquidity (all LP to Endaoment)
lp_tokens, amount_a, amount_b = endaoment.addPartnerLiquidity(
    2,  # Curve Lego ID
    curve_pool.address,
    endaoment.address,  # Self as partner
    usdc.address,
    2000_000000,  # 2000 USDC from treasury
    1900_000000000000000000,  # Min LP tokens
    sender=treasury_manager.address
)
# LP tokens: 100% remain with Endaoment
```

## Swap and Exchange Functions

### `swapTokens`

Executes a series of token swaps through different DeFi protocols (Lego contracts).

```vyper
@nonreentrant
@external
def swapTokens(
    _instructions: DynArray[SwapInstruction, MAX_SWAP_INSTRUCTIONS],
) -> (address, uint256, address, uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_instructions` | `DynArray[SwapInstruction, 5]` | Array of swap instructions containing token paths, pool paths, amounts, and lego IDs |

#### Returns

| Type | Description |
|------|-------------|
| `(address, uint256, address, uint256, uint256)` | (tokenIn, amountIn, tokenOut, amountOut, maxUsdValue) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Swap details (op code 20)

#### Example Usage
```python
# Swap USDC to ETH through multiple routes
instructions = [
    SwapInstruction(
        legoId=1,
        amountIn=1000_000000,
        minAmountOut=650000000000000000,
        tokenPath=[usdc.address, weth.address],
        poolPath=[curve_pool.address]
    )
]
token_in, amount_in, token_out, amount_out, usd_val = endaoment.swapTokens(
    instructions,
    sender=treasury_manager.address
)
```

## Yield and Reward Functions

### `claimIncentives`

Claims accumulated incentive rewards from a yield strategy using merkle proofs.

```vyper
@nonreentrant
@external
def claimIncentives(
    _user: address,
    _legoId: uint256,
    _rewardToken: address = empty(address),
    _rewardAmount: uint256 = max_value(uint256),
    _proofs: DynArray[bytes32, MAX_PROOFS] = [],
) -> (uint256, uint256):
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_user` | `address` | User address to claim for |
| `_legoId` | `uint256` | Strategy ID with incentives |
| `_rewardToken` | `address` | Reward token address |
| `_rewardAmount` | `uint256` | Amount to claim |
| `_proofs` | `DynArray[bytes32, 25]` | Merkle proofs for claim |

#### Returns

| Type | Description |
|------|-------------|
| `(uint256, uint256)` | (reward amount claimed, USD value) |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - Incentive claim details (op code 50)

#### Example Usage
```python
# Claim incentive rewards
reward_amount, usd_value = endaoment.claimIncentives(
    endaoment.address,
    1,  # Lego ID
    reward_token.address,
    1000e18,
    merkle_proofs,
    sender=treasury_manager.address
)
```

## ETH and WETH Conversion

### `convertEthToWeth`

A payable function to wrap ETH into WETH.

```vyper
@payable
@nonreentrant
@external
def convertEthToWeth(_amount: uint256 = max_value(uint256)) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_amount` | `uint256` | Amount to wrap (max = msg.value) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount of WETH received |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - ETH wrap details (op code 80)

#### Example Usage
```python
# Wrap 5 ETH to WETH
weth_amount = endaoment.convertEthToWeth(
    5_000000000000000000,
    value=5_000000000000000000,  # Send 5 ETH
    sender=treasury_manager.address
)
# Returns: 5000000000000000000 (5 WETH)
```

### `convertWethToEth`

Unwraps WETH back into ETH.

```vyper
@nonreentrant
@external
def convertWethToEth(_amount: uint256 = max_value(uint256)) -> uint256:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_amount` | `uint256` | Amount to unwrap (max = balance) |

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Amount of ETH received |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `WalletAction` - ETH unwrap details (op code 81)

#### Example Usage
```python
# Unwrap all WETH to ETH
eth_amount = endaoment.convertWethToEth(
    sender=treasury_manager.address
)
# Returns: Amount of ETH received
```

## Treasury Management

### `repayPoolDebt`

Repays the debt that was created when minting Green for a specific pool.

```vyper
@external
def repayPoolDebt(_pool: address, _amount: uint256 = max_value(uint256)) -> bool:
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `_pool` | `address` | Pool address to repay debt for |
| `_amount` | `uint256` | Amount to repay (max = full debt) |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if debt was repaid |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `PoolDebtRepaid` - Contains pool address and amount repaid

#### Example Usage
```python
# Repay all debt for a specific pool
success = endaoment.repayPoolDebt(
    curve_pool.address,
    sender=treasury_manager.address
)

# Repay partial debt
success = endaoment.repayPoolDebt(
    curve_pool.address,
    500e18,  # Repay 500 Green
    sender=treasury_manager.address
)
```

### `calcProfitForStabilizer`

Calculates the current profit position for the stabilizer.

```vyper
@view
@external
def calcProfitForStabilizer() -> uint256:
```

#### Returns

| Type | Description |
|------|-------------|
| `uint256` | Net profit in LP token terms |

#### Access

Public view function

#### Example Usage
```python
# Get current stabilizer profit
profit = endaoment.calcProfitForStabilizer()
```

## Key Mathematical Functions

### Stabilizer Profit Calculation

Calculates net position value for stabilizer operations:

```
profit = lpValue + leftoverGreen - poolDebt
```

Where:
- lpValue = LP tokens × virtual price
- leftoverGreen = Green token balance
- poolDebt = Minted Green for liquidity

### Green Amount Calculation

For adding liquidity when Green ratio < 50%:

```
totalPoolBalance = greenBalance × 100% / greenRatio
targetBalance = totalPoolBalance / 2
greenAdjustFull = (targetBalance - greenBalance) × 2
greenAdjustWeighted = greenAdjustFull × adjustWeight / 100%
```

For removing liquidity when Green ratio > 50%:

```
greenAdjustFull = (greenBalance - targetBalance) × 2
maxRemovable = max(poolDebt, userLpShare × greenBalance)
```

## Testing

For comprehensive test examples, see: [`tests/core/test_endaoment.py`](../../tests/core/test_endaoment.py)