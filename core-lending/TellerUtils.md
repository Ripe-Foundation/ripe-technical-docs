# TellerUtils Technical Documentation

[View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/TellerUtils.vy)

## Overview

TellerUtils is a utility contract that provides validation logic for deposits and withdrawals in Ripe Protocol, as well as underscore protocol integration checks. It separates complex validation logic from the main [Teller](./Teller.md) contract for better code organization and gas optimization.

**Core Functions**:
- **Deposit Validation**: Validates deposit requests against protocol limits and permissions
- **Withdrawal Validation**: Validates withdrawal requests including debt health checks
- **Vault Resolution**: Resolves vault addresses and IDs from various inputs
- **Underscore Integration**: Checks for underscore wallet/vault ownership and permissions

## Architecture & Modules

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Exported Interface**: Address utilities via `addys.__interface__`

### DeptBasics Module

- **Location**: `contracts/modules/DeptBasics.vy`
- **Purpose**: Provides department-level functionality
- **Documentation**: See [DeptBasics Technical Documentation](../shared-modules/DeptBasics.md)
- **Exported Interface**: Department basics via `deptBasics.__interface__`

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                        TellerUtils Contract                             |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Deposit Validation                             |  |
|  |                                                                  |  |
|  |  * Protocol/asset deposit toggles                                |  |
|  |  * Vault support for asset                                        |  |
|  |  * User allowlist check                                           |  |
|  |  * Per-user and global deposit limits                            |  |
|  |  * Max vaults and assets per vault limits                        |  |
|  |  * Minimum deposit balance                                        |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Withdrawal Validation                          |  |
|  |                                                                  |  |
|  |  * Protocol/asset withdrawal toggles                             |  |
|  |  * User allowlist check                                           |  |
|  |  * Caller permission to withdraw for user                        |  |
|  |  * Maximum withdrawable based on debt health                     |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Underscore Integration                         |  |
|  |                                                                  |  |
|  |  * Check if address is underscore wallet                         |  |
|  |  * Check if address is underscore vault                          |  |
|  |  * Check if caller is underscore wallet owner                    |  |
|  |  * Check if address is underscore lego                           |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| MissionControl   |    | CreditEngine      |    | Underscore       |
| * Deposit config |    | * Max withdraw    |    | * Ledger         |
| * Vault config   |    | * Debt health     |    | * Vault Registry |
+------------------+    +-------------------+    +------------------+
```

## Data Structures

### DepositLedgerData Struct

Data from Ledger for deposit validation:

```vyper
struct DepositLedgerData:
    isParticipatingInVault: bool  # User already has position in vault
    numUserVaults: uint256        # Total number of user's vaults
```

### TellerDepositConfig Struct

Configuration for deposit validation:

```vyper
struct TellerDepositConfig:
    canDepositGeneral: bool           # Global deposit toggle
    canDepositAsset: bool             # Asset-specific deposit toggle
    doesVaultSupportAsset: bool       # Vault supports this asset
    isUserAllowed: bool               # User on allowlist
    perUserDepositLimit: uint256      # Per-user deposit cap
    globalDepositLimit: uint256       # Global deposit cap
    perUserMaxAssetsPerVault: uint256 # Max assets per vault
    perUserMaxVaults: uint256         # Max vaults per user
    canAnyoneDeposit: bool            # Anyone can deposit for others
    minDepositBalance: uint256        # Minimum balance required
```

### TellerWithdrawConfig Struct

Configuration for withdrawal validation:

```vyper
struct TellerWithdrawConfig:
    canWithdrawGeneral: bool    # Global withdrawal toggle
    canWithdrawAsset: bool      # Asset-specific withdrawal toggle
    isUserAllowed: bool         # User on allowlist
    canWithdrawForUser: bool    # Can caller withdraw for user
    minDepositBalance: uint256  # Minimum balance to maintain
```

## State Variables

### Constants

- `UNDERSCORE_LEDGER_ID: uint256 = 1` - Registry ID for underscore ledger
- `UNDERSCORE_LEGOBOOK_ID: uint256 = 3` - Registry ID for underscore lego book
- `UNDERSCORE_VAULT_REGISTRY_ID: uint256 = 10` - Registry ID for underscore vault registry

## Constructor

### `__init__`

Initializes TellerUtils without minting permissions.

```vyper
@deploy
def __init__(_ripeHq: address):
```

#### Parameters

| Name      | Type      | Description             |
| --------- | --------- | ----------------------- |
| `_ripeHq` | `address` | RipeHq contract address |

## Deposit Validation

### `validateOnDeposit`

Validates a deposit request and returns the allowed amount.

```vyper
@view
@external
def validateOnDeposit(
    _asset: address,
    _amount: uint256,
    _user: address,
    _vaultId: uint256,
    _vaultAddr: address,
    _depositor: address,
    _didAlreadyValidateSender: bool,
    _areFundsHereAlready: bool,
    _d: DepositLedgerData,
    _a: addys.Addys = empty(addys.Addys),
) -> uint256:
```

#### Parameters

| Name                       | Type               | Description                          |
| -------------------------- | ------------------ | ------------------------------------ |
| `_asset`                   | `address`          | Asset to deposit                     |
| `_amount`                  | `uint256`          | Requested deposit amount             |
| `_user`                    | `address`          | User to deposit for                  |
| `_vaultId`                 | `uint256`          | Target vault ID                      |
| `_vaultAddr`               | `address`          | Target vault address                 |
| `_depositor`               | `address`          | Address initiating deposit           |
| `_didAlreadyValidateSender`| `bool`             | Skip sender validation               |
| `_areFundsHereAlready`     | `bool`             | Funds already at Teller              |
| `_d`                       | `DepositLedgerData`| Ledger data for user                 |
| `_a`                       | `addys.Addys`      | Cached addresses (optional)          |

#### Returns

| Type      | Description                  |
| --------- | ---------------------------- |
| `uint256` | Validated deposit amount     |

#### Validation Steps

1. Check protocol deposits enabled
2. Check asset deposits enabled
3. Check vault supports asset
4. Check user is allowed
5. Verify depositor can deposit for user (unless Ripe dept or underscore owner)
6. Check available balance
7. For non-Ripe departments:
   - Verify max vaults limit
   - Verify max assets per vault limit
   - Check per-user deposit limit
   - Check global deposit limit
   - Verify minimum balance requirement

## Withdrawal Validation

### `validateOnWithdrawal`

Validates a withdrawal request and returns the allowed amount.

```vyper
@view
@external
def validateOnWithdrawal(
    _asset: address,
    _amount: uint256,
    _user: address,
    _vaultAddr: address,
    _vaultId: uint256,
    _caller: address,
    _config: TellerWithdrawConfig,
    _a: addys.Addys = empty(addys.Addys),
) -> uint256:
```

#### Parameters

| Name       | Type                  | Description                     |
| ---------- | --------------------- | ------------------------------- |
| `_asset`   | `address`             | Asset to withdraw               |
| `_amount`  | `uint256`             | Requested withdrawal amount     |
| `_user`    | `address`             | User withdrawing                |
| `_vaultAddr`| `address`            | Vault address                   |
| `_vaultId` | `uint256`             | Vault ID                        |
| `_caller`  | `address`             | Caller address                  |
| `_config`  | `TellerWithdrawConfig`| Withdrawal configuration        |
| `_a`       | `addys.Addys`         | Cached addresses (optional)     |

#### Returns

| Type      | Description                    |
| --------- | ------------------------------ |
| `uint256` | Validated withdrawal amount    |

#### Validation Steps

1. Check amount is non-zero
2. Check protocol withdrawals enabled
3. Check asset withdrawals enabled
4. Check user is allowed
5. Verify caller can withdraw for user (if not same address)
6. Get max withdrawable from CreditEngine (respects debt health)
7. Return minimum of requested and max withdrawable

## Vault Resolution

### `getVaultAddrAndId`

Resolves vault address and ID from various inputs.

```vyper
@view
@external
def getVaultAddrAndId(
    _asset: address,
    _vaultAddr: address,
    _vaultId: uint256,
    _vaultBook: address,
    _missionControl: address,
) -> (address, uint256):
```

#### Parameters

| Name              | Type      | Description                    |
| ----------------- | --------- | ------------------------------ |
| `_asset`          | `address` | Asset address                  |
| `_vaultAddr`      | `address` | Vault address (optional)       |
| `_vaultId`        | `uint256` | Vault ID (optional)            |
| `_vaultBook`      | `address` | VaultBook registry address     |
| `_missionControl` | `address` | MissionControl address         |

#### Returns

| Type      | Description          |
| --------- | -------------------- |
| `address` | Resolved vault address|
| `uint256` | Resolved vault ID    |

#### Resolution Logic

1. If neither vault address nor ID provided: Get first vault for asset from MissionControl
2. If vault ID provided: Look up address from VaultBook
3. If vault address provided: Look up ID from VaultBook
4. Validates consistency if both provided

## Underscore Integration Functions

### `isUnderscoreWalletOrVault`

Checks if an address is an underscore wallet or vault.

```vyper
@view
@external
def isUnderscoreWalletOrVault(_addr: address, _mc: address = empty(address)) -> bool:
```

### `isUnderscoreWallet`

Checks if an address is an underscore wallet.

```vyper
@view
@external
def isUnderscoreWallet(_user: address, _mc: address = empty(address)) -> bool:
```

### `isUnderscoreVault`

Checks if an address is an underscore earn vault.

```vyper
@view
@external
def isUnderscoreVault(_user: address, _mc: address = empty(address)) -> bool:
```

### `isUnderscoreWalletOwner`

Checks if a caller is the owner of an underscore wallet.

```vyper
@view
@external
def isUnderscoreWalletOwner(_user: address, _caller: address, _mc: address = empty(address)) -> bool:
```

#### Logic

1. Verify user is an underscore wallet
2. Get wallet config from wallet
3. Check if caller matches owner in wallet config

### `isUnderscoreAddr`

Checks if an address is in the underscore registry or is an underscore lego.

```vyper
@view
@external
def isUnderscoreAddr(_addr: address, _mc: address = empty(address)) -> bool:
```

### `isUnderscoreOwnerOrLego`

Checks if caller is either the underscore wallet owner or an underscore lego.

```vyper
@view
@external
def isUnderscoreOwnerOrLego(_user: address, _caller: address, _mc: address = empty(address)) -> bool:
```

## Security Considerations

1. **Access Control**: Validation functions enforce protocol permissions
2. **Deposit Limits**: Multiple layers of limits (per-user, global, vault-specific)
3. **Withdrawal Protection**: Respects debt health via CreditEngine
4. **Underscore Integration**: Proper validation of underscore wallet ownership
5. **Trusted Deposits**: Ripe departments bypass user limits
6. **Pause Respect**: Inherits pause mechanism from DeptBasics

## Testing

For comprehensive test examples, see: [`tests/core/test_teller_utils.py`](../../tests/core/test_teller_utils.py)
