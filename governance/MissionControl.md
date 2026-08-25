# MissionControl

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/data/MissionControl.vy)

`MissionControl` is the protocol's configuration store and read-composition
layer. Switchboard configuration contracts write policy into it; Teller,
CreditEngine, AuctionHouse, Lootbox, price sources, vaults, and other consumers
read purpose-specific configuration views from it.

## Initialization and defaults

The constructor binds MissionControl to RipeHq and optionally copies values from
a [`Defaults`](../interfaces/Defaults.md) contract into storage. The copy is
one-time: the Defaults contract is not consulted for later configuration reads.

Initialization starts the current preferred StabilityPool ID at 1 and the
current core RipeGov vault ID at 2, and records each in its monotonic
classification. Processing Defaults also marks every nonzero StabilityPool ID
present in an asset's `specialStabPoolId` or the priority StabilityPool routes.
The selected Defaults implementation populates the remaining global, debt, HR, bond,
rewards, asset, training-wheels, Underscore, and lite-signer state.

## Configuration domains

| Domain | Stored policy |
| --- | --- |
| General | Global operation flags, vault/asset limits, price staleness |
| Debt | User/global caps, interval limits, rates, deviation rail, keeper fees, auction defaults |
| Assets | Vault routes, point allocations, deposit limits, debt terms, liquidation routes, per-asset flags and whitelist |
| Users | Public-action preferences and delegate permissions |
| Rewards | Emission rate, allocation ratios, auto-stake behavior, StabilityPool claim reward |
| Vaults | RipeGov asset terms, current core/preferred IDs, priority routes, historical classifications |
| HR and bonds | Contributor bounds and RIPE bond configuration |
| Other | Priority price sources, TrainingWheels, Underscore registry, last-touch policy, lite signers |

Every configuration setter accepts a currently registered Switchboard
configuration contract. Only `setUserConfig` and `setUserDelegation` have an
additional writer: the current Teller may call those two setters on behalf of
users. SwitchboardCharlie supplies the governance recovery/administration route
for the same user records, while ordinary user changes flow through Teller;
MissionControl does not authorize end-user calls directly.

## Current vault pointers and historical classifications

The vault identity model separates current routing from historical authority:

| State | Semantics |
| --- | --- |
| `coreRipeGovVaultId` | Current RipeGov destination used by new core flows |
| `preferredStabVaultId` | Current preferred StabilityPool destination |
| `isRipeGovVaultId[id]` | Monotonic: the ID is or once was a RipeGov vault |
| `isStabVaultId[id]` | Monotonic: the ID is or once was a StabilityPool |

Setting a new current ID marks both the previous and new RipeGov IDs as
historical RipeGov IDs. StabilityPool IDs are marked when they become preferred,
appear in a priority StabilityPool list, or are configured as an asset's special
StabilityPool. No setter clears either historical classification. Retired pools
can retain balances and claim/reward paths, so consumers must not treat
"not current" as "no longer a StabilityPool or RipeGov vault."

## Assets and point allocations

Supported assets use a one-based swap-and-pop index. `setAssetConfig` updates
aggregate staker/voter allocation totals before storing the new config and
registers a new asset if needed. `deregisterAsset` refuses an asset with active
staker or voter point allocation and then removes it from the enumerable list.

Liquidation view composition resolves configured vault IDs through the current
VaultBook and omits entries whose current vault address is zero. A special
StabilityPool route is likewise returned only when the configured vault and its
first asset resolve.

## Lite signers

Lite-action authority is an iterable set, not a public boolean mapping:

- `canPerformLiteAction(signer)` checks the signer's one-based index;
- `liteSigners(index)`, `indexOfLiteSigner`, and `numLiteSigners` expose the set;
  and
- removal uses swap-and-pop and clears the former last slot.

The individual Switchboard configuration contracts define what a lite signer
may do. Generally, lite access is limited to risk-reducing or operational
actions; it is not equivalent to governance.

## Composed read APIs

MissionControl turns stored policy into consumer-specific bundles for deposits,
withdrawals, borrowing, repayment, collateral redemption, auction purchases,
liquidation, StabilityPool claims/redemptions, loot claims, rewards, pricing,
bonds, and dynamic borrow rates.

Delegated actions are checked per capability. `doesUndyLegoHaveAccess` requires
the wallet's public deposit and public repayment permissions plus delegated
withdraw, borrow, and loot-claim permissions for that Lego address.

## Security notes

- Configuration setters trust registered Switchboard contracts to validate
  ranges and state transitions; direct MissionControl storage is intentionally
  lean.
- Current pointers may move while historical classification remains true.
- Defaults values are copied, not referenced.

<!-- BEGIN GENERATED API REFERENCE: MissionControl -->
## Exact API reference

> Generated from `contracts/data/MissionControl.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _defaults)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `assetConfig(address arg0)` | `view` | `(uint256[] vaultIds, uint256 stakersPointsAlloc, uint256 voterPointsAlloc, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 minDepositBalance, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, bool canDeposit, bool canWithdraw, bool canRedeemCollateral, bool canRedeemInStabPool, bool canBuyInAuction, bool canClaimInStabPool, uint256 specialStabPoolId, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) customAuctionParams, address whitelist, bool isNft)` | — |
| `assets(uint256 arg0)` | `view` | `address` | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `canPerformLiteAction(address _signer)` | `view` | `bool` | `bool` |
| `coreRipeGovVaultId()` | `view` | `uint256` | — |
| `deregisterAsset(address _asset)` | `nonpayable` | `bool` | `bool` |
| `doesUndyLegoHaveAccess(address _wallet, address _legoAddr)` | `view` | `bool` | `bool` |
| `genConfig()` | `view` | `(uint256 perUserMaxVaults, uint256 perUserMaxAssetsPerVault, uint256 priceStaleTime, bool canDeposit, bool canWithdraw, bool canBorrow, bool canRepay, bool canClaimLoot, bool canLiquidate, bool canRedeemCollateral, bool canRedeemInStabPool, bool canBuyInAuction, bool canClaimInStabPool)` | — |
| `genDebtConfig()` | `view` | `(uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, uint256 numAllowedBorrowers, uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval, uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate, uint256 maxLtvDeviation, uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee, bool isDaowryEnabled, uint256 ltvPaybackBuffer, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) genAuctionParams)` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getAssetLiqConfig(address _asset)` | `view` | `(bool hasConfig, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) customAuctionParams, (uint256 vaultId, address vaultAddr, address asset) specialStabPool)` | `AssetLiqConfig` |
| `getAuctionBuyConfig(address _asset, address _recipient)` | `view` | `(bool canBuyInAuctionGeneral, bool canBuyInAuctionAsset, bool isUserAllowed, bool canAnyoneDeposit)` | `AuctionBuyConfig` |
| `getBorrowConfig(address _user, address _caller)` | `view` | `(bool canBorrow, bool canBorrowForUser, uint256 numAllowedBorrowers, uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval, uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, bool isDaowryEnabled)` | `BorrowConfig` |
| `getClaimLootConfig(address _user, address _caller, address _ripeToken)` | `view` | `(bool canClaimLoot, bool canClaimLootForUser, uint256 autoStakeRatio, uint256 rewardsLockDuration)` | `ClaimLootConfig` |
| `getDebtTerms(address _asset)` | `view` | `(uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry)` | `cs.DebtTerms` |
| `getDepositPointsConfig(address _asset)` | `view` | `(uint256 stakersPointsAlloc, uint256 voterPointsAlloc, bool isNft)` | `DepositPointsConfig` |
| `getDynamicBorrowRateConfig()` | `view` | `(uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate)` | `DynamicBorrowRateConfig` |
| `getFirstVaultIdForAsset(address _asset)` | `view` | `uint256` | `uint256` |
| `getGenAuctionParams()` | `view` | `(bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration)` | `cs.AuctionParams` |
| `getGenLiqConfig()` | `view` | `(bool canLiquidate, uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee, uint256 ltvPaybackBuffer, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) genAuctionParams, (uint256 vaultId, address vaultAddr, address asset)[] priorityLiqAssetVaults, (uint256 vaultId, address vaultAddr, address asset)[] priorityStabVaults)` | `GenLiqConfig` |
| `getLtvPaybackBuffer()` | `view` | `uint256` | `uint256` |
| `getNumAssets()` | `view` | `uint256` | `uint256` |
| `getPriceConfig()` | `view` | `(uint256 staleTime, uint256[] priorityPriceSourceIds)` | `PriceConfig` |
| `getPriceStaleTime()` | `view` | `uint256` | `uint256` |
| `getPriorityLiqAssetVaults()` | `view` | `(uint256 vaultId, address asset)[]` | `DynArray[cs.VaultLite, PRIORITY_VAULT_DATA]` |
| `getPriorityPriceSourceIds()` | `view` | `uint256[]` | `DynArray[uint256, MAX_PRIORITY_PRICE_SOURCES]` |
| `getPriorityStabVaults()` | `view` | `(uint256 vaultId, address asset)[]` | `DynArray[cs.VaultLite, PRIORITY_VAULT_DATA]` |
| `getPurchaseRipeBondConfig(address _user)` | `view` | `(address asset, uint256 amountPerEpoch, bool canBond, uint256 minRipePerUnit, uint256 maxRipePerUnit, uint256 maxRipePerUnitLockBonus, uint256 epochLength, bool shouldAutoRestart, uint256 restartDelayBlocks, uint256 minLockDuration, uint256 maxLockDuration, bool canAnyoneBondForUser, bool isUserAllowed)` | `PurchaseRipeBondConfig` |
| `getRedeemCollateralConfig(address _asset, address _recipient)` | `view` | `(bool canRedeemCollateralGeneral, bool canRedeemCollateralAsset, bool isUserAllowed, uint256 ltvPaybackBuffer, bool canAnyoneDeposit)` | `RedeemCollateralConfig` |
| `getRepayConfig(address _user)` | `view` | `(bool canRepay, bool canAnyoneRepayDebt)` | `RepayConfig` |
| `getRewardsConfig()` | `view` | `(bool arePointsEnabled, uint256 ripePerBlock, uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc, uint256 stakersPointsAllocTotal, uint256 voterPointsAllocTotal)` | `RewardsConfig` |
| `getRipeHq()` | `view` | `address` | — |
| `getStabPoolClaimsConfig(address _claimAsset, address _claimer, address _caller, address _ripeToken)` | `view` | `(bool canClaimInStabPoolGeneral, bool canClaimInStabPoolAsset, bool canClaimFromStabPoolForUser, bool isUserAllowed, uint256 rewardsLockDuration, uint256 ripePerDollarClaimed)` | `StabPoolClaimsConfig` |
| `getStabPoolRedemptionsConfig(address _asset, address _recipient)` | `view` | `(bool canRedeemInStabPoolGeneral, bool canRedeemInStabPoolAsset, bool isUserAllowed, bool canAnyoneDeposit)` | `StabPoolRedemptionsConfig` |
| `getTellerDepositConfig(uint256 _vaultId, address _asset, address _user)` | `view` | `(bool canDepositGeneral, bool canDepositAsset, bool doesVaultSupportAsset, bool isUserAllowed, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 perUserMaxAssetsPerVault, uint256 perUserMaxVaults, bool canAnyoneDeposit, uint256 minDepositBalance)` | `TellerDepositConfig` |
| `getTellerWithdrawConfig(address _asset, address _user, address _caller)` | `view` | `(bool canWithdrawGeneral, bool canWithdrawAsset, bool isUserAllowed, bool canWithdrawForUser, uint256 minDepositBalance)` | `TellerWithdrawConfig` |
| `hrConfig()` | `view` | `(address contribTemplate, uint256 maxCompensation, uint256 minCliffLength, uint256 maxStartDelay, uint256 minVestingLength, uint256 maxVestingLength)` | — |
| `indexOfAsset(address arg0)` | `view` | `uint256` | — |
| `indexOfLiteSigner(address arg0)` | `view` | `uint256` | — |
| `isPaused()` | `view` | `bool` | — |
| `isRipeGovVaultId(uint256 arg0)` | `view` | `bool` | — |
| `isStabVaultId(uint256 arg0)` | `view` | `bool` | — |
| `isSupportedAsset(address _asset)` | `view` | `bool` | `bool` |
| `isSupportedAssetInVault(uint256 _vaultId, address _asset)` | `view` | `bool` | `bool` |
| `liteSigners(uint256 arg0)` | `view` | `address` | — |
| `maxLtvDeviation()` | `view` | `uint256` | `uint256` |
| `numAssets()` | `view` | `uint256` | — |
| `numLiteSigners()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `preferredStabVaultId()` | `view` | `uint256` | — |
| `priorityLiqAssetVaults(uint256 arg0)` | `view` | `(uint256 vaultId, address asset)` | — |
| `priorityPriceSourceIds(uint256 arg0)` | `view` | `uint256` | — |
| `priorityStabVaults(uint256 arg0)` | `view` | `(uint256 vaultId, address asset)` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `rewardsConfig()` | `view` | `(bool arePointsEnabled, uint256 ripePerBlock, uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc, uint256 autoStakeRatio, uint256 autoStakeDurationRatio, uint256 stabPoolRipePerDollarClaimed)` | — |
| `ripeBondConfig()` | `view` | `(address asset, uint256 amountPerEpoch, bool canBond, uint256 minRipePerUnit, uint256 maxRipePerUnit, uint256 maxRipePerUnitLockBonus, uint256 epochLength, bool shouldAutoRestart, uint256 restartDelayBlocks)` | — |
| `ripeGovVaultConfig(address arg0)` | `view` | `((uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee) lockTerms, uint256 assetWeight, bool shouldFreezeWhenBadDebt)` | — |
| `setAssetConfig(address _asset, (uint256[],uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,uint256,(bool,uint256,uint256,uint256,uint256),address,bool) _config)` | `nonpayable` | — | — |
| `setCanPerformLiteAction(address _signer, bool _canDo)` | `nonpayable` | — | — |
| `setCoreRipeGovVaultId(uint256 _vaultId)` | `nonpayable` | — | — |
| `setGeneralConfig((uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool) _config)` | `nonpayable` | — | — |
| `setGeneralDebtConfig((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256,(bool,uint256,uint256,uint256,uint256)) _config)` | `nonpayable` | — | — |
| `setHrConfig((address,uint256,uint256,uint256,uint256,uint256) _config)` | `nonpayable` | — | — |
| `setPreferredStabVaultId(uint256 _vaultId)` | `nonpayable` | — | — |
| `setPriorityLiqAssetVaults((uint256,address)[] _priorityLiqAssetVaults)` | `nonpayable` | — | — |
| `setPriorityPriceSourceIds(uint256[] _priorityIds)` | `nonpayable` | — | — |
| `setPriorityStabVaults((uint256,address)[] _priorityStabVaults)` | `nonpayable` | — | — |
| `setRipeBondConfig((address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256) _config)` | `nonpayable` | — | — |
| `setRipeGovVaultConfig(address _asset, uint256 _assetWeight, bool _shouldFreezeWhenBadDebt, (uint256,uint256,uint256,bool,uint256) _lockTerms)` | `nonpayable` | — | — |
| `setRipeRewardsConfig((bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _config)` | `nonpayable` | — | — |
| `setShouldCheckLastTouch(bool _shouldCheck)` | `nonpayable` | — | — |
| `setTrainingWheels(address _trainingWheels)` | `nonpayable` | — | — |
| `setUnderscoreRegistry(address _underscoreRegistry)` | `nonpayable` | — | — |
| `setUserConfig(address _user, (bool,bool,bool) _config)` | `nonpayable` | — | — |
| `setUserDelegation(address _user, address _delegate, (bool,bool,bool,bool) _config)` | `nonpayable` | — | — |
| `shouldCheckLastTouch()` | `view` | `bool` | — |
| `totalPointsAllocs()` | `view` | `(uint256 stakersPointsAllocTotal, uint256 voterPointsAllocTotal)` | — |
| `trainingWheels()` | `view` | `address` | — |
| `underscoreRegistry()` | `view` | `address` | — |
| `userConfig(address arg0)` | `view` | `(bool canAnyoneDeposit, bool canAnyoneRepayDebt, bool canAnyoneBondForUser)` | — |
| `userDelegation(address arg0, address arg1)` | `view` | `(bool canWithdraw, bool canBorrow, bool canClaimFromStabPool, bool canClaimLoot)` | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

### Structs declared by this source

- `TotalPointsAllocs(stakersPointsAllocTotal: uint256, voterPointsAllocTotal: uint256)`
- `TellerDepositConfig(canDepositGeneral: bool, canDepositAsset: bool, doesVaultSupportAsset: bool, isUserAllowed: bool, perUserDepositLimit: uint256, globalDepositLimit: uint256, perUserMaxAssetsPerVault: uint256, perUserMaxVaults: uint256, canAnyoneDeposit: bool, minDepositBalance: uint256)`
- `TellerWithdrawConfig(canWithdrawGeneral: bool, canWithdrawAsset: bool, isUserAllowed: bool, canWithdrawForUser: bool, minDepositBalance: uint256)`
- `BorrowConfig(canBorrow: bool, canBorrowForUser: bool, numAllowedBorrowers: uint256, maxBorrowPerInterval: uint256, numBlocksPerInterval: uint256, perUserDebtLimit: uint256, globalDebtLimit: uint256, minDebtAmount: uint256, isDaowryEnabled: bool)`
- `RepayConfig(canRepay: bool, canAnyoneRepayDebt: bool)`
- `RedeemCollateralConfig(canRedeemCollateralGeneral: bool, canRedeemCollateralAsset: bool, isUserAllowed: bool, ltvPaybackBuffer: uint256, canAnyoneDeposit: bool)`
- `AuctionBuyConfig(canBuyInAuctionGeneral: bool, canBuyInAuctionAsset: bool, isUserAllowed: bool, canAnyoneDeposit: bool)`
- `GenLiqConfig(canLiquidate: bool, keeperFeeRatio: uint256, minKeeperFee: uint256, maxKeeperFee: uint256, ltvPaybackBuffer: uint256, genAuctionParams: cs.AuctionParams, priorityLiqAssetVaults: DynArray[VaultData, PRIORITY_VAULT_DATA], priorityStabVaults: DynArray[VaultData, PRIORITY_VAULT_DATA])`
- `VaultData(vaultId: uint256, vaultAddr: address, asset: address)`
- `AssetLiqConfig(hasConfig: bool, shouldBurnAsPayment: bool, shouldTransferToEndaoment: bool, shouldSwapInStabPools: bool, shouldAuctionInstantly: bool, customAuctionParams: cs.AuctionParams, specialStabPool: VaultData)`
- `StabPoolClaimsConfig(canClaimInStabPoolGeneral: bool, canClaimInStabPoolAsset: bool, canClaimFromStabPoolForUser: bool, isUserAllowed: bool, rewardsLockDuration: uint256, ripePerDollarClaimed: uint256)`
- `StabPoolRedemptionsConfig(canRedeemInStabPoolGeneral: bool, canRedeemInStabPoolAsset: bool, isUserAllowed: bool, canAnyoneDeposit: bool)`
- `ClaimLootConfig(canClaimLoot: bool, canClaimLootForUser: bool, autoStakeRatio: uint256, rewardsLockDuration: uint256)`
- `RewardsConfig(arePointsEnabled: bool, ripePerBlock: uint256, borrowersAlloc: uint256, stakersAlloc: uint256, votersAlloc: uint256, genDepositorsAlloc: uint256, stakersPointsAllocTotal: uint256, voterPointsAllocTotal: uint256)`
- `DepositPointsConfig(stakersPointsAlloc: uint256, voterPointsAlloc: uint256, isNft: bool)`
- `PriceConfig(staleTime: uint256, priorityPriceSourceIds: DynArray[uint256, MAX_PRIORITY_PRICE_SOURCES])`
- `PurchaseRipeBondConfig(asset: address, amountPerEpoch: uint256, canBond: bool, minRipePerUnit: uint256, maxRipePerUnit: uint256, maxRipePerUnitLockBonus: uint256, epochLength: uint256, shouldAutoRestart: bool, restartDelayBlocks: uint256, minLockDuration: uint256, maxLockDuration: uint256, canAnyoneBondForUser: bool, isUserAllowed: bool)`
- `DynamicBorrowRateConfig(minDynamicRateBoost: uint256, maxDynamicRateBoost: uint256, increasePerDangerBlock: uint256, maxBorrowRate: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `active points alloc`
- `invalid vault id`
- `no perms`

<!-- END GENERATED API REFERENCE: MissionControl -->
