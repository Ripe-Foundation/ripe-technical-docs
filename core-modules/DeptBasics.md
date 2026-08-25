# DeptBasics

`DeptBasics` is the shared Department module for pause state, immutable minting
capability declarations, and recovery of accidentally held ERC-20 balances.
It implements the standard [`Department`](../interfaces/Department.md)
interface and is initialized inside a host contract.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/modules/DeptBasics.vy)

## Immutable capabilities

The constructor records `CAN_MINT_GREEN` and `CAN_MINT_RIPE`. The public
`canMintGreen()` and `canMintRipe()` views report those declarations; they do
not themselves grant minting authority. Root authorization also requires the
current `RipeHq` registry entry, the corresponding `HqConfig` permission, and
the global minting circuit breaker.

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
  token transfer must report success.

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
## Exact API reference

> Generated from declarations in `contracts/modules/DeptBasics.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def canMintGreen() -> bool`
- `def canMintRipe() -> bool`
- `def pause(_shouldPause: bool)`
- `def recoverFunds(_recipient: address, _asset: address)`
- `def recoverFundsMany(_recipient: address, _assets: DynArray[address, MAX_RECOVER_ASSETS])`

### Events declared by this source

- `DepartmentPauseModified(isPaused: bool)`
- `DepartmentFundsRecovered(asset: indexed(address), recipient: indexed(address), balance: uint256)`

<!-- END GENERATED API REFERENCE: DeptBasics -->
