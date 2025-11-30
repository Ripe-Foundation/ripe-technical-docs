# SwitchboardEcho Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/config/SwitchboardEcho.vy)

## Overview

SwitchboardEcho is a specialized Switchboard configuration contract for managing Endaoment and EndaomentPSM operations in Ripe Protocol. It provides time-locked governance control over treasury operations, liquidity management, token swaps, and PSM (Peg Stability Module) configuration.

**Core Features**:
- **Endaoment Operations**: Yield deposits/withdrawals, ETH/WETH conversions, claim incentives, liquidity management
- **EndaomentPSM Control**: Mint/redeem settings, allowlists, fees, rate limits
- **Time-Locked Actions**: All sensitive operations require time lock confirmation
- **Lite Access Mode**: Some operations allow "lite" governance access for faster execution

## Architecture & Modules

SwitchboardEcho uses the standard Switchboard architecture:

### LocalGov Module

- **Location**: `contracts/modules/LocalGov.vy`
- **Purpose**: Provides governance functionality
- **Documentation**: See [LocalGov Technical Documentation](../LocalGov.md)
- **Exported Interface**: Governance utilities via `gov.__interface__`

### TimeLock Module

- **Location**: `contracts/modules/TimeLock.vy`
- **Purpose**: Provides time-locked action management
- **Documentation**: See [TimeLock Technical Documentation](../TimeLock.md)
- **Exported Interface**: Time lock utilities via `timeLock.__interface__`

### Module Initialization

```vyper
initializes: gov
initializes: timeLock[gov := gov]
```

## Action Types

SwitchboardEcho defines 21 time-locked action types:

```vyper
flag ActionType:
    ENDAO_SWAP                           # Token swap in Endaoment
    ENDAO_ADD_LIQUIDITY                  # Add liquidity to pool
    ENDAO_REMOVE_LIQUIDITY               # Remove liquidity from pool
    ENDAO_PARTNER_MINT                   # Mint GREEN for partners
    ENDAO_PARTNER_POOL                   # Add partner liquidity
    ENDAO_REPAY                          # Repay pool debt
    ENDAO_TRANSFER                       # Transfer funds to governance
    PSM_SET_CAN_MINT                     # Enable/disable minting
    PSM_SET_MINT_FEE                     # Set mint fee
    PSM_SET_MAX_INTERVAL_MINT            # Set mint rate limit
    PSM_SET_SHOULD_ENFORCE_MINT_ALLOWLIST # Toggle mint allowlist
    PSM_UPDATE_MINT_ALLOWLIST            # Update mint allowlist
    PSM_SET_CAN_REDEEM                   # Enable/disable redemption
    PSM_SET_REDEEM_FEE                   # Set redeem fee
    PSM_SET_MAX_INTERVAL_REDEEM          # Set redeem rate limit
    PSM_SET_SHOULD_ENFORCE_REDEEM_ALLOWLIST # Toggle redeem allowlist
    PSM_UPDATE_REDEEM_ALLOWLIST          # Update redeem allowlist
    PSM_SET_USDC_YIELD_POSITION          # Set USDC yield strategy
    PSM_SET_NUM_BLOCKS_PER_INTERVAL      # Set rate limit interval
    PSM_SET_SHOULD_AUTO_DEPOSIT          # Toggle auto-deposit
```

## Data Structures

### Endaoment Action Structs

```vyper
struct EndaoLiquidityAction:
    legoId: uint256
    pool: address
    tokenA: address
    tokenB: address
    amountA: uint256
    amountB: uint256
    minAmountA: uint256
    minAmountB: uint256
    minLpAmount: uint256
    extraData: bytes32
    lpToken: address
    lpAmount: uint256

struct EndaoPartnerMintAction:
    partner: address
    asset: address
    amount: uint256

struct EndaoPartnerPoolAction:
    legoId: uint256
    pool: address
    partner: address
    asset: address
    amount: uint256
    minLpAmount: uint256

struct EndaoRepayAction:
    pool: address
    amount: uint256

struct EndaoTransfer:
    asset: address
    amount: uint256
```

### PSM Action Structs

Various structs for PSM configuration actions (mint/redeem settings, fees, allowlists, etc.).

## State Variables

### Public Variables

- `actionType: HashMap[uint256, ActionType]` - Maps action IDs to types
- `pendingEndao*Actions: HashMap[uint256, *Action]` - Pending Endaoment actions
- `pendingPsm*Actions: HashMap[uint256, *Action]` - Pending PSM actions

### Constants

- `MAX_SWAP_INSTRUCTIONS: constant(uint256) = 5`
- `MAX_PROOFS: constant(uint256) = 25`
- `MAX_ASSETS: constant(uint256) = 10`
- `MISSION_CONTROL_ID: constant(uint256) = 5`
- `ENDAOMENT_ID: constant(uint256) = 14`
- `ENDAOMENT_PSM_ID: constant(uint256) = 22`

## Constructor

### `__init__`

Initializes SwitchboardEcho with governance and time lock settings.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _tempGov: address,
    _minConfigTimeLock: uint256,
    _maxConfigTimeLock: uint256,
):
```

#### Parameters

| Name                 | Type      | Description                           |
| -------------------- | --------- | ------------------------------------- |
| `_ripeHq`            | `address` | RipeHq contract address               |
| `_tempGov`           | `address` | Temporary governance address          |
| `_minConfigTimeLock` | `uint256` | Minimum blocks for time-locked actions|
| `_maxConfigTimeLock` | `uint256` | Maximum blocks for time-locked actions|

## Endaoment Lite Functions

These functions allow "lite" governance access (MissionControl.canPerformLiteAction):

### `depositForYieldInEndaoment`

Deposits assets into yield strategies.

```vyper
@external
def depositForYieldInEndaoment(
    _legoId: uint256,
    _asset: address,
    _vaultAddr: address = empty(address),
    _amount: uint256 = max_value(uint256),
    _extraData: bytes32 = empty(bytes32)
) -> (uint256, address, uint256, uint256):
```

### `withdrawFromYieldInEndaoment`

Withdraws assets from yield strategies.

```vyper
@external
def withdrawFromYieldInEndaoment(
    _legoId: uint256,
    _vaultToken: address,
    _amount: uint256 = max_value(uint256),
    _extraData: bytes32 = empty(bytes32)
) -> (uint256, address, uint256, uint256):
```

### `convertEthToWethInEndaoment` / `convertWethToEthInEndaoment`

Converts between ETH and WETH.

### `claimIncentivesInEndaoment`

Claims incentive rewards.

```vyper
@external
def claimIncentivesInEndaoment(
    _user: address,
    _legoId: uint256,
    _rewardToken: address = empty(address),
    _rewardAmount: uint256 = max_value(uint256),
    _proofs: DynArray[bytes32, MAX_PROOFS] = []
) -> (uint256, uint256):
```

### `stabilizeGreenRefPoolInEndaoment`

Triggers GREEN reference pool stabilization.

### `transferFundsToEndaomentPsmInEndaoment`

Transfers funds to the PSM.

### `transferFundsToVaultInEndaoment`

Transfers assets to vaults.

## EndaomentPSM Lite Functions

### `depositToYieldInPsm`

Deposits PSM USDC to yield.

### `withdrawFromYieldInPsm`

Withdraws PSM USDC from yield.

### `transferUsdcToEndaomentFundsInPsm`

Transfers USDC to EndaomentFunds.

## Time-Locked Endaoment Functions

These require full governance and time lock:

### `performEndaomentTransfer`

Initiates fund transfer to governance.

```vyper
@external
def performEndaomentTransfer(_asset: address, _amount: uint256) -> uint256:
```

### `performEndaomentSwap`

Initiates token swap.

```vyper
@external
def performEndaomentSwap(_instructions: DynArray[ul.SwapInstruction, MAX_SWAP_INSTRUCTIONS]) -> uint256:
```

### `addLiquidityInEndaoment` / `removeLiquidityInEndaoment`

Manages pool liquidity.

### `mintPartnerLiquidityInEndaoment`

Mints GREEN for partner liquidity.

### `addPartnerLiquidityInEndaoment`

Adds partner funds to liquidity pool.

### `repayPoolDebtInEndaoment`

Repays debt to a pool.

## Time-Locked PSM Functions

### `setPsmCanMint` / `setPsmCanRedeem`

Enable/disable mint/redeem.

```vyper
@external
def setPsmCanMint(_canMint: bool) -> uint256:
```

**Note**: Disabling (`False`) allows lite access for emergency shutoff.

### `setPsmMintFee` / `setPsmRedeemFee`

Set mint/redeem fees.

### `setPsmMaxIntervalMint` / `setPsmMaxIntervalRedeem`

Set rate limits per interval.

### `setPsmShouldEnforceMintAllowlist` / `setPsmShouldEnforceRedeemAllowlist`

Toggle allowlist enforcement.

### `updatePsmMintAllowlist` / `updatePsmRedeemAllowlist`

Add/remove users from allowlists.

### `setPsmUsdcYieldPosition`

Set the USDC yield strategy.

### `setPsmNumBlocksPerInterval`

Set rate limit interval duration.

### `setPsmShouldAutoDeposit`

Toggle automatic USDC deposits to yield.

**Note**: Disabling (`False`) allows lite access.

## Execution Functions

### `executePendingAction`

Executes a pending time-locked action.

```vyper
@external
def executePendingAction(_aid: uint256) -> bool:
```

#### Access

Only callable by governance

#### Behavior

1. Checks time lock has elapsed
2. If expired, cancels action and returns false
3. Executes the appropriate action based on `actionType`
4. Emits corresponding execution event
5. Clears action type storage

### `cancelPendingAction`

Cancels a pending action.

```vyper
@external
def cancelPendingAction(_aid: uint256) -> bool:
```

## Events

### Pending Action Events

Each action type has a corresponding `Pending*Action` event emitted when initiated.

### Execution Events

Each action type has a corresponding `*Executed` event emitted when confirmed.

### Lite Operation Events

- `EndaomentDepositPerformed`
- `EndaomentWithdrawalPerformed`
- `EndaomentEthToWethPerformed`
- `EndaomentWethToEthPerformed`
- `EndaomentClaimPerformed`
- `EndaomentStabilizerPerformed`
- `EndaomentPsmTransferPerformed`
- `EndaomentVaultTransferPerformed`
- `EndaomentPsmDepositPerformed`
- `EndaomentPsmWithdrawPerformed`
- `EndaomentPsmTransferToFundsPerformed`

## Access Control

### Lite Access

Some operations allow "lite" governance:
- Checked via `MissionControl.canPerformLiteAction(caller)`
- Used for routine treasury operations
- Faster execution without time lock

### Full Governance

Sensitive operations require:
- `gov._canGovern(msg.sender)` check
- Time lock before execution
- Confirmation step after delay

### Emergency Access

Disabling operations (setting to `False`) often allow lite access for emergency response:
- `setPsmCanMint(False)`
- `setPsmCanRedeem(False)`
- `setPsmShouldAutoDeposit(False)`

## Security Considerations

1. **Time-Locked Changes**: All sensitive config changes require time delay
2. **Two-Step Execution**: Initiate then confirm pattern prevents accidents
3. **Lite Access Limits**: Only routine operations allow faster governance
4. **Emergency Shutoff**: Critical functions can be disabled quickly
5. **Event Logging**: All actions emit events for transparency
6. **Expiry Handling**: Expired actions are automatically cancelled
