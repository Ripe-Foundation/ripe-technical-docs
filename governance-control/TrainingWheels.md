# TrainingWheels Technical Documentation

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/master/contracts/config/TrainingWheels.vy)

## Overview

TrainingWheels is an access control contract that manages a whitelist of allowed users in Ripe Protocol. It provides a simple allowlist mechanism that can be used to restrict access to certain protocol features during early deployment phases or for specific user groups.

**Core Features**:
- **User Allowlist**: Maintains a mapping of allowed user addresses
- **Switchboard Access**: Only Switchboard-registered contracts can modify the allowlist
- **Batch Initialization**: Supports setting initial allowed users at deployment
- **Whitelist Compatibility**: Interface compatible with other whitelist contracts

## Architecture & Modules

TrainingWheels uses a standard department architecture:

### Addys Module

- **Location**: `contracts/modules/Addys.vy`
- **Purpose**: Provides protocol-wide address resolution and validation
- **Documentation**: See [Addys Technical Documentation](../shared-modules/Addys.md)
- **Exported Interface**: Address utilities via `addys.__interface__`

### DeptBasics Module

- **Location**: `contracts/modules/DeptBasics.vy`
- **Purpose**: Provides department-level basic functionality
- **Documentation**: See [DeptBasics Technical Documentation](../shared-modules/DeptBasics.md)
- **Key Features**:
  - Pause mechanism
  - Department interface compliance
  - No minting capabilities
- **Exported Interface**: Department basics via `deptBasics.__interface__`

### Module Initialization

```vyper
initializes: addys
initializes: deptBasics[addys := addys]
```

## Events

### TrainingWheelsModified

Emitted when a user's allowlist status changes:

```vyper
event TrainingWheelsModified:
    user: indexed(address)     # User address modified
    shouldAllow: bool          # New allowlist status
```

## State Variables

### Public Variables

- `allowed: HashMap[address, bool]` - Maps user addresses to their allowlist status

### Constants

- `MAX_INITIAL: uint256 = 20` - Maximum users that can be set in initial list

## Constructor

### `__init__`

Initializes TrainingWheels with optional initial allowlist.

```vyper
@deploy
def __init__(_ripeHq: address, _initialList: DynArray[address, MAX_INITIAL]):
```

#### Parameters

| Name           | Type                              | Description                    |
| -------------- | --------------------------------- | ------------------------------ |
| `_ripeHq`      | `address`                         | RipeHq contract address        |
| `_initialList` | `DynArray[address, MAX_INITIAL]`  | Initial list of allowed users  |

#### Behavior

1. Initializes Addys with RipeHq address
2. Initializes DeptBasics with no minting capabilities
3. Iterates through initial list and sets each address as allowed
4. Emits `TrainingWheelsModified` for each initialized user
5. Skips empty addresses in the initial list

#### Example Usage

```python
# Deploy with initial allowed users
initial_users = [user1.address, user2.address, user3.address]
training_wheels = boa.load(
    "contracts/config/TrainingWheels.vy",
    ripe_hq.address,
    initial_users
)

# Deploy with empty initial list
training_wheels = boa.load(
    "contracts/config/TrainingWheels.vy",
    ripe_hq.address,
    []
)
```

## Functions

### `setAllowed`

Updates a user's allowlist status.

```vyper
@external
def setAllowed(_user: address, _shouldAllow: bool):
```

#### Parameters

| Name           | Type      | Description                          |
| -------------- | --------- | ------------------------------------ |
| `_user`        | `address` | User address to update               |
| `_shouldAllow` | `bool`    | Whether user should be allowed       |

#### Access

Only callable by Switchboard-registered contracts

#### Events Emitted

- `TrainingWheelsModified` - Contains user and new status

#### Example Usage

```python
# Allow a user
training_wheels.setAllowed(
    new_user.address,
    True,
    sender=switchboard_config.address
)

# Revoke access
training_wheels.setAllowed(
    revoked_user.address,
    False,
    sender=switchboard_config.address
)
```

### `isUserAllowed`

Checks if a user is on the allowlist.

```vyper
@view
@external
def isUserAllowed(_user: address, _asset: address) -> bool:
```

#### Parameters

| Name     | Type      | Description                                    |
| -------- | --------- | ---------------------------------------------- |
| `_user`  | `address` | User address to check                          |
| `_asset` | `address` | Asset parameter (unused, for interface compat) |

#### Returns

| Type   | Description                    |
| ------ | ------------------------------ |
| `bool` | True if user is on allowlist   |

#### Notes

- The `_asset` parameter is included for interface compatibility with other whitelist contracts but is not used in this implementation
- Returns `False` for any user not explicitly added to the allowlist

#### Example Usage

```python
# Check if user is allowed
is_allowed = training_wheels.isUserAllowed(user.address, empty(address))
```

## Use Cases

### Early Access Control

TrainingWheels can restrict protocol features to approved users during:
- Beta testing phases
- Gradual rollouts
- VIP access programs

### Integration Pattern

Other contracts can use TrainingWheels for access checks:

```vyper
interface TrainingWheels:
    def isUserAllowed(_user: address, _asset: address) -> bool: view

# In some protocol contract
def someRestrictedFunction():
    tw: TrainingWheels = TrainingWheels(training_wheels_addr)
    assert staticcall tw.isUserAllowed(msg.sender, empty(address))
    # ... perform restricted action
```

## Security Considerations

1. **Switchboard Only**: Only Switchboard-authorized contracts can modify the allowlist
2. **Non-Zero Address**: Prevents setting allowlist status for zero address
3. **No Minting**: Department has no token minting capabilities
4. **Event Logging**: All changes are logged for transparency and auditing
5. **Simple Logic**: Minimal attack surface with straightforward boolean mapping
