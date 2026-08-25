# Department interface

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/interfaces/Department.vyi)

`Department.vyi` is the common control surface expected from protocol
Departments that use `DeptBasics` or provide equivalent behavior.

## Capability views

`canMintGreen()` and `canMintRipe()` report whether the implementation declares
the corresponding immutable capability. They do not grant mint authority on
their own. RipeHq also requires current registry membership, the matching
`HqConfig` permission, and the global minting-enable flag to be `true`.

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
## Exact source-declared API reference

> Generated from declarations in `interfaces/Department.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def canMintGreen() -> bool` | `0` | `view` | `bool` |
| `def canMintRipe() -> bool` | `0` | `view` | `bool` |
| `def isPaused() -> bool` | `0` | `view` | `bool` |
| `def pause(_shouldPause: bool)` | `1` | `nonpayable` | — |
| `def recoverFunds(_recipient: address, _asset: address)` | `2` | `nonpayable` | — |
| `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])` | `2` | `nonpayable` | — |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, DynArray[address, 20] _assets)` | `nonpayable` | — |

<!-- END GENERATED API REFERENCE: Department -->
