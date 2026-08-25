# DefaultsBase

`DefaultsBase` implements the [`Defaults`](../../interfaces/Defaults.md)
interface. `MissionControl` and `Ledger` read its getters during construction
and copy the returned values into their own storage.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/DefaultsBase.vy)

## Construction and role

The contract has no constructor arguments. Its getter bodies encode a complete
configuration profile covering:

- general and debt policy;
- Ledger RIPE budgets;
- bond, rewards, RipeGov, and HR configuration;
- asset onboarding and debt/liquidation routes;
- priority liquidation vaults, StabilityPools, and price sources; and
- TrainingWheels, Underscore, last-touch policy, and lite signers.

Percentages are basis points (`100_00 == 100%`). Token and USD quantities retain
the decimals expected by each consuming configuration field.

## Copy semantics

Deploying MissionControl with this defaults contract copies the values once.
Later configuration changes do not mutate `DefaultsBase`, and changing the
Defaults source does not alter an existing `MissionControl` or `Ledger`.

<!-- BEGIN GENERATED API REFERENCE: DefaultsBase -->
## Exact API reference

> Generated from `contracts/config/DefaultsBase.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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

<!-- END GENERATED API REFERENCE: DefaultsBase -->
