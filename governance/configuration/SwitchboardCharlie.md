# SwitchboardCharlie

`SwitchboardCharlie` combines emergency controls, keeper-style maintenance, and
timelocked operational governance. Charlie is also the authority for
changing the current core RipeGov and preferred StabilityPool vault pointers.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/SwitchboardCharlie.vy)

## Directional lite access

Governance can perform every Charlie operation. MissionControl lite signers may
perform selected immediate maintenance and risk-reducing actions:

- pause, blacklist, and lock accounts, but not unpause, unblacklist, or unlock;
- disable per-asset operation flags, but not re-enable them;
- update debt, rewards, and deposit points and claim loot;
- distribute Underscore rewards; and
- disable Underscore rewards, but not enable them.

This asymmetry is deliberate: lite authority can contain risk or advance
accounting, while governance is required to restore permissions.

## Timelocked actions

Governance uses the inherited TimeLock for:

- single or batch Department fund recovery;
- starting or pausing single or batch fungible auctions;
- changing the TrainingWheels pointer;
- changing the current core RipeGov or preferred StabilityPool ID;
- deregistering an asset or a vault/asset pair;
- changing Lootbox Underscore interval/reward amounts; and
- writing a user's public-action configuration or delegation.

MissionControl-targeted proposals bind the resolved target at proposal and
re-use it at execution. Charlie revalidates state-sensitive vault pointers when
the delay elapses.

TrainingWheels membership has a separate immediate route:
`setManyTrainingWheelsAccess` lets governance, but not a lite signer, update up
to 25 users in one call. The TrainingWheels contract pointer itself remains a
timelocked change.

## Core RipeGov pointer

The proposed ID must be nonzero, currently valid in VaultBook, resolve to a
contract, differ from the current pointer, support RIPE in MissionControl, expose
the RipeGov points interface, and be unpaused. The checks run both at proposal
and execution.

After execution, MissionControl updates `coreRipeGovVaultId` but keeps both the
old and new IDs marked in the monotonic `isRipeGovVaultId` classification. The
old vault is not implicitly disabled or emptied.

## Preferred StabilityPool pointer

The new preferred ID must resolve to a registered VaultBook contract that
supports Savings GREEN, exposes the StabilityPool surface, is unpaused, and has
no Savings GREEN reserved as a claim asset. Execution changes
`preferredStabVaultId` and marks the new ID as a historical StabilityPool ID; it
does not clear the prior ID's classification or balances.

## Deregistration and user state

MissionControl asset deregistration is timelocked and fails if the asset still
has active staker or voter point allocations. Vault-asset deregistration calls
the target vault's own cleanup logic. User config and delegation writes are
governance recovery/administration paths; ordinary users normally update them
through Teller.

## Contract boundary

Charlie does not own Endaoment liquidity, swap, or treasury action selectors.
Those routes belong to SwitchboardEcho.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardCharlie -->
## Exact API reference

> Generated from `contracts/config/SwitchboardCharlie.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `deregisterAsset(address _asset, address _missionControl)` | `1–2` | `_missionControl` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `setCanBuyInAuctionAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCanClaimInStabPoolAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCanDepositAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCanRedeemCollateralAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCanRedeemInStabPoolAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCanWithdrawAsset(address _asset, bool _shouldEnable, address _missionControl)` | `2–3` | `_missionControl` |
| `setCoreRipeGovVaultId(uint256 _newVaultId, address _missionControl)` | `1–2` | `_missionControl` |
| `setPreferredStabVaultId(uint256 _newVaultId, address _missionControl)` | `1–2` | `_missionControl` |
| `setTrainingWheels(address _trainingWheels, address _missionControl)` | `1–2` | `_missionControl` |
| `setUserConfig(address _user, tuple _config, address _missionControl)` | `2–3` | `_missionControl` |
| `setUserDelegation(address _user, address _delegate, tuple _config, address _missionControl)` | `3–4` | `_missionControl` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `actionType(uint256 arg0)` | `view` | `uint256` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` |
| `claimDepositLootForAsset(address _user, uint256 _vaultId, address _asset)` | `nonpayable` | `uint256` |
| `claimLootForManyUsers(address[] _users, bool _shouldStake)` | `nonpayable` | `uint256` |
| `claimLootForUser(address _user, bool _shouldStake)` | `nonpayable` | `uint256` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `deregisterAsset(address _asset)` | `nonpayable` | `uint256` |
| `deregisterAsset(address _asset, address _missionControl)` | `nonpayable` | `uint256` |
| `deregisterVaultAsset(address _vaultAddr, address _asset)` | `nonpayable` | `uint256` |
| `distributeUnderscoreRewards()` | `nonpayable` | `bool` |
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
| `pause(address _contractAddr, bool _shouldPause)` | `nonpayable` | `bool` |
| `pauseAuction(address _liqUser, uint256 _vaultId, address _asset)` | `nonpayable` | `uint256` |
| `pauseManyAuctions((address,uint256,address)[] _auctions)` | `nonpayable` | `uint256` |
| `pendingActions(uint256 arg0)` | `view` | `(uint256,uint256,uint256)` |
| `pendingCoreRipeGovVaultId(uint256 arg0)` | `view` | `uint256` |
| `pendingDeregisterAsset(uint256 arg0)` | `view` | `address` |
| `pendingDeregisterVaultAsset(uint256 arg0)` | `view` | `(address,address)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingMissionControl(uint256 arg0)` | `view` | `address` |
| `pendingPauseAuctionActions(uint256 arg0)` | `view` | `(address,uint256,address)` |
| `pendingPauseManyAuctionsActions(uint256 arg0, uint256 arg1)` | `view` | `(address,uint256,address)` |
| `pendingPreferredStabVaultId(uint256 arg0)` | `view` | `uint256` |
| `pendingRecoverFundsActions(uint256 arg0)` | `view` | `(address,address,address)` |
| `pendingRecoverFundsManyActions(uint256 arg0)` | `view` | `(address,address,address[])` |
| `pendingStartAuctionActions(uint256 arg0)` | `view` | `(address,uint256,address)` |
| `pendingStartManyAuctionsActions(uint256 arg0, uint256 arg1)` | `view` | `(address,uint256,address)` |
| `pendingTrainingWheels(uint256 arg0)` | `view` | `address` |
| `pendingUnderscoreSendInterval(uint256 arg0)` | `view` | `uint256` |
| `pendingUndyDepositRewardsAmount(uint256 arg0)` | `view` | `uint256` |
| `pendingUndyYieldBonusAmount(uint256 arg0)` | `view` | `uint256` |
| `pendingUserConfig(uint256 arg0)` | `view` | `(address,(bool,bool,bool))` |
| `pendingUserDelegation(uint256 arg0)` | `view` | `(address,address,(bool,bool,bool,bool))` |
| `recoverFunds(address _contractAddr, address _recipient, address _asset)` | `nonpayable` | `uint256` |
| `recoverFundsMany(address _contractAddr, address _recipient, address[] _assets)` | `nonpayable` | `uint256` |
| `relinquishGov()` | `nonpayable` | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setBlacklist(address _tokenAddr, address _addr, bool _shouldBlacklist)` | `nonpayable` | `bool` |
| `setCanBuyInAuctionAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanBuyInAuctionAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCanClaimInStabPoolAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanClaimInStabPoolAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCanDepositAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanDepositAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCanRedeemCollateralAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanRedeemCollateralAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCanRedeemInStabPoolAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanRedeemInStabPoolAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCanWithdrawAsset(address _asset, bool _shouldEnable)` | `nonpayable` | `bool` |
| `setCanWithdrawAsset(address _asset, bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` |
| `setCoreRipeGovVaultId(uint256 _newVaultId)` | `nonpayable` | `uint256` |
| `setCoreRipeGovVaultId(uint256 _newVaultId, address _missionControl)` | `nonpayable` | `uint256` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setHasUnderscoreRewards(bool _hasRewards)` | `nonpayable` | `bool` |
| `setLockedAccount(address _wallet, bool _shouldLock)` | `nonpayable` | `bool` |
| `setManyTrainingWheelsAccess(address _addr, (address,bool)[] _trainingWheels)` | `nonpayable` | — |
| `setPreferredStabVaultId(uint256 _newVaultId)` | `nonpayable` | `uint256` |
| `setPreferredStabVaultId(uint256 _newVaultId, address _missionControl)` | `nonpayable` | `uint256` |
| `setTrainingWheels(address _trainingWheels)` | `nonpayable` | `uint256` |
| `setTrainingWheels(address _trainingWheels, address _missionControl)` | `nonpayable` | `uint256` |
| `setUnderscoreSendInterval(uint256 _interval)` | `nonpayable` | `uint256` |
| `setUndyDepositRewardsAmount(uint256 _amount)` | `nonpayable` | `uint256` |
| `setUndyYieldBonusAmount(uint256 _amount)` | `nonpayable` | `uint256` |
| `setUserConfig(address _user, (bool,bool,bool) _config)` | `nonpayable` | `uint256` |
| `setUserConfig(address _user, (bool,bool,bool) _config, address _missionControl)` | `nonpayable` | `uint256` |
| `setUserDelegation(address _user, address _delegate, (bool,bool,bool,bool) _config)` | `nonpayable` | `uint256` |
| `setUserDelegation(address _user, address _delegate, (bool,bool,bool,bool) _config, address _missionControl)` | `nonpayable` | `uint256` |
| `startAuction(address _liqUser, uint256 _vaultId, address _asset)` | `nonpayable` | `uint256` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |
| `startManyAuctions((address,uint256,address)[] _auctions)` | `nonpayable` | `uint256` |
| `updateDebtForManyUsers(address[] _users)` | `nonpayable` | `bool` |
| `updateDebtForUser(address _user)` | `nonpayable` | `bool` |
| `updateDepositPoints(address _user, uint256 _vaultId, address _asset)` | `nonpayable` | `bool` |
| `updateManyDepositPoints(address[] _users, uint256 _vaultId, address _asset)` | `nonpayable` | `bool` |
| `updateRipeRewards()` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `AssetDeregistered` | `address asset indexed` |
| `BlacklistSet` | `address tokenAddr indexed, address addr indexed, bool isBlacklisted, address caller indexed` |
| `CanBuyInAuctionAssetSet` | `address asset indexed, bool canBuyInAuction, address caller indexed` |
| `CanClaimInStabPoolAssetSet` | `address asset indexed, bool canClaimInStabPool, address caller indexed` |
| `CanDepositAssetSet` | `address asset indexed, bool canDeposit, address caller indexed` |
| `CanRedeemCollateralAssetSet` | `address asset indexed, bool canRedeemCollateral, address caller indexed` |
| `CanRedeemInStabPoolAssetSet` | `address asset indexed, bool canRedeemInStabPool, address caller indexed` |
| `CanWithdrawAssetSet` | `address asset indexed, bool canWithdraw, address caller indexed` |
| `CoreRipeGovVaultIdSet` | `uint256 previousVaultId, uint256 newVaultId, address newVaultAddr` |
| `DebtUpdatedForManyUsers` | `uint256 numUsers, address caller indexed` |
| `DebtUpdatedForUser` | `address user indexed, bool success, address caller indexed` |
| `DepositLootClaimedForAsset` | `address user indexed, uint256 vaultId, address asset indexed, uint256 ripeAmount, address caller indexed` |
| `DepositPointsUpdated` | `address user indexed, uint256 vaultId, address asset indexed, address caller indexed` |
| `DepositPointsUpdatedMany` | `uint256 numUsers, uint256 vaultId, address asset indexed, address caller indexed` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `HasUnderscoreRewardsSet` | `bool hasRewards, address caller indexed` |
| `LockedAccountSet` | `address wallet indexed, bool isLocked, address caller indexed` |
| `LootClaimedForManyUsers` | `uint256 numUsers, address caller indexed, bool shouldStake, uint256 totalRipeAmount` |
| `LootClaimedForUser` | `address user indexed, address caller indexed, bool shouldStake, uint256 ripeAmount` |
| `PauseAuctionExecuted` | `address liqUser indexed, uint256 vaultId, address asset indexed, bool success` |
| `PauseExecuted` | `address contractAddr indexed, bool shouldPause` |
| `PauseManyAuctionsExecuted` | `uint256 numAuctionsPaused` |
| `PendingCoreRipeGovVaultIdChange` | `uint256 previousVaultId, uint256 newVaultId, address newVaultAddr, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeregisterAssetAction` | `address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeregisterVaultAssetAction` | `address vaultAddr indexed, address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingPauseAuctionAction` | `address liqUser indexed, uint256 vaultId, address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingPauseManyAuctionsAction` | `uint256 numAuctions, uint256 confirmationBlock, uint256 actionId` |
| `PendingPreferredStabVaultIdChange` | `uint256 previousVaultId, uint256 newVaultId, address newVaultAddr, uint256 confirmationBlock, uint256 actionId` |
| `PendingRecoverFundsAction` | `address contractAddr indexed, address recipient indexed, address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingRecoverFundsManyAction` | `address contractAddr indexed, address recipient indexed, uint256 numAssets, uint256 confirmationBlock, uint256 actionId` |
| `PendingStartAuctionAction` | `address liqUser indexed, uint256 vaultId, address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingStartManyAuctionsAction` | `uint256 numAuctions, uint256 confirmationBlock, uint256 actionId` |
| `PendingTrainingWheelsChange` | `address trainingWheels indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingUnderscoreSendIntervalAction` | `uint256 interval, uint256 confirmationBlock, uint256 actionId` |
| `PendingUndyDepositRewardsAmountAction` | `uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingUndyYieldBonusAmountAction` | `uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingUserConfigAction` | `address user indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingUserDelegationAction` | `address user indexed, address delegate indexed, uint256 confirmationBlock, uint256 actionId` |
| `PreferredStabVaultIdSet` | `uint256 previousVaultId, uint256 newVaultId, address newVaultAddr` |
| `RecoverFundsExecuted` | `address contractAddr indexed, address recipient indexed, address asset indexed` |
| `RecoverFundsManyExecuted` | `address contractAddr indexed, address recipient indexed, uint256 numAssets` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `RipeRewardsUpdated` | `address caller indexed, bool success` |
| `StartAuctionExecuted` | `address liqUser indexed, uint256 vaultId, address asset indexed, bool success` |
| `StartManyAuctionsExecuted` | `uint256 numAuctionsStarted` |
| `TrainingWheelsAccessSet` | `address trainingWheels indexed, address user indexed, bool isAllowed` |
| `TrainingWheelsSet` | `address trainingWheels indexed` |
| `UnderscoreRewardsDistributed` | `address caller indexed, bool success` |
| `UnderscoreSendIntervalSet` | `uint256 interval, address caller indexed` |
| `UndyDepositRewardsAmountSet` | `uint256 amount, address caller indexed` |
| `UndyYieldBonusAmountSet` | `uint256 amount, address caller indexed` |
| `UserConfigSet` | `address user indexed, address caller indexed` |
| `UserDelegationSet` | `address user indexed, address delegate indexed, address caller indexed` |
| `VaultAssetDeregistered` | `address vaultAddr indexed, address asset indexed` |

### Structs declared by this source

- `RecoverFundsAction(contractAddr: address, recipient: address, asset: address)`
- `RecoverFundsManyAction(contractAddr: address, recipient: address, assets: DynArray[address, MAX_RECOVER_ASSETS])`
- `FungAuctionConfig(liqUser: address, vaultId: uint256, asset: address)`
- `TrainingWheelAccess(user: address, isAllowed: bool)`
- `DeregisterVaultAssetAction(vaultAddr: address, asset: address)`
- `UserConfigAction(user: address, config: cs.UserConfig)`
- `UserDelegationAction(user: address, delegate: address, config: cs.ActionDelegation)`

<!-- END GENERATED API REFERENCE: SwitchboardCharlie -->
