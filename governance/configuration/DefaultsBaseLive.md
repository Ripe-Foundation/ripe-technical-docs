# DefaultsBaseLive

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/DefaultsBaseLive.vy)

`DefaultsBaseLive` is a generated implementation of the
[`Defaults`](../../interfaces/Defaults.md) interface. `MissionControl` and
`Ledger` can read it during construction and copy the returned configuration
into storage.

## Construction and getter domains

`DefaultsBaseLive` is a generated replacement seed for constructing a new
MissionControl or Ledger from state exposed through Defaults. It is not
interchangeable with the newly constructed-consumer seed in
[`DefaultsBase`](DefaultsBase.md).

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
surface. A replacement MissionControl starts with its constructor pointer
defaults rather than copying current pointers. Known user settings and pointers
can be reconstructed individually through Teller or Switchboard routes, but
there is no direct arbitrary bulk import for historical role mappings.

<!-- BEGIN GENERATED API REFERENCE: DefaultsBaseLive -->
## Exact API reference

> Generated from `contracts/config/DefaultsBaseLive.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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

<!-- END GENERATED API REFERENCE: DefaultsBaseLive -->
