# SwitchboardBravo

`SwitchboardBravo` governs collateral onboarding and the timelocked update of
asset deposit, liquidation, debt, and whitelist configuration in
MissionControl.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/SwitchboardBravo.vy)

## Action model

Bravo supports five timelocked action types:

1. add a new asset;
2. update deposit/vault/points parameters;
3. update liquidation routing;
4. update debt terms; and
5. update an asset whitelist.

Only governance may propose, execute, or cancel. Each proposal binds its target
MissionControl address and is re-read and revalidated at execution. Expired
actions are cancelled.

When a newly added fungible asset has no PriceDesk token scale, execution calls
`syncTokenScale` after storing the asset configuration.

## Asset validation

Deposit configuration requires nonzero finite user/global limits, user limit no
greater than the global limit, minimum balance no greater than the user limit,
valid VaultBook IDs, and combined staker/voter allocations no greater than
100%. A nonzero staker allocation also requires either the current core RipeGov
vault or an ID historically classified as a StabilityPool.

Liquidation configuration enforces the route combinations used by the
liquidation engine:

- StabilityPool swapping implies immediate auction fallback;
- only GREEN or Savings GREEN may be burned as payment;
- assets transferred to Endaoment cannot be GREEN or Savings GREEN;
- NFTs cannot use StabilityPool swapping;
- collateral redemption requires a non-NFT asset with nonzero LTV that is not
  marked for Endaoment transfer; and
- custom auction parameters must pass SwitchboardAlpha validation.

A special StabilityPool ID must resolve to a registered, unpaused contract with
the expected claim and vault getters. If it already has a stabilization asset,
that pool cannot also register the proposed collateral as principal, and a new
claim pair is rejected when the active claim-asset count is already 20. These
are structural configuration checks; reservation, custody, value, and
liquidation-acceptance checks remain the StabilityPool settlement path's job.

## Directional debt-term rails

Debt terms must preserve the ordering
`LTV <= redemption threshold <= liquidation threshold`, keep the liquidation
threshold plus fee at or below 100%, and satisfy the remaining percentage and
nonzero constraints.

`maxLtvDeviation` is directional:

| Change | Restricted direction |
| --- | --- |
| LTV | Decreases are step-limited; increases are not |
| Redemption threshold | Decreases are step-limited; increases are not |
| Liquidation threshold | Decreases are step-limited; increases are not |
| Borrow rate | Increases are step-limited; decreases are not |

These are risk-direction rails, not a symmetric absolute-difference band. A
previously nonzero LTV cannot be set to zero. A zero deviation disables the step
size checks, but not the structural debt-term invariants.

The same directional checks run when the action is proposed and again against
the then-current debt terms when it executes. Multiple queued actions therefore
cannot bypass the rail by validating against a stale common baseline.

## Whitelists and lifecycle

A nonzero whitelist must expose the generic `isUserAllowed(user, asset)`
surface. An allocated asset remains governed by MissionControl until a separate
SwitchboardCharlie deregistration action removes it.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardBravo -->
## Exact API reference

> Generated from `contracts/config/SwitchboardBravo.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, tuple _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId, tuple _customAuctionParams, address _whitelist, bool _isNft, address _missionControl)` | `6–23` | `_minDepositBalance`, `_debtTerms`, `_shouldBurnAsPayment`, `_shouldTransferToEndaoment`, `_shouldSwapInStabPools`, `_shouldAuctionInstantly`, `_canDeposit`, `_canWithdraw`, `_canRedeemCollateral`, `_canRedeemInStabPool`, `_canBuyInAuction`, `_canClaimInStabPool`, `_specialStabPoolId`, `_customAuctionParams`, `_whitelist`, `_isNft`, `_missionControl` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `setAssetDebtTerms(address _asset, uint256 _ltv, uint256 _redemptionThreshold, uint256 _liqThreshold, uint256 _liqFee, uint256 _borrowRate, uint256 _daowry, address _missionControl)` | `7–8` | `_missionControl` |
| `setAssetDepositParams(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, address _missionControl)` | `7–8` | `_missionControl` |
| `setAssetLiqConfig(address _asset, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, uint256 _specialStabPoolId, tuple _customAuctionParams, address _missionControl)` | `5–8` | `_specialStabPoolId`, `_customAuctionParams`, `_missionControl` |
| `setWhitelistForAsset(address _asset, address _whitelist, address _missionControl)` | `2–3` | `_missionControl` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `actionType(uint256 arg0)` | `view` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams, address _whitelist)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams, address _whitelist, bool _isNft)` | `nonpayable` | `uint256` |
| `addAsset(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, (uint256,uint256,uint256,uint256,uint256,uint256) _debtTerms, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, bool _canDeposit, bool _canWithdraw, bool _canRedeemCollateral, bool _canRedeemInStabPool, bool _canBuyInAuction, bool _canClaimInStabPool, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams, address _whitelist, bool _isNft, address _missionControl)` | `nonpayable` | `uint256` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `executePendingAction(uint256 _aid)` | `nonpayable` | `bool` |
| `expiration()` | `view` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getGovernors()` | `view` | `address[]` |
| `getRipeHqFromGov()` | `view` | `address` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` |
| `hasPendingGovChange()` | `view` | `bool` |
| `isExpired(uint256 _actionId)` | `view` | `bool` |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingAssetConfig(uint256 arg0)` | `view` | `(address,(uint256[],uint256,uint256,uint256,uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,uint256,(bool,uint256,uint256,uint256,uint256),address,bool))` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingMissionControl(uint256 arg0)` | `view` | `address` |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setAssetDebtTerms(address _asset, uint256 _ltv, uint256 _redemptionThreshold, uint256 _liqThreshold, uint256 _liqFee, uint256 _borrowRate, uint256 _daowry)` | `nonpayable` | `uint256` |
| `setAssetDebtTerms(address _asset, uint256 _ltv, uint256 _redemptionThreshold, uint256 _liqThreshold, uint256 _liqFee, uint256 _borrowRate, uint256 _daowry, address _missionControl)` | `nonpayable` | `uint256` |
| `setAssetDepositParams(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance)` | `nonpayable` | `uint256` |
| `setAssetDepositParams(address _asset, uint256[] _vaultIds, uint256 _stakersPointsAlloc, uint256 _voterPointsAlloc, uint256 _perUserDepositLimit, uint256 _globalDepositLimit, uint256 _minDepositBalance, address _missionControl)` | `nonpayable` | `uint256` |
| `setAssetLiqConfig(address _asset, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly)` | `nonpayable` | `uint256` |
| `setAssetLiqConfig(address _asset, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, uint256 _specialStabPoolId)` | `nonpayable` | `uint256` |
| `setAssetLiqConfig(address _asset, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams)` | `nonpayable` | `uint256` |
| `setAssetLiqConfig(address _asset, bool _shouldBurnAsPayment, bool _shouldTransferToEndaoment, bool _shouldSwapInStabPools, bool _shouldAuctionInstantly, uint256 _specialStabPoolId, (bool,uint256,uint256,uint256,uint256) _customAuctionParams, address _missionControl)` | `nonpayable` | `uint256` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setWhitelistForAsset(address _asset, address _whitelist)` | `nonpayable` | `uint256` |
| `setWhitelistForAsset(address _asset, address _whitelist, address _missionControl)` | `nonpayable` | `uint256` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `AssetAdded` | `address asset indexed` |
| `AssetDebtTermsSet` | `address asset indexed, uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry` |
| `AssetDepositParamsSet` | `address asset indexed, uint256 numVaultIds, uint256 stakersPointsAlloc, uint256 voterPointsAlloc, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 minDepositBalance` |
| `AssetLiqConfigSet` | `address asset indexed, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, uint256 specialStabPoolId, uint256 auctionStartDiscount, uint256 auctionMaxDiscount, uint256 auctionDelay, uint256 auctionDuration` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewAssetPending` | `address asset indexed, uint256 numVaults, uint256 stakersPointsAlloc, uint256 voterPointsAlloc, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 minDepositBalance, uint256 debtTermsLtv, uint256 debtTermsRedemptionThreshold, uint256 debtTermsLiqThreshold, uint256 debtTermsLiqFee, uint256 debtTermsBorrowRate, uint256 debtTermsDaowry, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, bool canDeposit, bool canWithdraw, bool canRedeemCollateral, bool canRedeemInStabPool, bool canBuyInAuction, bool canClaimInStabPool, uint256 specialStabPoolId, uint256 auctionStartDiscount, uint256 auctionMaxDiscount, uint256 auctionDelay, uint256 auctionDuration, address whitelist, bool isNft` |
| `PendingAssetDebtTermsChange` | `address asset indexed, uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry, uint256 confirmationBlock, uint256 actionId` |
| `PendingAssetDepositParamsChange` | `address asset indexed, uint256 numVaultIds, uint256 stakersPointsAlloc, uint256 voterPointsAlloc, uint256 perUserDepositLimit, uint256 globalDepositLimit, uint256 minDepositBalance, uint256 confirmationBlock, uint256 actionId` |
| `PendingAssetLiqConfigChange` | `address asset indexed, bool shouldBurnAsPayment, bool shouldTransferToEndaoment, bool shouldSwapInStabPools, bool shouldAuctionInstantly, uint256 specialStabPoolId, uint256 auctionStartDiscount, uint256 auctionMaxDiscount, uint256 auctionDelay, uint256 auctionDuration, uint256 confirmationBlock, uint256 actionId` |
| `PendingAssetWhitelistChange` | `address asset indexed, address whitelist indexed, uint256 confirmationBlock, uint256 actionId` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `WhitelistAssetSet` | `address asset indexed, address whitelist indexed` |

### Structs declared by this source

- `AssetUpdate(asset: address, config: cs.AssetConfig)`

<!-- END GENERATED API REFERENCE: SwitchboardBravo -->
