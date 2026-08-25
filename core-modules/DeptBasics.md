# DeptBasics

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/modules/DeptBasics.vy)

`DeptBasics` is the shared Department module for pause state, immutable minting
capability declarations, and recovery of accidentally held ERC-20 balances.
It implements the standard [`Department`](../interfaces/Department.md)
interface and is initialized inside a host contract.

## Immutable capabilities

The constructor records `CAN_MINT_GREEN` and `CAN_MINT_RIPE`. The public
`canMintGreen()` and `canMintRipe()` views report those declarations; they do
not themselves grant minting authority. Root authorization also requires the
current `RipeHq` registry entry, the corresponding `HqConfig` permission, and
the global minting enable flag.

## Pause behavior

`pause(shouldPause)` may be called only by a currently registered Switchboard
configuration contract and rejects no-op changes. The module stores and emits
pause state, but it does not automatically guard every host function. Each host
must explicitly include `isPaused` in the operations that pause is intended to
block.

## Fund recovery

Only a registered Switchboard configuration contract may recover funds.

- `recoverFunds` transfers the host's full balance of one ERC-20.
- `recoverFundsMany` applies the same operation to at most 20 assets.
- Recipient and asset must be nonzero, the balance must be nonzero, and the
  token transfer must return `true` or return no data. An explicit `false`
  return or a revert fails recovery.

Recovery does not check the host's pause flag and therefore remains callable
while the host is paused. A many-asset recovery is one atomic transaction: if
any balance lookup or transfer fails, all earlier transfers and events in that
batch are reverted.

Recovery is a privileged escape hatch, not an accounting-aware withdrawal.
Contracts whose token balances represent user or protocol liabilities may
override, restrict, or deliberately disable it.

## Security properties

- Minting capabilities cannot be changed after construction.
- Pause and recovery authority follows the current Switchboard registry, not a
  hardcoded operator address.
- A removed or replaced Switchboard configuration address immediately loses
  these module-level permissions.

<!-- BEGIN GENERATED API REFERENCE: DeptBasics -->
## Exact source-declared API reference

> Generated from declarations in `contracts/modules/DeptBasics.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers deployment/module initializers, external functions and their default-argument call forms, compiler-generated public getters inferred from declarations, events, flags, constants, structs, and source-declared revert reasons found in this source. It does not claim a composed host ABI or canonical runtime selector surface.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__(_shouldPause: bool, _canMintGreen: bool, _canMintRipe: bool)`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def canMintGreen() -> bool` | `0` | `view` | `bool` |
| `def canMintRipe() -> bool` | `0` | `view` | `bool` |
| `def pause(_shouldPause: bool)` | `1` | `nonpayable` | — |
| `def recoverFunds(_recipient: address, _asset: address)` | `2` | `nonpayable` | — |
| `def recoverFundsMany(_recipient: address, _assets: DynArray[address, MAX_RECOVER_ASSETS])` | `2` | `nonpayable` | — |

### Source-declared call forms

Each row is one source-level call form permitted by the declaration's trailing defaults. These signatures use Vyper source notation; they are not canonical ABI signatures or selector-hash preimages. Without a tracked compiled ABI, this table does not claim the exact runtime selector surface.

| Source call form | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, DynArray[address, MAX_RECOVER_ASSETS] _assets)` | `nonpayable` | — |

### Compiler-generated public getters

| Getter | Mutability | Source return type |
| --- | --- | --- |
| `isPaused()` | `view` | `bool` |

### Events declared by this source

- `DepartmentPauseModified(isPaused: bool)`
- `DepartmentFundsRecovered(asset: indexed(address), recipient: indexed(address), balance: uint256)`

### Constants declared by this source

- `MAX_RECOVER_ASSETS: uint256 = 20`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid recipient or asset`
- `no change`
- `no perms`
- `nothing to recover`
- `recovery failed`

<!-- END GENERATED API REFERENCE: DeptBasics -->
