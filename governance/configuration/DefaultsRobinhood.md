# DefaultsRobinhood

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/DefaultsRobinhood.vy)

`DefaultsRobinhood` implements the
[`Defaults`](../../interfaces/Defaults.md) interface. `MissionControl` and
`Ledger` read its getters during construction and copy the results into their
own storage.

## Constructor

`DefaultsRobinhood` is a seed profile for newly constructed MissionControl and
Ledger consumers. It is not a replacement-state profile; that role belongs to
[`DefaultsRobinhoodLive`](DefaultsRobinhoodLive.md).

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

Shared unit conventions and interface capacities are documented on the
[`Defaults` interface](../../interfaces/Defaults.md). Ledger's action-block
source remains a separate constructor dependency.

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

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `assetConfigs()` | `view` | `(address asset, (uint256[] vaultIds, uint256 stakersPointsAlloc, uint256 voterPointsAlloc, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 minDepositBalance, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, bool canDeposit, bool canWithdraw, bool canRedeemCollateral, bool canRedeemInStabPool, bool canBuyInAuction, bool canClaimInStabPool, uint256 specialStabPoolId, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) customAuctionParams, address whitelist, bool isNft) config)[]` | `DynArray[cs.AssetConfigEntry, 50]` |
| `genConfig()` | `view` | `(uint256 perUserMaxVaults, uint256 perUserMaxAssetsPerVault, uint256 priceStaleTime, bool canDeposit, bool canWithdraw, bool canBorrow, bool canRepay, bool canClaimLoot, bool canLiquidate, bool canRedeemCollateral, bool canRedeemInStabPool, bool canBuyInAuction, bool canClaimInStabPool)` | `cs.GenConfig` |
| `genDebtConfig()` | `view` | `(uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, uint256 numAllowedBorrowers, uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval, uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate, uint256 maxLtvDeviation, uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee, bool isDaowryEnabled, uint256 ltvPaybackBuffer, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) genAuctionParams)` | `cs.GenDebtConfig` |
| `hrConfig()` | `view` | `(address contribTemplate, uint256 maxCompensation, uint256 minCliffLength, uint256 maxStartDelay, uint256 minVestingLength, uint256 maxVestingLength)` | `cs.HrConfig` |
| `liteSigners()` | `view` | `address[]` | `DynArray[address, 10]` |
| `priorityLiqAssetVaults()` | `view` | `(uint256 vaultId, address asset)[]` | `DynArray[cs.VaultLite, 20]` |
| `priorityPriceSourceIds()` | `view` | `uint256[]` | `DynArray[uint256, 10]` |
| `priorityStabVaults()` | `view` | `(uint256 vaultId, address asset)[]` | `DynArray[cs.VaultLite, 20]` |
| `rewardsConfig()` | `view` | `(bool arePointsEnabled, uint256 ripePerBlock, uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc, uint256 autoStakeRatio, uint256 autoStakeDurationRatio, uint256 stabPoolRipePerDollarClaimed)` | `cs.RipeRewardsConfig` |
| `ripeAvailForBonds()` | `view` | `uint256` | `uint256` |
| `ripeAvailForHr()` | `view` | `uint256` | `uint256` |
| `ripeAvailForRewards()` | `view` | `uint256` | `uint256` |
| `ripeBondConfig()` | `view` | `(address asset, uint256 amountPerEpoch, bool canBond, uint256 minRipePerUnit, uint256 maxRipePerUnit, uint256 maxRipePerUnitLockBonus, uint256 epochLength, bool shouldAutoRestart, uint256 restartDelayBlocks)` | `cs.RipeBondConfig` |
| `ripeGovVaultConfigs()` | `view` | `(address asset, ((uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee) lockTerms, uint256 assetWeight, bool shouldFreezeWhenBadDebt) config)[]` | `DynArray[cs.RipeGovVaultConfigEntry, 5]` |
| `shouldCheckLastTouch()` | `view` | `bool` | `bool` |
| `trainingWheels()` | `view` | `address` | `address` |
| `underscoreRegistry()` | `view` | `address` | `address` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `duplicate defaults address`
- `invalid defaults address`

<!-- END GENERATED API REFERENCE: DefaultsRobinhood -->
