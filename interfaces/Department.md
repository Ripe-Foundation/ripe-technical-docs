# Department interface

`Department.vyi` is the common control surface expected from protocol
Departments that use `DeptBasics` or provide equivalent behavior.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/Department.vyi)

## Capability views

`canMintGreen()` and `canMintRipe()` report whether the implementation declares
the corresponding immutable capability. They do not grant mint authority on
their own. RipeHq also requires current registry membership, the matching
`HqConfig` permission, and an enabled global mint circuit breaker.

## Pause and recovery surface

The interface standardizes:

- `isPaused()`;
- `pause(shouldPause)`;
- recovery of one ERC-20 balance; and
- recovery of up to 20 ERC-20 balances.

The interface does not specify which functions a host must block while paused,
who may call recovery, or whether recovery is safe for funds represented in the
host's accounting. Current `DeptBasics` implementations authorize registered
Switchboard contracts, while specialized hosts may add restrictions or disable
recovery.

## Integration rule

RipeHq probes the minting views when granting and checking Department
permissions. A replacement at a mint-enabled registry ID must therefore retain
the expected interface and capability; callable shape alone does not preserve
economic or custody semantics.

<!-- BEGIN GENERATED API REFERENCE: Department -->
## Exact API reference

> Generated from declarations in `interfaces/Department.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def canMintGreen() -> bool`
- `def canMintRipe() -> bool`
- `def isPaused() -> bool`
- `def pause(_shouldPause: bool)`
- `def recoverFunds(_recipient: address, _asset: address)`
- `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])`

<!-- END GENERATED API REFERENCE: Department -->
