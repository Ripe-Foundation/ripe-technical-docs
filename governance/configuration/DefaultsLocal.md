# DefaultsLocal

`DefaultsLocal` is the minimal [`Defaults`](../../interfaces/Defaults.md)
implementation used by local development and tests.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/DefaultsLocal.vy)

## Behavior

The contract has no constructor arguments. Most getters return an empty struct,
zero address, `False`, or an empty list, leaving policy domains unconfigured.
The Ledger budget getters return synthetic availability so tests can exercise
reward, contributor, and bond issuance paths.

`MissionControl` and `Ledger` copy these returns during construction. The
Defaults contract is not consulted for later reads.

## Getter surface

The contract implements every Defaults getter so it can be substituted in
constructor tests without a separate mock interface. The exact return shapes
are listed below.

<!-- BEGIN GENERATED API REFERENCE: DefaultsLocal -->
## Exact API reference

> Generated from `contracts/config/DefaultsLocal.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor()`

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `assetConfigs()` | `view` | `(address,(uint256[],uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,uint256,(bool,uint256,uint256,uint256,uint256),address,bool))[]` |
| `genConfig()` | `view` | `(uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool)` |
| `genDebtConfig()` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256,(bool,uint256,uint256,uint256,uint256))` |
| `hrConfig()` | `view` | `(address,uint256,uint256,uint256,uint256,uint256)` |
| `liteSigners()` | `view` | `address[]` |
| `priorityLiqAssetVaults()` | `view` | `(uint256,address)[]` |
| `priorityPriceSourceIds()` | `view` | `uint256[]` |
| `priorityStabVaults()` | `view` | `(uint256,address)[]` |
| `rewardsConfig()` | `view` | `(bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `ripeAvailForBonds()` | `view` | `uint256` |
| `ripeAvailForHr()` | `view` | `uint256` |
| `ripeAvailForRewards()` | `view` | `uint256` |
| `ripeBondConfig()` | `view` | `(address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256)` |
| `ripeGovVaultConfigs()` | `view` | `(address,((uint256,uint256,uint256,bool,uint256),uint256,bool))[]` |
| `shouldCheckLastTouch()` | `view` | `bool` |
| `trainingWheels()` | `view` | `address` |
| `underscoreRegistry()` | `view` | `address` |

<!-- END GENERATED API REFERENCE: DefaultsLocal -->
