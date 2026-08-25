# Defaults interface

`Defaults.vyi` defines the configuration snapshot consumed by MissionControl
and Ledger constructors.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/Defaults.vyi)

## Getter groups

The interface returns:

- `genConfig` and `genDebtConfig`;
- RIPE availability for rewards, HR, and bonds;
- bond, rewards, RipeGov, and HR configuration;
- Underscore registry, TrainingWheels, and last-touch policy;
- up to 50 asset configurations;
- up to 20 priority liquidation and StabilityPool routes;
- up to 10 priority price source IDs; and
- up to 10 lite signers.

Shared tuple types come from [`ConfigStructs`](ConfigStructs.md).

## Copy semantics

Defaults is not a dependency after construction. MissionControl and Ledger read
the getters and copy returned values into their own storage. Later changes to
that stored configuration do not mutate the Defaults implementation.

The interface has no getters for MissionControl's per-user `userConfig` or
`userDelegation`, current `coreRipeGovVaultId` or `preferredStabVaultId`
pointers, or historical `isRipeGovVaultId` and `isStabVaultId` entries.
Those state domains are therefore outside every implementation of this
interface and must be handled through their dedicated MissionControl APIs.

## Implementations and roles

| Page | Intended role |
| --- | --- |
| [`DefaultsBase`](../governance/configuration/DefaultsBase.md) | Constructor configuration profile with no constructor arguments |
| [`DefaultsBaseLive`](../governance/configuration/DefaultsBaseLive.md) | Generated configuration profile with no constructor arguments |
| [`DefaultsRobinhood`](../governance/configuration/DefaultsRobinhood.md) | Configuration profile with constructor-bound component addresses |
| [`DefaultsRobinhoodLive`](../governance/configuration/DefaultsRobinhoodLive.md) | Generated configuration profile with a constructor-bound Contributor template |
| [`DefaultsLocal`](../governance/configuration/DefaultsLocal.md) | Local development/test profile |

<!-- BEGIN GENERATED API REFERENCE: Defaults -->
## Exact API reference

> Generated from declarations in `interfaces/Defaults.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def assetConfigs() -> DynArray[cs.AssetConfigEntry, 50]`
- `def genConfig() -> cs.GenConfig`
- `def genDebtConfig() -> cs.GenDebtConfig`
- `def hrConfig() -> cs.HrConfig`
- `def liteSigners() -> DynArray[address, 10]`
- `def priorityLiqAssetVaults() -> DynArray[cs.VaultLite, 20]`
- `def priorityPriceSourceIds() -> DynArray[uint256, 10]`
- `def priorityStabVaults() -> DynArray[cs.VaultLite, 20]`
- `def rewardsConfig() -> cs.RipeRewardsConfig`
- `def ripeAvailForBonds() -> uint256`
- `def ripeAvailForHr() -> uint256`
- `def ripeAvailForRewards() -> uint256`
- `def ripeBondConfig() -> cs.RipeBondConfig`
- `def ripeGovVaultConfigs() -> DynArray[cs.RipeGovVaultConfigEntry, 5]`
- `def shouldCheckLastTouch() -> bool`
- `def trainingWheels() -> address`
- `def underscoreRegistry() -> address`

<!-- END GENERATED API REFERENCE: Defaults -->
