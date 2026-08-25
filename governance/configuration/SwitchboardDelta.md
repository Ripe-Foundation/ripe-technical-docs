# SwitchboardDelta

`SwitchboardDelta` governs deleveraging, Human Resources, RIPE bonds, reward
budgets, bond boosters, Lootbox resets, and Underscore integration settings.
It combines immediate direction-limited operations with timelocked policy
changes.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/config/SwitchboardDelta.vy)

## Deleveraging

Governance or a lite signer may call the bounded `deleverageManyUsers` and
`deleverageWithSpecificAssets` Teller routes. The volatile-asset route is
governance-only and calls Deleverage directly. Delta has no single-user
`deleverageUser` selector.

Those Delta helpers are governance conveniences, not exclusive Teller
authority. Any caller can enter Teller's general batch, where an untrusted
request succeeds only for a non-liquidating near-redemption target and is
repayment-capped. Teller's specific-asset route separately requires self,
registered-Ripe, or `canBorrow` authority.

All deleverage policy changes are timelocked:

- minimum deleverage basis points and general buffer;
- cooldown;
- Underscore safe-spread basis points;
- full-payoff buffer;
- overage basis points; and
- dust threshold and dust basis points.

Hard ceilings include 7,200 blocks for cooldown, 500 bps for safe spread,
overage, and dust ratio, `1e18` for the full-payoff USD buffer, and `1e16` for
the dust USD threshold. These are raw on-chain units; block wall time depends on
the target chain.

## Human Resources

Timelocked HR configuration covers contributor template, maximum compensation,
minimum cliff, maximum start delay, and vesting boundaries. Execution re-reads
the target MissionControl configuration and rejects an infeasible cliff above
the effective maximum vesting length. MissionControl-targeted proposals bind
their resolved target.

Contributor-specific manager and paycheck cancellation changes are timelocked.
Cash-check, RIPE-transfer cancellation, and ownership-change cancellation are
immediate actions available to governance or a MissionControl lite signer.
Freezing is likewise lite-safe, while unfreezing requires governance.

## RIPE bonds and budgets

Timelocked bond policy includes the payment asset, epoch amount, price bounds,
lock bonus, automatic-restart flag/delay, epoch length, bad debt, and BondBooster
contract/configuration. `setStartEpochAtBlock` is an immediate governance call
that starts no earlier than the current block. Delta does not expose a
`restartBondEpoch` selector.

Disabling bond purchases is lite-safe; enabling them requires governance.
Changes to Ledger's RIPE budgets for rewards, HR, and bonds are timelocked.

## Booster and Lootbox maintenance

Booster additions and boundary changes are timelocked. Governance or a lite
signer may immediately remove one or many boosters; changing the minimum lock
duration is immediate but governance-only. User-balance, asset-point, and
user-borrow-point reset batches are timelocked and bounded.

## Underscore integration

Changing MissionControl's Underscore registry or `shouldCheckLastTouch` policy
is timelocked. A nonzero Underscore registry must be a contract and pass Ledger,
root-registry, optional vault-registry, and optional LegoBook interface probes;
the zero address is an allowed explicit disable.

## Execution model

Expired actions are cancelled. Delta re-reads the latest target configuration
at execution so each action changes only its intended fields, and it applies
execution-time HR feasibility checks before committing state.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardDelta -->
## Exact API reference

> Generated from `contracts/config/SwitchboardDelta.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock` |
| `setCanPurchaseRipeBond(bool _canBond, address _missionControl)` | `1–2` | `_missionControl` |
| `setContributorTemplate(address _contribTemplate, address _missionControl)` | `1–2` | `_missionControl` |
| `setMaxCompensation(uint256 _maxComp, address _missionControl)` | `1–2` | `_missionControl` |
| `setMaxStartDelay(uint256 _maxStartDelay, address _missionControl)` | `1–2` | `_missionControl` |
| `setMinCliffLength(uint256 _minCliffLength, address _missionControl)` | `1–2` | `_missionControl` |
| `setRipeBondConfig(address _asset, uint256 _amountPerEpoch, uint256 _minRipePerUnit, uint256 _maxRipePerUnit, uint256 _maxRipePerUnitLockBonus, bool _shouldAutoRestart, uint256 _restartDelayBlocks, address _missionControl)` | `7–8` | `_missionControl` |
| `setRipeBondEpochLength(uint256 _epochLength, address _missionControl)` | `1–2` | `_missionControl` |
| `setShouldCheckLastTouch(bool _shouldCheck, address _missionControl)` | `1–2` | `_missionControl` |
| `setStartEpochAtBlock(uint256 _block)` | `0–1` | `_block` |
| `setUnderscoreRegistry(address _underscoreRegistry, address _missionControl)` | `1–2` | `_missionControl` |
| `setVestingLengthBoundaries(uint256 _minVestingLength, uint256 _maxVestingLength, address _missionControl)` | `2–3` | `_missionControl` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `actionId()` | `view` | `uint256` |
| `actionTimeLock()` | `view` | `uint256` |
| `actionType(uint256 arg0)` | `view` | `uint256` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` |
| `canGovern(address _addr)` | `view` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelOwnershipChangeForContributor(address _contributor)` | `nonpayable` | `bool` |
| `cancelPaycheckForContributor(address _contributor)` | `nonpayable` | `uint256` |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` |
| `cancelRipeTransferForContributor(address _contributor)` | `nonpayable` | `bool` |
| `cashRipeCheckForContributor(address _contributor)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `deleverageManyUsers((address,uint256)[] _users)` | `nonpayable` | `uint256` |
| `deleverageWithSpecificAssets((uint256,address,uint256)[] _assets, address _user)` | `nonpayable` | `uint256` |
| `deleverageWithVolAssets(address _user, (uint256,address,uint256)[] _assets)` | `nonpayable` | `uint256` |
| `executePendingAction(uint256 _aid)` | `nonpayable` | `bool` |
| `expiration()` | `view` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `freezeContributor(address _contributor, bool _shouldFreeze)` | `nonpayable` | `bool` |
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
| `pendingAssetReset(uint256 arg0, uint256 arg1)` | `view` | `(address,uint256)` |
| `pendingBondBooster(uint256 arg0)` | `view` | `address` |
| `pendingBoosterBoundaries(uint256 arg0)` | `view` | `(uint256,uint256)` |
| `pendingBoosterConfigs(uint256 arg0, uint256 arg1)` | `view` | `(address,uint256,uint256,uint256)` |
| `pendingCancelPaycheck(uint256 arg0)` | `view` | `address` |
| `pendingDeleverageBuffer(uint256 arg0)` | `view` | `uint256` |
| `pendingDeleverageCooldown(uint256 arg0)` | `view` | `uint256` |
| `pendingDeleverageDustBps(uint256 arg0)` | `view` | `uint256` |
| `pendingDeleverageDustThreshold(uint256 arg0)` | `view` | `uint256` |
| `pendingDeleverageFullPayoffBuffer(uint256 arg0)` | `view` | `uint256` |
| `pendingDeleverageOverageBps(uint256 arg0)` | `view` | `uint256` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingHrConfig(uint256 arg0)` | `view` | `(address,uint256,uint256,uint256,uint256,uint256)` |
| `pendingManager(uint256 arg0)` | `view` | `(address,address)` |
| `pendingMinDeleverageBps(uint256 arg0)` | `view` | `uint256` |
| `pendingMissionControl(uint256 arg0)` | `view` | `address` |
| `pendingRipeAvailable(uint256 arg0)` | `view` | `uint256` |
| `pendingRipeBondConfig(uint256 arg0)` | `view` | `(address,uint256,bool,uint256,uint256,uint256,uint256,bool,uint256)` |
| `pendingRipeBondConfigValue(uint256 arg0)` | `view` | `uint256` |
| `pendingShouldCheckLastTouch(uint256 arg0)` | `view` | `bool` |
| `pendingUnderscoreRegistry(uint256 arg0)` | `view` | `address` |
| `pendingUnderscoreSafeSpreadBps(uint256 arg0)` | `view` | `uint256` |
| `pendingUserBalanceReset(uint256 arg0, uint256 arg1)` | `view` | `(address,address,uint256)` |
| `pendingUserBorrowReset(uint256 arg0, uint256 arg1)` | `view` | `address` |
| `relinquishGov()` | `nonpayable` | — |
| `removeBondBooster(address _user)` | `nonpayable` | `bool` |
| `removeManyBondBoosters(address[] _users)` | `nonpayable` | `bool` |
| `resetManyAssetPoints((address,uint256)[] _assets)` | `nonpayable` | `uint256` |
| `resetManyUserBalancePoints((address,address,uint256)[] _users)` | `nonpayable` | `uint256` |
| `resetManyUserBorrowPoints(address[] _users)` | `nonpayable` | `uint256` |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `setBadDebt(uint256 _amount)` | `nonpayable` | `uint256` |
| `setBondBooster((address,uint256,uint256,uint256) _config)` | `nonpayable` | `uint256` |
| `setBoosterBoundaries(uint256 _maxBoostRatio, uint256 _maxUnits)` | `nonpayable` | `uint256` |
| `setBoosterMinLockDuration(uint256 _minLockDuration)` | `nonpayable` | `bool` |
| `setCanPurchaseRipeBond(bool _canBond)` | `nonpayable` | `bool` |
| `setCanPurchaseRipeBond(bool _canBond, address _missionControl)` | `nonpayable` | `bool` |
| `setContributorTemplate(address _contribTemplate)` | `nonpayable` | `uint256` |
| `setContributorTemplate(address _contribTemplate, address _missionControl)` | `nonpayable` | `uint256` |
| `setDeleverageBuffer(uint256 _bps)` | `nonpayable` | `uint256` |
| `setDeleverageCooldown(uint256 _blocks)` | `nonpayable` | `uint256` |
| `setDeleverageDustBps(uint256 _bps)` | `nonpayable` | `uint256` |
| `setDeleverageDustThreshold(uint256 _usdAmount)` | `nonpayable` | `uint256` |
| `setDeleverageFullPayoffBuffer(uint256 _usdAmount)` | `nonpayable` | `uint256` |
| `setDeleverageOverageBps(uint256 _bps)` | `nonpayable` | `uint256` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setManagerForContributor(address _contributor, address _manager)` | `nonpayable` | `uint256` |
| `setManyBondBoosters((address,uint256,uint256,uint256)[] _boosters)` | `nonpayable` | `uint256` |
| `setMaxCompensation(uint256 _maxComp)` | `nonpayable` | `uint256` |
| `setMaxCompensation(uint256 _maxComp, address _missionControl)` | `nonpayable` | `uint256` |
| `setMaxStartDelay(uint256 _maxStartDelay)` | `nonpayable` | `uint256` |
| `setMaxStartDelay(uint256 _maxStartDelay, address _missionControl)` | `nonpayable` | `uint256` |
| `setMinCliffLength(uint256 _minCliffLength)` | `nonpayable` | `uint256` |
| `setMinCliffLength(uint256 _minCliffLength, address _missionControl)` | `nonpayable` | `uint256` |
| `setMinDeleverageBps(uint256 _bps)` | `nonpayable` | `uint256` |
| `setRipeAvailableForBonds(uint256 _amount)` | `nonpayable` | `uint256` |
| `setRipeAvailableForHr(uint256 _amount)` | `nonpayable` | `uint256` |
| `setRipeAvailableForRewards(uint256 _amount)` | `nonpayable` | `uint256` |
| `setRipeBondBooster(address _bondBooster)` | `nonpayable` | `uint256` |
| `setRipeBondConfig(address _asset, uint256 _amountPerEpoch, uint256 _minRipePerUnit, uint256 _maxRipePerUnit, uint256 _maxRipePerUnitLockBonus, bool _shouldAutoRestart, uint256 _restartDelayBlocks)` | `nonpayable` | `uint256` |
| `setRipeBondConfig(address _asset, uint256 _amountPerEpoch, uint256 _minRipePerUnit, uint256 _maxRipePerUnit, uint256 _maxRipePerUnitLockBonus, bool _shouldAutoRestart, uint256 _restartDelayBlocks, address _missionControl)` | `nonpayable` | `uint256` |
| `setRipeBondEpochLength(uint256 _epochLength)` | `nonpayable` | `uint256` |
| `setRipeBondEpochLength(uint256 _epochLength, address _missionControl)` | `nonpayable` | `uint256` |
| `setShouldCheckLastTouch(bool _shouldCheck)` | `nonpayable` | `uint256` |
| `setShouldCheckLastTouch(bool _shouldCheck, address _missionControl)` | `nonpayable` | `uint256` |
| `setStartEpochAtBlock()` | `nonpayable` | — |
| `setStartEpochAtBlock(uint256 _block)` | `nonpayable` | — |
| `setUnderscoreRegistry(address _underscoreRegistry)` | `nonpayable` | `uint256` |
| `setUnderscoreRegistry(address _underscoreRegistry, address _missionControl)` | `nonpayable` | `uint256` |
| `setUnderscoreSafeSpreadBps(uint256 _bps)` | `nonpayable` | `uint256` |
| `setVestingLengthBoundaries(uint256 _minVestingLength, uint256 _maxVestingLength)` | `nonpayable` | `uint256` |
| `setVestingLengthBoundaries(uint256 _minVestingLength, uint256 _maxVestingLength, address _missionControl)` | `nonpayable` | `uint256` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `AssetResetExecuted` | `uint256 numResets` |
| `BadDebtSet` | `uint256 badDebt` |
| `BondBoosterRemoved` | `address user indexed` |
| `BoosterBoundariesSet` | `uint256 maxBoostRatio, uint256 maxUnits` |
| `BoosterMinLockDurationSet` | `uint256 minLockDuration` |
| `CanPurchaseRipeBondModified` | `bool canPurchaseRipeBond, address modifier indexed` |
| `ContributorFrozenFromSwitchboard` | `address contributor indexed, address frozenBy indexed, bool shouldFreeze` |
| `DeleverageBufferSet` | `uint256 bps` |
| `DeleverageCooldownSet` | `uint256 blocks` |
| `DeleverageDustBpsSet` | `uint256 bps` |
| `DeleverageDustThresholdSet` | `uint256 usdAmount` |
| `DeleverageFullPayoffBufferSet` | `uint256 usdAmount` |
| `DeleverageOverageBpsSet` | `uint256 bps` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `HrContribTemplateSet` | `address contribTemplate indexed` |
| `HrContributorCancelPaycheckSet` | `address contributor indexed` |
| `HrContributorManagerSet` | `address contributor indexed, address manager indexed` |
| `HrMaxCompensationSet` | `uint256 maxCompensation` |
| `HrMaxStartDelaySet` | `uint256 maxStartDelay` |
| `HrMinCliffLengthSet` | `uint256 minCliffLength` |
| `HrVestingLengthBoundariesSet` | `uint256 minVestingLength, uint256 maxVestingLength` |
| `ManyBondBoostersRemoved` | `uint256 numUsers` |
| `ManyBondBoostersSet` | `uint256 numBoosters` |
| `MinDeleverageBpsSet` | `uint256 bps` |
| `OwnershipChangeCancelledFromSwitchboard` | `address contributor indexed, address cancelledBy indexed` |
| `PendingAssetResetSet` | `uint256 numResets, uint256 confirmationBlock, uint256 actionId` |
| `PendingBadDebtSet` | `uint256 badDebt, uint256 confirmationBlock, uint256 actionId` |
| `PendingBondBoosterSet` | `address bondBooster indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingBoosterBoundariesSet` | `uint256 maxBoostRatio, uint256 maxUnits, uint256 confirmationBlock, uint256 actionId` |
| `PendingBoosterConfigSet` | `address user indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingBoosterConfigsSet` | `uint256 numBoosters, uint256 confirmationBlock, uint256 actionId` |
| `PendingCancelPaycheckSet` | `address contributor indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageBufferChange` | `uint256 bps, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageCooldownChange` | `uint256 blocks, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageDustBpsChange` | `uint256 bps, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageDustThresholdChange` | `uint256 usdAmount, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageFullPayoffBufferChange` | `uint256 usdAmount, uint256 confirmationBlock, uint256 actionId` |
| `PendingDeleverageOverageBpsChange` | `uint256 bps, uint256 confirmationBlock, uint256 actionId` |
| `PendingHrContribTemplateChange` | `address contribTemplate indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingHrMaxCompensationChange` | `uint256 maxCompensation, uint256 confirmationBlock, uint256 actionId` |
| `PendingHrMaxStartDelayChange` | `uint256 maxStartDelay, uint256 confirmationBlock, uint256 actionId` |
| `PendingHrMinCliffLengthChange` | `uint256 minCliffLength, uint256 confirmationBlock, uint256 actionId` |
| `PendingHrVestingLengthBoundariesChange` | `uint256 minVestingLength, uint256 maxVestingLength, uint256 confirmationBlock, uint256 actionId` |
| `PendingManagerSet` | `address contributor indexed, address manager indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingMinDeleverageBpsChange` | `uint256 bps, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeAvailableForBondsChange` | `uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeAvailableForHrChange` | `uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeAvailableForRewardsChange` | `uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeBondConfigSet` | `address asset indexed, uint256 amountPerEpoch, uint256 minRipePerUnit, uint256 maxRipePerUnit, uint256 maxRipePerUnitLockBonus, bool shouldAutoRestart, uint256 restartDelayBlocks, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeBondEpochLengthSet` | `uint256 epochLength, uint256 confirmationBlock, uint256 actionId` |
| `PendingShouldCheckLastTouchChange` | `bool shouldCheck, uint256 confirmationBlock, uint256 actionId` |
| `PendingUnderscoreRegistryChange` | `address underscoreRegistry, uint256 confirmationBlock, uint256 actionId` |
| `PendingUnderscoreSafeSpreadBpsChange` | `uint256 bps, uint256 confirmationBlock, uint256 actionId` |
| `PendingUserBalanceResetSet` | `uint256 numResets, uint256 confirmationBlock, uint256 actionId` |
| `PendingUserBorrowResetSet` | `uint256 numResets, uint256 confirmationBlock, uint256 actionId` |
| `RipeAvailableForBondsSet` | `uint256 amount` |
| `RipeAvailableForHrSet` | `uint256 amount` |
| `RipeAvailableForRewardsSet` | `uint256 amount` |
| `RipeBondBoosterSet` | `address bondBooster indexed` |
| `RipeBondConfigSet` | `address asset indexed, uint256 amountPerEpoch, uint256 minRipePerUnit, uint256 maxRipePerUnit, uint256 maxRipePerUnitLockBonus, bool shouldAutoRestart` |
| `RipeBondEpochLengthSet` | `uint256 epochLength` |
| `RipeBondStartEpochAtBlockSet` | `uint256 startBlock` |
| `RipeCheckCashedFromSwitchboard` | `address contributor indexed, address cashedBy indexed, uint256 amount` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `RipeTransferCancelledFromSwitchboard` | `address contributor indexed, address cancelledBy indexed` |
| `ShouldCheckLastTouchSet` | `bool shouldCheck` |
| `UnderscoreRegistrySet` | `address addr indexed` |
| `UnderscoreSafeSpreadBpsSet` | `uint256 bps` |
| `UserBalanceResetExecuted` | `uint256 numResets` |
| `UserBorrowResetExecuted` | `uint256 numResets` |

### Structs declared by this source

- `DeleverageUserRequest(user: address, targetRepayAmount: uint256)`
- `DeleverageAsset(vaultId: uint256, asset: address, targetRepayAmount: uint256)`
- `PendingManager(contributor: address, pendingManager: address)`
- `BoosterConfig(user: address, boostRatio: uint256, maxUnitsAllowed: uint256, expireBlock: uint256)`
- `UserBalanceReset(user: address, asset: address, vaultId: uint256)`
- `AssetReset(asset: address, vaultId: uint256)`
- `BoosterBoundaries(maxBoostRatio: uint256, maxUnits: uint256)`

<!-- END GENERATED API REFERENCE: SwitchboardDelta -->
