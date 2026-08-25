# DefaultsRobinhood

`DefaultsRobinhood` implements the
[`Defaults`](../../interfaces/Defaults.md) interface. `MissionControl` and
`Ledger` read its getters during construction and copy the results into their
own storage.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/DefaultsRobinhood.vy)

## Constructor

The constructor binds seven component addresses:

- Contributor template;
- TrainingWheels;
- RIPE;
- GREEN;
- Savings GREEN;
- USDG; and
- WETH.

Every address must be nonzero, and the constructor rejects duplicates across
the set. The Underscore registry getter is independent of those
constructor-bound components.

## Getter domains

The contract returns general and debt configuration, Ledger budgets, bond and
reward policy, RipeGov and HR configuration, asset configuration, priority
routes, price-source priority, Underscore and TrainingWheels settings,
last-touch policy, and lite signers.

Durations returned by Defaults are consumed as EVM `block.number` intervals
unless the receiving field explicitly uses timestamps. Ledger's action-block
source is a separate constructor dependency.

## Copy semantics

`MissionControl` and `Ledger` copy the returned values during construction.
Later changes to their stored configuration do not modify this contract, and
later changes to the Defaults source do not modify existing consumers.

<!-- BEGIN GENERATED API REFERENCE: DefaultsRobinhood -->
## Exact API reference

> Generated from `contracts/config/DefaultsRobinhood.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _contribTemplate, address _trainingWheels, address _ripeToken, address _greenToken, address _sgreenToken, address _usdgToken, address _wethToken)`

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

<!-- END GENERATED API REFERENCE: DefaultsRobinhood -->
