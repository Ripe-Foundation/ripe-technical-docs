# Defaults interface

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/interfaces/Defaults.vyi)

`Defaults.vyi` defines the configuration snapshot consumed by MissionControl
and Ledger constructors.

## Getter groups

The interface returns:

- `genConfig` and `genDebtConfig`;
- RIPE availability for rewards, HR, and bonds;
- bond, rewards, RipeGov, and HR configuration;
- Underscore registry, TrainingWheels, and last-touch policy;
- up to 5 RipeGov vault configurations;
- up to 50 asset configurations;
- up to 20 priority liquidation and StabilityPool routes;
- up to 10 priority price source IDs; and
- up to 10 lite signers.

Shared tuple types come from [`ConfigStructs`](ConfigStructs.md).

## Shared units

Percentage and ratio fields use basis points (`100_00 == 100%`).
`priceStaleTime` and HR cliff, start-delay, and vesting fields are seconds.
Debt intervals, auction terms, bond epochs, and governance-vault lock terms are
generally `block.number` deltas. Ledger's action-block source is a separate
constructor dependency. Token and USD quantities retain the decimals of their
consuming field; Defaults does not impose one universal amount scale.

## Copy semantics

Defaults is not a dependency after construction. MissionControl and Ledger read
the getters and copy returned values into their own storage. Later changes to
that stored configuration do not mutate the Defaults implementation.

The interface has no getters for MissionControl's per-user `userConfig` or
`userDelegation`, current `coreRipeGovVaultId` or `preferredStabVaultId`
pointers, or historical `isRipeGovVaultId` and `isStabVaultId` entries.
Those state domains are therefore outside every implementation of this
interface. A replacement MissionControl starts with constructor pointer
defaults (preferred StabilityPool ID 1 and core RipeGov ID 2), not the replaced
contract's current pointers. Known user settings and pointers can be rebuilt
individually through Teller or Switchboard routes. Historical role flags change
only as side effects of the available configuration setters; there is no direct
arbitrary bulk history import.

## Implementations and roles

The Base and Robinhood names identify chain-targeted source-profile families
with different chain clocks, dependency sets, and asset universes. They do not
describe current deployment status or live parameter values.

| Page | Intended role |
| --- | --- |
| [`DefaultsBase`](../governance/configuration/DefaultsBase.md) | Seed profile for newly constructed consumers; no constructor arguments |
| [`DefaultsBaseLive`](../governance/configuration/DefaultsBaseLive.md) | Generated replacement seed for existing consumer state; no constructor arguments |
| [`DefaultsRobinhood`](../governance/configuration/DefaultsRobinhood.md) | Seed profile for newly constructed consumers; seven constructor-bound component addresses |
| [`DefaultsRobinhoodLive`](../governance/configuration/DefaultsRobinhoodLive.md) | Generated replacement seed; only the Contributor template is constructor-bound |
| [`DefaultsLocal`](../governance/configuration/DefaultsLocal.md) | Deliberately minimal local development/test seed |

The `Live` suffix describes the source files' replacement-seed role; it is not
a statement about current deployment status. Launch-style and replacement
profiles are not interchangeable.

<!-- BEGIN GENERATED API REFERENCE: Defaults -->
## Exact source-declared API reference

> Generated from declarations in `interfaces/Defaults.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers deployment/module initializers, external functions and their default-argument call forms, compiler-generated public getters inferred from declarations, events, flags, constants, structs, and source-declared revert reasons found in this source. It does not claim a composed host ABI or canonical runtime selector surface.

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def assetConfigs() -> DynArray[cs.AssetConfigEntry, 50]` | `0` | `view` | `DynArray[cs.AssetConfigEntry, 50]` |
| `def genConfig() -> cs.GenConfig` | `0` | `view` | `cs.GenConfig` |
| `def genDebtConfig() -> cs.GenDebtConfig` | `0` | `view` | `cs.GenDebtConfig` |
| `def hrConfig() -> cs.HrConfig` | `0` | `view` | `cs.HrConfig` |
| `def liteSigners() -> DynArray[address, 10]` | `0` | `view` | `DynArray[address, 10]` |
| `def priorityLiqAssetVaults() -> DynArray[cs.VaultLite, 20]` | `0` | `view` | `DynArray[cs.VaultLite, 20]` |
| `def priorityPriceSourceIds() -> DynArray[uint256, 10]` | `0` | `view` | `DynArray[uint256, 10]` |
| `def priorityStabVaults() -> DynArray[cs.VaultLite, 20]` | `0` | `view` | `DynArray[cs.VaultLite, 20]` |
| `def rewardsConfig() -> cs.RipeRewardsConfig` | `0` | `view` | `cs.RipeRewardsConfig` |
| `def ripeAvailForBonds() -> uint256` | `0` | `view` | `uint256` |
| `def ripeAvailForHr() -> uint256` | `0` | `view` | `uint256` |
| `def ripeAvailForRewards() -> uint256` | `0` | `view` | `uint256` |
| `def ripeBondConfig() -> cs.RipeBondConfig` | `0` | `view` | `cs.RipeBondConfig` |
| `def ripeGovVaultConfigs() -> DynArray[cs.RipeGovVaultConfigEntry, 5]` | `0` | `view` | `DynArray[cs.RipeGovVaultConfigEntry, 5]` |
| `def shouldCheckLastTouch() -> bool` | `0` | `view` | `bool` |
| `def trainingWheels() -> address` | `0` | `view` | `address` |
| `def underscoreRegistry() -> address` | `0` | `view` | `address` |

### Source-declared call forms

Each row is one source-level call form permitted by the declaration's trailing defaults. These signatures use Vyper source notation; they are not canonical ABI signatures or selector-hash preimages. Without a tracked compiled ABI, this table does not claim the exact runtime selector surface.

| Source call form | Mutability | Returns |
| --- | --- | --- |
| `assetConfigs()` | `view` | `DynArray[cs.AssetConfigEntry, 50]` |
| `genConfig()` | `view` | `cs.GenConfig` |
| `genDebtConfig()` | `view` | `cs.GenDebtConfig` |
| `hrConfig()` | `view` | `cs.HrConfig` |
| `liteSigners()` | `view` | `DynArray[address, 10]` |
| `priorityLiqAssetVaults()` | `view` | `DynArray[cs.VaultLite, 20]` |
| `priorityPriceSourceIds()` | `view` | `DynArray[uint256, 10]` |
| `priorityStabVaults()` | `view` | `DynArray[cs.VaultLite, 20]` |
| `rewardsConfig()` | `view` | `cs.RipeRewardsConfig` |
| `ripeAvailForBonds()` | `view` | `uint256` |
| `ripeAvailForHr()` | `view` | `uint256` |
| `ripeAvailForRewards()` | `view` | `uint256` |
| `ripeBondConfig()` | `view` | `cs.RipeBondConfig` |
| `ripeGovVaultConfigs()` | `view` | `DynArray[cs.RipeGovVaultConfigEntry, 5]` |
| `shouldCheckLastTouch()` | `view` | `bool` |
| `trainingWheels()` | `view` | `address` |
| `underscoreRegistry()` | `view` | `address` |

<!-- END GENERATED API REFERENCE: Defaults -->
