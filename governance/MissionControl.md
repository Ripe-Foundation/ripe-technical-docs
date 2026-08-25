# MissionControl

`MissionControl` is the protocol's configuration store and read-composition
layer. Switchboard configuration contracts write policy into it; Teller,
CreditEngine, AuctionHouse, Lootbox, price sources, vaults, and other consumers
read purpose-specific configuration views from it.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/data/MissionControl.vy)

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

Only a currently registered Switchboard configuration contract may call the
configuration setters, except that Teller may write user configuration and
delegation on behalf of users.

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

| Signature | Mutability | Returns |
| --- | --- | --- |
| `assetConfig(address arg0)` | `view` | `(uint256[],uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,uint256,(bool,uint256,uint256,uint256,uint256),address,bool)` |
| `assets(uint256 arg0)` | `view` | `address` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `canPerformLiteAction(address _signer)` | `view` | `bool` |
| `coreRipeGovVaultId()` | `view` | `uint256` |
| `deregisterAsset(address _asset)` | `nonpayable` | `bool` |
| `doesUndyLegoHaveAccess(address _wallet, address _legoAddr)` | `view` | `bool` |
| `genConfig()` | `view` | `(uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool)` |
| `genDebtConfig()` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256,(bool,uint256,uint256,uint256,uint256))` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getAssetLiqConfig(address _asset)` | `view` | `(bool,bool,bool,bool,bool,(bool,uint256,uint256,uint256,uint256),(uint256,address,address))` |
| `getAuctionBuyConfig(address _asset, address _recipient)` | `view` | `(bool,bool,bool,bool)` |
| `getBorrowConfig(address _user, address _caller)` | `view` | `(bool,bool,uint256,uint256,uint256,uint256,uint256,uint256,bool)` |
| `getClaimLootConfig(address _user, address _caller, address _ripeToken)` | `view` | `(bool,bool,uint256,uint256)` |
| `getDebtTerms(address _asset)` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256)` |
| `getDepositPointsConfig(address _asset)` | `view` | `(uint256,uint256,bool)` |
| `getDynamicBorrowRateConfig()` | `view` | `(uint256,uint256,uint256,uint256)` |
| `getFirstVaultIdForAsset(address _asset)` | `view` | `uint256` |
| `getGenAuctionParams()` | `view` | `(bool,uint256,uint256,uint256,uint256)` |
| `getGenLiqConfig()` | `view` | `(bool,uint256,uint256,uint256,uint256,(bool,uint256,uint256,uint256,uint256),(uint256,address,address)[],(uint256,address,address)[])` |
| `getLtvPaybackBuffer()` | `view` | `uint256` |
| `getNumAssets()` | `view` | `uint256` |
| `getPriceConfig()` | `view` | `(uint256,uint256[])` |
| `getPriceStaleTime()` | `view` | `uint256` |
| `getPriorityLiqAssetVaults()` | `view` | `(uint256,address)[]` |
| `getPriorityPriceSourceIds()` | `view` | `uint256[]` |
| `getPriorityStabVaults()` | `view` | `(uint256,address)[]` |
| `getPurchaseRipeBondConfig(address _user)` | `view` | `(address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256,uint256,uint256,bool,bool)` |
| `getRedeemCollateralConfig(address _asset, address _recipient)` | `view` | `(bool,bool,bool,uint256,bool)` |
| `getRepayConfig(address _user)` | `view` | `(bool,bool)` |
| `getRewardsConfig()` | `view` | `(bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `getRipeHq()` | `view` | `address` |
| `getStabPoolClaimsConfig(address _claimAsset, address _claimer, address _caller, address _ripeToken)` | `view` | `(bool,bool,bool,bool,uint256,uint256)` |
| `getStabPoolRedemptionsConfig(address _asset, address _recipient)` | `view` | `(bool,bool,bool,bool)` |
| `getTellerDepositConfig(uint256 _vaultId, address _asset, address _user)` | `view` | `(bool,bool,bool,bool,uint256,uint256,uint256,uint256,bool,uint256)` |
| `getTellerWithdrawConfig(address _asset, address _user, address _caller)` | `view` | `(bool,bool,bool,bool,uint256)` |
| `hrConfig()` | `view` | `(address,uint256,uint256,uint256,uint256,uint256)` |
| `indexOfAsset(address arg0)` | `view` | `uint256` |
| `indexOfLiteSigner(address arg0)` | `view` | `uint256` |
| `isPaused()` | `view` | `bool` |
| `isRipeGovVaultId(uint256 arg0)` | `view` | `bool` |
| `isStabVaultId(uint256 arg0)` | `view` | `bool` |
| `isSupportedAsset(address _asset)` | `view` | `bool` |
| `isSupportedAssetInVault(uint256 _vaultId, address _asset)` | `view` | `bool` |
| `liteSigners(uint256 arg0)` | `view` | `address` |
| `maxLtvDeviation()` | `view` | `uint256` |
| `numAssets()` | `view` | `uint256` |
| `numLiteSigners()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `preferredStabVaultId()` | `view` | `uint256` |
| `priorityLiqAssetVaults(uint256 arg0)` | `view` | `(uint256,address)` |
| `priorityPriceSourceIds(uint256 arg0)` | `view` | `uint256` |
| `priorityStabVaults(uint256 arg0)` | `view` | `(uint256,address)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `rewardsConfig()` | `view` | `(bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `ripeBondConfig()` | `view` | `(address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256)` |
| `ripeGovVaultConfig(address arg0)` | `view` | `((uint256,uint256,uint256,bool,uint256),uint256,bool)` |
| `setAssetConfig(address _asset, (uint256[],uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,uint256,(bool,uint256,uint256,uint256,uint256),address,bool) _config)` | `nonpayable` | — |
| `setCanPerformLiteAction(address _signer, bool _canDo)` | `nonpayable` | — |
| `setCoreRipeGovVaultId(uint256 _vaultId)` | `nonpayable` | — |
| `setGeneralConfig((uint256,uint256,uint256,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool) _config)` | `nonpayable` | — |
| `setGeneralDebtConfig((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256,(bool,uint256,uint256,uint256,uint256)) _config)` | `nonpayable` | — |
| `setHrConfig((address,uint256,uint256,uint256,uint256,uint256) _config)` | `nonpayable` | — |
| `setPreferredStabVaultId(uint256 _vaultId)` | `nonpayable` | — |
| `setPriorityLiqAssetVaults((uint256,address)[] _priorityLiqAssetVaults)` | `nonpayable` | — |
| `setPriorityPriceSourceIds(uint256[] _priorityIds)` | `nonpayable` | — |
| `setPriorityStabVaults((uint256,address)[] _priorityStabVaults)` | `nonpayable` | — |
| `setRipeBondConfig((address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256) _config)` | `nonpayable` | — |
| `setRipeGovVaultConfig(address _asset, uint256 _assetWeight, bool _shouldFreezeWhenBadDebt, (uint256,uint256,uint256,bool,uint256) _lockTerms)` | `nonpayable` | — |
| `setRipeRewardsConfig((bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _config)` | `nonpayable` | — |
| `setShouldCheckLastTouch(bool _shouldCheck)` | `nonpayable` | — |
| `setTrainingWheels(address _trainingWheels)` | `nonpayable` | — |
| `setUnderscoreRegistry(address _underscoreRegistry)` | `nonpayable` | — |
| `setUserConfig(address _user, (bool,bool,bool) _config)` | `nonpayable` | — |
| `setUserDelegation(address _user, address _delegate, (bool,bool,bool,bool) _config)` | `nonpayable` | — |
| `shouldCheckLastTouch()` | `view` | `bool` |
| `totalPointsAllocs()` | `view` | `(uint256,uint256)` |
| `trainingWheels()` | `view` | `address` |
| `underscoreRegistry()` | `view` | `address` |
| `userConfig(address arg0)` | `view` | `(bool,bool,bool)` |
| `userDelegation(address arg0, address arg1)` | `view` | `(bool,bool,bool,bool)` |

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

<!-- END GENERATED API REFERENCE: MissionControl -->
