# EndaomentPSM Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/EndaomentPSM.vy)

## Overview

EndaomentPSM (Peg Stability Module) is the GREEN/USDC conversion engine of Ripe Protocol, enabling users to mint GREEN stablecoins by depositing USDC and redeem GREEN for USDC. This creates a direct arbitrage mechanism that helps maintain the GREEN peg to USD.

**Core Functions**:
- **GREEN Minting**: Deposit USDC to mint GREEN tokens (optionally as sGREEN)
- **GREEN Redemption**: Burn GREEN to receive USDC
- **Yield Generation**: Idle USDC is deposited into yield strategies for protocol revenue
- **Rate Limiting**: Block-based interval limits prevent excessive mint/redeem volumes
- **Fee Collection**: Configurable fees on mint and redeem operations
- **Allowlist Control**: Optional allowlists for controlled access during launch phases

The PSM uses underscore protocol integration for yield strategies and provides special treatment for underscore addresses (bypass fees and rate limits). It works closely with [Endaoment](./Endaoment.md) for treasury management and [EndaomentFunds](./EndaomentFunds.md) for USDC transfers.

## Architecture & Modules

EndaomentPSM is built using a modular architecture with the following components:

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
  - GREEN minting capability enabled
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
|                        EndaomentPSM Contract                            |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                      Mint Flow (USDC → GREEN)                     |  |
|  |                                                                  |  |
|  |  1. User sends USDC                                               |  |
|  |  2. Apply mint fee (unless underscore)                            |  |
|  |  3. Check interval limit (unless underscore)                      |  |
|  |  4. Mint GREEN (or deposit to sGREEN)                            |  |
|  |  5. Auto-deposit USDC to yield (if enabled)                       |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Redeem Flow (GREEN → USDC)                     |  |
|  |                                                                  |  |
|  |  1. User sends GREEN (or sGREEN)                                  |  |
|  |  2. Check interval limit (unless underscore)                      |  |
|  |  3. Calculate USDC to return                                      |  |
|  |  4. Apply redeem fee (unless underscore)                          |  |
|  |  5. Withdraw from yield if needed                                 |  |
|  |  6. Transfer USDC to user                                         |  |
|  |  7. Burn GREEN                                                    |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Yield Position Management                      |  |
|  |                                                                  |  |
|  |  - USDC deposited to underscore Lego strategies                  |  |
|  |  - Auto-deposit on mint (if shouldAutoDeposit)                   |  |
|  |  - Withdraw as needed for redemptions                            |  |
|  |  - Manual deposit/withdraw by Ripe addresses                     |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| GreenToken       |    | SavingsGreen      |    | Underscore Lego  |
| * Mint tokens    |    | * sGREEN deposit  |    | * Yield strategy |
| * Burn tokens    |    | * Share conversion|    | * Vault tokens   |
+------------------+    +-------------------+    +------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| PriceDesk        |    | EndaomentFunds    |    | MissionControl   |
| * USD pricing    |    | * USDC transfers  |    | * Underscore reg |
| * USDC valuation |    | * Protocol vault  |    | * Config access  |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### PsmInterval Struct

Tracks mint/redeem activity within a time interval:

```vyper
struct PsmInterval:
    start: uint256      # Block number when interval started
    amount: uint256     # Total amount processed in this interval
```

### UsdcYieldPosition Struct

Configuration for USDC yield strategy:

```vyper
struct UsdcYieldPosition:
    legoId: uint256     # Underscore Lego ID for yield strategy
    vaultToken: address # Vault token received from yield deposit
```

## Events

### MintGreen

Emitted when GREEN is minted via USDC deposit:

```vyper
event MintGreen:
    user: indexed(address)      # Recipient of GREEN
    sender: indexed(address)    # Transaction sender
    usdcIn: uint256             # USDC deposited
    greenOut: uint256           # GREEN minted
    usdcFee: uint256            # Fee collected in USDC
    receivedSavingsGreen: bool  # Whether received as sGREEN
```

### RedeemGreen

Emitted when GREEN is redeemed for USDC:

```vyper
event RedeemGreen:
    user: indexed(address)      # USDC recipient
    sender: indexed(address)    # Transaction sender
    greenIn: uint256            # GREEN burned
    usdcOut: uint256            # USDC received
    usdcFee: uint256            # Fee collected in USDC
    paidWithSavingsGreen: bool  # Whether paid with sGREEN
```

### EndaomentPSMYieldDeposit

Emitted when USDC is deposited to yield:

```vyper
event EndaomentPSMYieldDeposit:
    amount: uint256                 # USDC deposited
    vaultToken: indexed(address)    # Vault token address
    vaultTokenReceived: uint256     # Vault tokens received
    usdValue: uint256               # USD value of deposit
```

### EndaomentPSMYieldWithdrawal

Emitted when USDC is withdrawn from yield:

```vyper
event EndaomentPSMYieldWithdrawal:
    vaultToken: indexed(address)    # Vault token address
    vaultTokenBurned: uint256       # Vault tokens burned
    usdcReceived: uint256           # USDC received
    usdValue: uint256               # USD value of withdrawal
```

### Configuration Events

```vyper
event CanMintUpdated:
    canMint: bool

event CanRedeemUpdated:
    canRedeem: bool

event MintFeeUpdated:
    fee: uint256

event RedeemFeeUpdated:
    fee: uint256

event MaxIntervalMintUpdated:
    maxAmount: uint256

event MaxIntervalRedeemUpdated:
    maxAmount: uint256

event NumBlocksPerIntervalUpdated:
    blocks: uint256

event ShouldEnforceMintAllowlistUpdated:
    shouldEnforce: bool

event ShouldEnforceRedeemAllowlistUpdated:
    shouldEnforce: bool

event MintAllowlistUpdated:
    user: indexed(address)
    isAllowed: bool

event RedeemAllowlistUpdated:
    user: indexed(address)
    isAllowed: bool

event UsdcYieldPositionUpdated:
    legoId: uint256
    vaultToken: indexed(address)

event ShouldAutoDepositUpdated:
    shouldAutoDeposit: bool
```

## State Variables

### Constants

- `UNDERSCORE_LEGOBOOK_ID: uint256 = 3` - Registry ID for underscore lego book
- `UNDERSCORE_VAULT_REGISTRY_ID: uint256 = 10` - Registry ID for underscore vault registry
- `HUNDRED_PERCENT: uint256 = 100_00` - 100.00% in basis points
- `ONE_USDC: uint256 = 10 ** 6` - 1 USDC (6 decimals)
- `ONE_GREEN: uint256 = 10 ** 18` - 1 GREEN (18 decimals)

### Immutables

- `USDC: address` - USDC token address

### General Configuration

- `numBlocksPerInterval: uint256` - Duration of rate limit intervals in blocks
- `usdcYieldPosition: UsdcYieldPosition` - Current yield strategy configuration
- `shouldAutoDeposit: bool` - Whether to auto-deposit USDC to yield on mint

### Mint Configuration

- `canMint: bool` - Global mint toggle
- `mintFee: uint256` - Mint fee in basis points
- `maxIntervalMint: uint256` - Maximum GREEN mintable per interval
- `mintAllowlist: HashMap[address, bool]` - Addresses allowed to mint
- `shouldEnforceMintAllowlist: bool` - Whether to enforce allowlist
- `globalMintInterval: PsmInterval` - Current mint interval state

### Redeem Configuration

- `canRedeem: bool` - Global redeem toggle
- `redeemFee: uint256` - Redeem fee in basis points
- `maxIntervalRedeem: uint256` - Maximum GREEN redeemable per interval
- `redeemAllowlist: HashMap[address, bool]` - Addresses allowed to redeem
- `shouldEnforceRedeemAllowlist: bool` - Whether to enforce allowlist
- `globalRedeemInterval: PsmInterval` - Current redeem interval state

### Inherited State Variables

From [DeptBasics](../core-modules/DeptBasics.md):

- `isPaused: bool` - Department pause state
- `canMintGreen: bool` - Set to `True` for GREEN minting

## Constructor

### `__init__`

Initializes EndaomentPSM with configuration parameters.

```vyper
@deploy
def __init__(
    _ripeHq: address,
    _numBlocksPerInterval: uint256,
    _mintFee: uint256,
    _maxIntervalMint: uint256,
    _redeemFee: uint256,
    _maxIntervalRedeem: uint256,
    _usdc: address,
    _usdcYieldLegoId: uint256,
    _usdcYieldVaultToken: address,
):
```

#### Parameters

| Name                    | Type      | Description                      |
| ----------------------- | --------- | -------------------------------- |
| `_ripeHq`               | `address` | RipeHq contract address          |
| `_numBlocksPerInterval` | `uint256` | Blocks per rate limit interval   |
| `_mintFee`              | `uint256` | Initial mint fee (basis points)  |
| `_maxIntervalMint`      | `uint256` | Max GREEN mintable per interval  |
| `_redeemFee`            | `uint256` | Initial redeem fee (basis points)|
| `_maxIntervalRedeem`    | `uint256` | Max GREEN redeemable per interval|
| `_usdc`                 | `address` | USDC token address               |
| `_usdcYieldLegoId`      | `uint256` | Lego ID for yield strategy       |
| `_usdcYieldVaultToken`  | `address` | Vault token for yield strategy   |

#### Example Usage

```python
# Deploy EndaomentPSM
psm = boa.load(
    "contracts/core/EndaomentPSM.vy",
    ripe_hq.address,
    7200,           # ~1 day at 12s blocks
    50,             # 0.5% mint fee
    1_000_000e18,   # 1M GREEN max per interval
    50,             # 0.5% redeem fee
    1_000_000e18,   # 1M GREEN max per interval
    usdc.address,
    1,              # Lego ID
    vault_token.address
)
```

## Mint Functions

### `mintGreen`

Mints GREEN tokens by depositing USDC. Optionally delivers as sGREEN.

```vyper
@nonreentrant
@external
def mintGreen(
    _usdcAmount: uint256 = max_value(uint256),
    _recipient: address = msg.sender,
    _wantsSavingsGreen: bool = False
) -> uint256:
```

#### Parameters

| Name                 | Type      | Description                     |
| -------------------- | --------- | ------------------------------- |
| `_usdcAmount`        | `uint256` | USDC to deposit (max=all)       |
| `_recipient`         | `address` | GREEN recipient (default=sender)|
| `_wantsSavingsGreen` | `bool`    | Receive as sGREEN instead       |

#### Returns

| Type      | Description        |
| --------- | ------------------ |
| `uint256` | GREEN amount minted|

#### Access

Public, but may require allowlist if `shouldEnforceMintAllowlist` is true.
Underscore addresses bypass allowlist, fees, and interval limits.

#### Events Emitted

- `MintGreen` - Mint details

#### Example Usage

```python
# Mint GREEN from USDC
usdc.approve(psm.address, 1000e6)
green_minted = psm.mintGreen(1000e6, user.address, False)

# Mint sGREEN from USDC
usdc.approve(psm.address, 1000e6)
green_minted = psm.mintGreen(1000e6, user.address, True)
```

### `getMaxUsdcAmountForMint`

Returns the maximum USDC amount that can be used for minting.

```vyper
@view
@external
def getMaxUsdcAmountForMint(
    _user: address = empty(address),
    _isUnderscoreAddr: bool = False
) -> uint256:
```

#### Parameters

| Name               | Type      | Description                          |
| ------------------ | --------- | ------------------------------------ |
| `_user`            | `address` | User to check balance (optional)     |
| `_isUnderscoreAddr`| `bool`    | Whether caller is underscore address |

#### Returns

| Type      | Description              |
| --------- | ------------------------ |
| `uint256` | Maximum USDC for minting |

#### Example Usage

```python
# Get max mintable for user
max_usdc = psm.getMaxUsdcAmountForMint(user.address, False)
```

### `getAvailIntervalMint`

Returns remaining GREEN mintable in the current interval.

```vyper
@view
@external
def getAvailIntervalMint() -> uint256:
```

#### Returns

| Type      | Description                        |
| --------- | ---------------------------------- |
| `uint256` | Remaining GREEN mintable in interval|

## Redeem Functions

### `redeemGreen`

Redeems GREEN (or sGREEN) for USDC.

```vyper
@nonreentrant
@external
def redeemGreen(
    _paymentAmount: uint256 = max_value(uint256),
    _recipient: address = msg.sender,
    _isPaymentSavingsGreen: bool = False
) -> uint256:
```

#### Parameters

| Name                    | Type      | Description                        |
| ----------------------- | --------- | ---------------------------------- |
| `_paymentAmount`        | `uint256` | GREEN to redeem (max=all)          |
| `_recipient`            | `address` | USDC recipient (default=sender)    |
| `_isPaymentSavingsGreen`| `bool`    | Pay with sGREEN instead of GREEN   |

#### Returns

| Type      | Description         |
| --------- | ------------------- |
| `uint256` | USDC amount received|

#### Access

Public, but may require allowlist if `shouldEnforceRedeemAllowlist` is true.
Underscore addresses bypass allowlist, fees, and interval limits.

#### Events Emitted

- `RedeemGreen` - Redemption details

#### Example Usage

```python
# Redeem GREEN for USDC
green_token.approve(psm.address, 1000e18)
usdc_received = psm.redeemGreen(1000e18, user.address, False)

# Redeem sGREEN for USDC
savings_green.approve(psm.address, 1000e18)
usdc_received = psm.redeemGreen(1000e18, user.address, True)
```

### `getMaxRedeemableGreenAmount`

Returns the maximum GREEN amount that can be redeemed.

```vyper
@view
@external
def getMaxRedeemableGreenAmount(
    _user: address = empty(address),
    _isUnderscoreAddr: bool = False
) -> uint256:
```

#### Parameters

| Name               | Type      | Description                          |
| ------------------ | --------- | ------------------------------------ |
| `_user`            | `address` | User to check balance (optional)     |
| `_isUnderscoreAddr`| `bool`    | Whether caller is underscore address |

#### Returns

| Type      | Description                 |
| --------- | --------------------------- |
| `uint256` | Maximum GREEN for redemption|

### `getAvailIntervalRedemptions`

Returns remaining GREEN redeemable in the current interval.

```vyper
@view
@external
def getAvailIntervalRedemptions() -> uint256:
```

#### Returns

| Type      | Description                          |
| --------- | ------------------------------------ |
| `uint256` | Remaining GREEN redeemable in interval|

## Yield Position Functions

### `getUsdcYieldPositionVaultToken`

Returns the vault token address for the current yield position.

```vyper
@view
@external
def getUsdcYieldPositionVaultToken() -> address:
```

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `address` | Vault token address  |

### `depositToYield`

Manually deposits idle USDC to the yield strategy.

```vyper
@nonreentrant
@external
def depositToYield() -> uint256:
```

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | USDC amount deposited|

#### Access

Only callable by valid Ripe addresses

#### Events Emitted

- `EndaomentPSMYieldDeposit` - Deposit details

### `withdrawFromYield`

Withdraws USDC from the yield strategy.

```vyper
@external
def withdrawFromYield(
    _amount: uint256 = max_value(uint256),
    _shouldTransferToEndaoFunds: bool = False,
    _shouldFullSweep: bool = False
) -> (uint256, uint256):
```

#### Parameters

| Name                        | Type      | Description                      |
| --------------------------- | --------- | -------------------------------- |
| `_amount`                   | `uint256` | USDC to withdraw (max=all)       |
| `_shouldTransferToEndaoFunds`| `bool`   | Transfer to EndaomentFunds       |
| `_shouldFullSweep`          | `bool`    | Transfer entire balance          |

#### Returns

| Type      | Description                 |
| --------- | --------------------------- |
| `uint256` | USDC withdrawn from yield   |
| `uint256` | USDC transferred to EndaoFunds|

#### Access

Only callable by valid Ripe addresses

#### Events Emitted

- `EndaomentPSMYieldWithdrawal` - Withdrawal details

### `getUnderlyingYieldAmount`

Returns the USDC value in the yield position.

```vyper
@view
@external
def getUnderlyingYieldAmount() -> uint256:
```

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | USDC in yield position|

### `getAvailableUsdc`

Returns total available USDC (idle + yield).

```vyper
@view
@external
def getAvailableUsdc() -> uint256:
```

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | Total available USDC |

### `transferUsdcToEndaomentFunds`

Transfers USDC to EndaomentFunds vault.

```vyper
@external
def transferUsdcToEndaomentFunds(_amount: uint256) -> uint256:
```

#### Parameters

| Name      | Type      | Description          |
| --------- | --------- | -------------------- |
| `_amount` | `uint256` | USDC to transfer     |

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `uint256` | USDC transferred     |

#### Access

Only callable by valid Ripe addresses

## Configuration Functions (Switchboard Only)

### Mint Configuration

```vyper
@external
def setCanMint(_canMint: bool):

@external
def setMintFee(_fee: uint256):

@external
def setMaxIntervalMint(_maxGreenAmount: uint256):

@external
def setShouldEnforceMintAllowlist(_shouldEnforce: bool):

@external
def updateMintAllowlist(_user: address, _isAllowed: bool):
```

### Redeem Configuration

```vyper
@external
def setCanRedeem(_canRedeem: bool):

@external
def setRedeemFee(_fee: uint256):

@external
def setMaxIntervalRedeem(_maxGreenAmount: uint256):

@external
def setShouldEnforceRedeemAllowlist(_shouldEnforce: bool):

@external
def updateRedeemAllowlist(_user: address, _isAllowed: bool):
```

### General Configuration

```vyper
@external
def setUsdcYieldPosition(_legoId: uint256, _vaultToken: address):

@external
def setNumBlocksPerInterval(_blocks: uint256):

@external
def setShouldAutoDeposit(_shouldAutoDeposit: bool):
```

All configuration functions:
- Require Switchboard access
- Emit corresponding update events
- Validate inputs (no-change checks, range validation)

## Key Mathematical Functions

### GREEN Minting Calculation

```
usdcAfterFee = usdcIn - (usdcIn × mintFee / 100%)
usdValue = PriceDesk.getUsdValue(usdc, usdcAfterFee)
usdcInGreenDecimals = usdcAfterFee × 10^18 / 10^6
greenToMint = min(usdValue, usdcInGreenDecimals)
```

### GREEN Redemption Calculation

```
usdcFromPriceDesk = PriceDesk.getAssetAmount(usdc, greenAmount)
greenInUsdcDecimals = greenAmount × 10^6 / 10^18
usdcToGive = min(usdcFromPriceDesk, greenInUsdcDecimals)
usdcAfterFee = usdcToGive - (usdcToGive × redeemFee / 100%)
```

### Interval Capacity Calculation

```
# If current block is within interval
if intervalStart + numBlocksPerInterval > currentBlock:
    remainingCapacity = maxInterval - intervalAmount

# If interval expired
else:
    remainingCapacity = maxInterval (interval resets)
```

## Security Considerations

1. **Reentrancy Protection**: All state-changing functions use `@nonreentrant`
2. **Access Control**: Configuration functions restricted to Switchboard; yield operations to Ripe addresses
3. **Rate Limiting**: Block-based intervals prevent excessive volume attacks
4. **Underscore Bypass**: Special addresses bypass fees/limits but still respect USDC availability
5. **Fee Validation**: Fees capped at 100% (HUNDRED_PERCENT)
6. **Yield Position Safety**: Cannot change yield position while vault tokens exist
7. **Price Protection**: Uses min() of PriceDesk value and decimal conversion
8. **Pause Mechanism**: All functions respect `isPaused` flag
