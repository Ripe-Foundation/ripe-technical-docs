# DefaultsLocal

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/DefaultsLocal.vy)

`DefaultsLocal` is the minimal [`Defaults`](../../interfaces/Defaults.md)
seed used by local development and tests. It is deliberately sparse and is not
a launch-style or replacement-state profile.

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

<!-- END GENERATED API REFERENCE: DefaultsLocal -->
