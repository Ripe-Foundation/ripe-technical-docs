# EndaomentFunds Technical Documentation

[View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/core/EndaomentFunds.vy)

## Overview

EndaomentFunds is a secure custodial vault for protocol-owned funds in Ripe Protocol. It serves as a minimal-permission holding contract that receives assets from deleveraging and redemption operations, with funds only withdrawable by the Endaoment contract.

**Core Functions**:
- **Asset Custody**: Securely holds ERC20 tokens and ETH for the protocol
- **Controlled Withdrawals**: Only the Endaoment contract can withdraw funds
- **Balance Checking**: Simple view function to check holdings

The contract is intentionally minimal to reduce attack surface. It receives assets from [Deleverage](../core-lending/Deleverage.md) operations and [CreditRedeem](../core-lending/CreditRedeem.md) flows, acting as an intermediary before funds are processed by [Endaoment](./Endaoment.md).

## Architecture & Modules

EndaomentFunds uses a streamlined architecture:

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Key Features**:
  - Access to Endaoment contract address
  - Validation of caller permissions
- **Exported Interface**: Address utilities via `addys.__interface__`

### Module Initialization

```vyper
initializes: addys
```

## System Architecture Diagram

```
+------------------------------------------------------------------------+
|                       EndaomentFunds Contract                           |
+------------------------------------------------------------------------+
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Asset Custody                                  |  |
|  |                                                                  |  |
|  |  * Holds ERC20 tokens from deleverage operations                 |  |
|  |  * Holds ETH from protocol operations                            |  |
|  |  * Receives assets from CreditRedeem flows                       |  |
|  |  * Acts as secure staging area for protocol treasury             |  |
|  +------------------------------------------------------------------+  |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                    Access Control                                 |  |
|  |                                                                  |  |
|  |  ONLY Endaoment contract can call transfer()                     |  |
|  |  Anyone can receive ETH (payable __default__)                    |  |
|  |  Anyone can check balances (hasBalance view)                     |  |
|  +------------------------------------------------------------------+  |
+------------------------------------------------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+------------------+    +-------------------+    +------------------+
| Deleverage       |    | CreditRedeem      |    | Endaoment        |
| * Sends assets   |    | * Sends assets    |    | * Withdraws      |
| * During delev   |    | * During redeem   |    | * For treasury   |
+------------------+    +-------------------+    +------------------+
```

## Events

### EndaomentFundsMoved

Emitted when funds are transferred out to Endaoment:

```vyper
event EndaomentFundsMoved:
    token: indexed(address)     # Token address (empty for ETH)
    to: indexed(address)        # Recipient (always Endaoment)
    amount: uint256             # Amount transferred
```

## State Variables

### Constants

- `API_VERSION: String[28] = "0.1.0"` - Contract version

## Constructor

### `__init__`

Initializes EndaomentFunds with minimal setup.

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
# Deploy EndaomentFunds
endaoment_funds = boa.load(
    "contracts/core/EndaomentFunds.vy",
    ripe_hq.address
)
```

## Functions

### `__default__`

Payable fallback function that allows the contract to receive ETH.

```vyper
@payable
@external
def __default__():
    pass
```

#### Access

Public - anyone can send ETH to this contract

### `hasBalance`

Checks if the contract has a balance of the specified asset.

```vyper
@view
@external
def hasBalance(_asset: address = empty(address)) -> bool:
```

#### Parameters

| Name     | Type      | Description                        |
| -------- | --------- | ---------------------------------- |
| `_asset` | `address` | Token address (empty for ETH)      |

#### Returns

| Type   | Description                      |
| ------ | -------------------------------- |
| `bool` | True if contract has balance > 0 |

#### Access

Public view function

#### Example Usage

```python
# Check ETH balance
has_eth = endaoment_funds.hasBalance()

# Check USDC balance
has_usdc = endaoment_funds.hasBalance(usdc.address)
```

### `transfer`

Transfers funds to the Endaoment contract. Only callable by Endaoment.

```vyper
@external
def transfer(
    _asset: address = empty(address),
    _amount: uint256 = max_value(uint256)
) -> uint256:
```

#### Parameters

| Name      | Type      | Description                        |
| --------- | --------- | ---------------------------------- |
| `_asset`  | `address` | Token address (empty for ETH)      |
| `_amount` | `uint256` | Amount to transfer (max=all)       |

#### Returns

| Type      | Description              |
| --------- | ------------------------ |
| `uint256` | Actual amount transferred|

#### Access

Only callable by Endaoment contract

#### Events Emitted

- `EndaomentFundsMoved` - Transfer details

#### Example Usage

```python
# Transfer all USDC to Endaoment
amount = endaoment_funds.transfer(
    usdc.address,
    sender=endaoment.address
)

# Transfer specific amount of ETH
amount = endaoment_funds.transfer(
    empty(address),  # ETH
    1e18,            # 1 ETH
    sender=endaoment.address
)
```

#### Behavior

1. Validates caller is Endaoment contract
2. Calculates actual amount (min of requested and balance)
3. Asserts amount is non-zero
4. Transfers to Endaoment:
   - ERC20: Uses `transfer()` with default return value handling
   - ETH: Uses `send()`
5. Emits `EndaomentFundsMoved` event
6. Returns actual amount transferred

## Security Considerations

1. **Minimal Attack Surface**: Contract has only 2 external functions
2. **Strict Access Control**: Only Endaoment can withdraw funds
3. **Graceful Balance Handling**: Transfer caps at actual balance
4. **ETH Reception**: Payable fallback allows ETH deposits from any source
5. **No State Manipulation**: No complex state that could be exploited
6. **Default Return Value**: Handles tokens that don't return bool on transfer

## Integration Points

### Receives Assets From:
- **Deleverage**: Assets transferred during user deleverage operations
- **CreditRedeem**: Assets transferred during collateral redemption
- **EndaomentPSM**: USDC transfers from PSM yield operations
- **Direct Transfers**: Any address can send ERC20 or ETH

### Sends Assets To:
- **Endaoment**: The only authorized recipient

## Testing

For comprehensive test examples, see: [`tests/core/test_endaoment_funds.py`](../../tests/core/test_endaoment_funds.py)
