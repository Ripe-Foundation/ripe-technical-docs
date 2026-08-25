# DefaultsBaseLive

`DefaultsBaseLive` is a generated implementation of the
[`Defaults`](../../interfaces/Defaults.md) interface. `MissionControl` and
`Ledger` can read it during construction and copy the returned configuration
into storage.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/DefaultsBaseLive.vy)

## Construction and getter domains

The contract has no constructor arguments. Its getters cover the same general,
debt, budget, bond, rewards, RipeGov, HR, asset, priority-route, price-source,
Underscore, TrainingWheels, last-touch, and lite-signer domains defined by the
Defaults interface.

The values are read only during construction. The Defaults contract is not a
dependency used for later `MissionControl` or `Ledger` reads.

## Interface limits

The Defaults interface has no slots for MissionControl's per-user `userConfig`
or `userDelegation`, current `coreRipeGovVaultId` or `preferredStabVaultId`
pointers, or historical `isRipeGovVaultId` and `isStabVaultId` entries. Those
state domains are therefore outside every Defaults implementation's getter
surface.

<!-- BEGIN GENERATED API REFERENCE: DefaultsBaseLive -->
## Exact API reference

> Generated from `contracts/config/DefaultsBaseLive.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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

<!-- END GENERATED API REFERENCE: DefaultsBaseLive -->
