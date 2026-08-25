# ConfigStructs interface

`ConfigStructs.vyi` is the canonical shared type vocabulary for Defaults,
MissionControl, Switchboards, and configuration consumers. It declares data
shapes only and does not validate their values.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/ConfigStructs.vyi)

## Configuration groups

| Struct | Purpose |
| --- | --- |
| `GenConfig` | Global vault/asset limits, price staleness, and operation enable flags |
| `GenDebtConfig` | Debt caps, interval/rate policy, directional deviation rail, keeper fees, daowry, payback buffer, and default auction parameters |
| `HrConfig` | Contributor template and compensation/cliff/start/vesting bounds |
| `RipeBondConfig` | Bond asset, epoch capacity, RIPE price limits, lock bonus, epoch, and restart policy |
| `RipeRewardsConfig` | Point enablement, emission/allocation, auto-stake policy, and StabilityPool claim reward |
| `RipeGovVaultConfig` | Per-asset RipeGov lock terms, weight, and bad-debt freeze policy |
| `LockTerms` | Minimum/maximum duration, maximum boost, early-exit flag and fee |
| `AuctionParams` | Presence flag, start/max discount, delay, and duration |
| `AssetConfig` | Vault routes, point allocations, deposit caps, debt terms, liquidation routing, operation flags, special pool, whitelist, and NFT flag |
| `DebtTerms` | LTV, redemption/liquidation thresholds, liquidation fee, borrow rate, and daowry |
| `UserConfig` | Public deposit, public repayment, and public bond-for-user preferences |
| `ActionDelegation` | Delegate permissions for withdraw, borrow, StabilityPool claim, and loot claim |
| `VaultLite` | `(vaultId, asset)` routing pair |
| `AssetConfigEntry` | Asset plus complete `AssetConfig`, used by Defaults |
| `RipeGovVaultConfigEntry` | Asset plus RipeGov configuration, used by Defaults |

`AssetConfig.vaultIds` is bounded by `MAX_VAULTS_PER_ASSET == 10`.

## Units and validation

The interface does not encode units. In current implementations:

- percentages and ratios are generally basis points (`100_00 == 100%`);
- token amounts use the relevant token's native decimals unless a consumer
  explicitly normalizes them;
- debt and reward USD accounting commonly uses 18 decimals; and
- duration fields may use EVM blocks or seconds depending on the consuming
  subsystem.

Switchboards, not this interface, enforce ordering, caps, overflow safety,
directional debt-term limits, supported-vault checks, and other semantic
invariants.

## Compatibility rule

Adding, removing, or reordering a struct field changes the ABI tuple type of
every function that consumes it. Consumers should use the exact generated
interface inventory rather than reconstructing tuples from examples.

<!-- BEGIN GENERATED API REFERENCE: ConfigStructs -->
## Exact API reference

> Generated from declarations in `interfaces/ConfigStructs.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- None.

### Structs declared by this source

- `GenConfig(perUserMaxVaults: uint256, perUserMaxAssetsPerVault: uint256, priceStaleTime: uint256, canDeposit: bool, canWithdraw: bool, canBorrow: bool, canRepay: bool, canClaimLoot: bool, canLiquidate: bool, canRedeemCollateral: bool, canRedeemInStabPool: bool, canBuyInAuction: bool, canClaimInStabPool: bool)`
- `GenDebtConfig(perUserDebtLimit: uint256, globalDebtLimit: uint256, minDebtAmount: uint256, numAllowedBorrowers: uint256, maxBorrowPerInterval: uint256, numBlocksPerInterval: uint256, minDynamicRateBoost: uint256, maxDynamicRateBoost: uint256, increasePerDangerBlock: uint256, maxBorrowRate: uint256, maxLtvDeviation: uint256, keeperFeeRatio: uint256, minKeeperFee: uint256, maxKeeperFee: uint256, isDaowryEnabled: bool, ltvPaybackBuffer: uint256, genAuctionParams: AuctionParams)`
- `HrConfig(contribTemplate: address, maxCompensation: uint256, minCliffLength: uint256, maxStartDelay: uint256, minVestingLength: uint256, maxVestingLength: uint256)`
- `RipeBondConfig(asset: address, amountPerEpoch: uint256, canBond: bool, minRipePerUnit: uint256, maxRipePerUnit: uint256, maxRipePerUnitLockBonus: uint256, epochLength: uint256, shouldAutoRestart: bool, restartDelayBlocks: uint256)`
- `RipeRewardsConfig(arePointsEnabled: bool, ripePerBlock: uint256, borrowersAlloc: uint256, stakersAlloc: uint256, votersAlloc: uint256, genDepositorsAlloc: uint256, autoStakeRatio: uint256, autoStakeDurationRatio: uint256, stabPoolRipePerDollarClaimed: uint256)`
- `RipeGovVaultConfig(lockTerms: LockTerms, assetWeight: uint256, shouldFreezeWhenBadDebt: bool)`
- `LockTerms(minLockDuration: uint256, maxLockDuration: uint256, maxLockBoost: uint256, canExit: bool, exitFee: uint256)`
- `AuctionParams(hasParams: bool, startDiscount: uint256, maxDiscount: uint256, delay: uint256, duration: uint256)`
- `AssetConfig(vaultIds: DynArray[uint256, MAX_VAULTS_PER_ASSET], stakersPointsAlloc: uint256, voterPointsAlloc: uint256, perUserDepositLimit: uint256, globalDepositLimit: uint256, minDepositBalance: uint256, debtTerms: DebtTerms, shouldBurnAsPayment: bool, shouldTransferToEndaoment: bool, shouldSwapInStabPools: bool, shouldAuctionInstantly: bool, canDeposit: bool, canWithdraw: bool, canRedeemCollateral: bool, canRedeemInStabPool: bool, canBuyInAuction: bool, canClaimInStabPool: bool, specialStabPoolId: uint256, customAuctionParams: AuctionParams, whitelist: address, isNft: bool)`
- `DebtTerms(ltv: uint256, redemptionThreshold: uint256, liqThreshold: uint256, liqFee: uint256, borrowRate: uint256, daowry: uint256)`
- `UserConfig(canAnyoneDeposit: bool, canAnyoneRepayDebt: bool, canAnyoneBondForUser: bool)`
- `ActionDelegation(canWithdraw: bool, canBorrow: bool, canClaimFromStabPool: bool, canClaimLoot: bool)`
- `VaultLite(vaultId: uint256, asset: address)`
- `AssetConfigEntry(asset: address, config: AssetConfig)`
- `RipeGovVaultConfigEntry(asset: address, config: RipeGovVaultConfig)`

<!-- END GENERATED API REFERENCE: ConfigStructs -->
