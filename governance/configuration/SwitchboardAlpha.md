# SwitchboardAlpha

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/SwitchboardAlpha.vy)

`SwitchboardAlpha` governs global, debt, rewards, price, priority-routing, lite
signer, and RipeGov asset policy. It composes `LocalGov` and `TimeLock` and
writes validated configuration to MissionControl or the relevant protocol
component.

## Access model

Governance can perform every Alpha action. MissionControl lite signers may only
perform explicitly risk-reducing immediate operations:

- disable global deposit, withdrawal, borrow, repay, loot, liquidation,
  collateral-redemption, StabilityPool, or auction flags;
- disable daowry or rewards points;
- add price snapshots; and
- continue to execute other explicitly lite-safe maintenance calls.

Re-enabling a disabled function requires governance. Granting a new lite signer
is timelocked; revoking one is immediate but still governance-only.

## Timelocked policy domains

Alpha stores an action type, the pending payload, and the target MissionControl
address under each action ID. An empty target parameter means "resolve the
current MissionControl now"; the resolved address is then bound to the proposal.
A pending action with no stored target falls back to current MissionControl at
execution.

| Domain | Timelocked changes |
| --- | --- |
| General | Per-user vault/asset limits and price stale time |
| Debt | Global limits, borrow interval, dynamic rates, `maxLtvDeviation`, keeper fees, LTV payback buffer, default auction parameters |
| Rewards | RIPE per block, allocation ratios, auto-stake parameters, StabilityPool claim reward |
| Routing | Priority liquidation vaults, priority StabilityPools, priority price-source IDs |
| Other | Add lite signer, RipeGov asset/lock configuration, Underscore vault discount, buyback ratio, Pyth confidence ratio |

The stale-time constructor bounds are immutable. Percentage allocations and
auto-stake ratios are basis points and are range-checked; auction delays are
bounded to protect downstream block arithmetic.

## Priority vault validation

Priority routes are validated at proposal and again at execution.

- Entries must resolve to valid VaultBook IDs and supported vault/asset pairs.
- Duplicate `(vaultId, asset)` pairs are rejected at proposal.
- Priority liquidation entries cannot use IDs historically classified as
  RipeGov or StabilityPool IDs.
- Priority StabilityPool entries must expose the expected claim/liquidation
  surface and must not be paused.

This distinction uses MissionControl's monotonic historical classifications,
not only its current `coreRipeGovVaultId` or `preferredStabVaultId` pointers.

## RipeGov configuration

RipeGov asset configuration is accepted only for a supported asset present in
the current core RipeGov vault. Alpha validates asset weight, lock ordering,
duration arithmetic, maximum boost, exit fee, and the relationship between
`canExit` and a nonzero exit fee. The current core vault ID is read from
MissionControl; no permanent vault ID is hardcoded in Alpha.

## Price operations

`setPriorityPriceSourceIds` is timelocked. At execution, invalid, disabled, and
duplicate source IDs are removed before storing the list. `addPriceSnapshot` is
an operational call available to governance or a lite signer and forwards to
the selected current PriceDesk source.

## Execution safety

Expired actions are cancelled instead of executed. State-sensitive data is
re-read before writing, and priority routes are revalidated after the delay.
Alpha's `maxLtvDeviation` value is consumed by SwitchboardBravo's directional
debt-term rails.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardAlpha -->
## Exact API reference

> Generated from `contracts/config/SwitchboardAlpha.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minStaleTime, uint256 _maxStaleTime, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock, uint256 _pythPricesId)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |
| `setAutoStakeParams(uint256 _autoStakeRatio, uint256 _autoStakeDurationRatio, uint256 _stabPoolRipePerDollarClaimed, address _missionControl)` | `3–4` | `_missionControl = empty(address)` |
| `setBorrowIntervalConfig(uint256 _maxBorrowPerInterval, uint256 _numBlocksPerInterval, address _missionControl)` | `2–3` | `_missionControl = empty(address)` |
| `setCanBorrow(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanBuyInAuction(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanClaimInStabPool(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanClaimLoot(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanDeposit(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanLiquidate(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanPerformLiteAction(address _user, bool _canDo, address _missionControl)` | `2–3` | `_missionControl = empty(address)` |
| `setCanRedeemCollateral(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanRedeemInStabPool(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanRepay(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setCanWithdraw(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setDynamicRateConfig(uint256 _minDynamicRateBoost, uint256 _maxDynamicRateBoost, uint256 _increasePerDangerBlock, uint256 _maxBorrowRate, address _missionControl)` | `4–5` | `_missionControl = empty(address)` |
| `setGenAuctionParams(uint256 _startDiscount, uint256 _maxDiscount, uint256 _delay, uint256 _duration, address _missionControl)` | `4–5` | `_missionControl = empty(address)` |
| `setGlobalDebtLimits(uint256 _perUserDebtLimit, uint256 _globalDebtLimit, uint256 _minDebtAmount, uint256 _numAllowedBorrowers, address _missionControl)` | `4–5` | `_missionControl = empty(address)` |
| `setIsDaowryEnabled(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setKeeperConfig(uint256 _keeperFeeRatio, uint256 _minKeeperFee, uint256 _maxKeeperFee, address _missionControl)` | `3–4` | `_missionControl = empty(address)` |
| `setLtvPaybackBuffer(uint256 _ltvPaybackBuffer, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setMaxLtvDeviation(uint256 _newDeviation, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setPriorityLiqAssetVaults(tuple[] _priorityLiqAssetVaults, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setPriorityPriceSourceIds(uint256[] _priorityIds, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setPriorityStabVaults(tuple[] _priorityStabVaults, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setRewardsPointsEnabled(bool _shouldEnable, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setRipeGovVaultConfig(address _asset, uint256 _assetWeight, bool _shouldFreezeWhenBadDebt, uint256 _minLockDuration, uint256 _maxLockDuration, uint256 _maxLockBoost, uint256 _exitFee, bool _canExit, address _missionControl)` | `8–9` | `_missionControl = empty(address)` |
| `setRipePerBlock(uint256 _ripePerBlock, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setRipeRewardsAllocs(uint256 _borrowersAlloc, uint256 _stakersAlloc, uint256 _votersAlloc, uint256 _genDepositorsAlloc, address _missionControl)` | `4–5` | `_missionControl = empty(address)` |
| `setStaleTime(uint256 _staleTime, address _missionControl)` | `1–2` | `_missionControl = empty(address)` |
| `setVaultLimits(uint256 _perUserMaxVaults, uint256 _perUserMaxAssetsPerVault, address _missionControl)` | `2–3` | `_missionControl = empty(address)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `MAX_STALE_TIME()` | `view` | `uint256` | — |
| `MIN_STALE_TIME()` | `view` | `uint256` | — |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `actionType(uint256 arg0)` | `view` | `uint256` | — |
| `addPriceSnapshot(address _asset, uint256 _priceSourceId)` | `nonpayable` | `bool` | `bool` |
| `areValidAuctionParams((bool,uint256,uint256,uint256,uint256) _params)` | `view` | `bool` | `bool` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `executePendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `expiration()` | `view` | `uint256` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `isExpired(uint256 _actionId)` | `view` | `bool` | — |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingBuybackRatio(uint256 arg0)` | `view` | `uint256` | — |
| `pendingCanPerformLiteAction(uint256 arg0)` | `view` | `(address user, bool canDo)` | — |
| `pendingDebtConfig(uint256 arg0)` | `view` | `(uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, uint256 numAllowedBorrowers, uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval, uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate, uint256 maxLtvDeviation, uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee, bool isDaowryEnabled, uint256 ltvPaybackBuffer, (bool hasParams, uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration) genAuctionParams)` | — |
| `pendingGeneralConfig(uint256 arg0)` | `view` | `(uint256 perUserMaxVaults, uint256 perUserMaxAssetsPerVault, uint256 priceStaleTime)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingMissionControl(uint256 arg0)` | `view` | `address` | — |
| `pendingPriorityLiqAssetVaults(uint256 arg0, uint256 arg1)` | `view` | `(uint256 vaultId, address asset)` | — |
| `pendingPriorityPriceSourceIds(uint256 arg0, uint256 arg1)` | `view` | `uint256` | — |
| `pendingPriorityStabVaults(uint256 arg0, uint256 arg1)` | `view` | `(uint256 vaultId, address asset)` | — |
| `pendingPythMaxConfidenceRatio(uint256 arg0)` | `view` | `uint256` | — |
| `pendingRipeGovVaultConfig(uint256 arg0)` | `view` | `(address asset, uint256 assetWeight, bool shouldFreezeWhenBadDebt, (uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee) lockTerms)` | — |
| `pendingRipeRewardsConfig(uint256 arg0)` | `view` | `(bool arePointsEnabled, uint256 ripePerBlock, uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc, uint256 autoStakeRatio, uint256 autoStakeDurationRatio, uint256 stabPoolRipePerDollarClaimed)` | — |
| `pendingUndyVaultDiscount(uint256 arg0)` | `view` | `uint256` | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setAutoStakeParams(uint256 _autoStakeRatio, uint256 _autoStakeDurationRatio, uint256 _stabPoolRipePerDollarClaimed)` | `nonpayable` | `uint256` | `uint256` |
| `setAutoStakeParams(uint256 _autoStakeRatio, uint256 _autoStakeDurationRatio, uint256 _stabPoolRipePerDollarClaimed, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setBorrowIntervalConfig(uint256 _maxBorrowPerInterval, uint256 _numBlocksPerInterval)` | `nonpayable` | `uint256` | `uint256` |
| `setBorrowIntervalConfig(uint256 _maxBorrowPerInterval, uint256 _numBlocksPerInterval, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setBuybackRatio(uint256 _ratio)` | `nonpayable` | `uint256` | `uint256` |
| `setCanBorrow(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanBorrow(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanBuyInAuction(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanBuyInAuction(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanClaimInStabPool(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanClaimInStabPool(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanClaimLoot(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanClaimLoot(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanDeposit(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanDeposit(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanLiquidate(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanLiquidate(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanPerformLiteAction(address _user, bool _canDo)` | `nonpayable` | `uint256` | `uint256` |
| `setCanPerformLiteAction(address _user, bool _canDo, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setCanRedeemCollateral(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanRedeemCollateral(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanRedeemInStabPool(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanRedeemInStabPool(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanRepay(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanRepay(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setCanWithdraw(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setCanWithdraw(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setDynamicRateConfig(uint256 _minDynamicRateBoost, uint256 _maxDynamicRateBoost, uint256 _increasePerDangerBlock, uint256 _maxBorrowRate)` | `nonpayable` | `uint256` | `uint256` |
| `setDynamicRateConfig(uint256 _minDynamicRateBoost, uint256 _maxDynamicRateBoost, uint256 _increasePerDangerBlock, uint256 _maxBorrowRate, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGenAuctionParams(uint256 _startDiscount, uint256 _maxDiscount, uint256 _delay, uint256 _duration)` | `nonpayable` | `uint256` | `uint256` |
| `setGenAuctionParams(uint256 _startDiscount, uint256 _maxDiscount, uint256 _delay, uint256 _duration, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setGlobalDebtLimits(uint256 _perUserDebtLimit, uint256 _globalDebtLimit, uint256 _minDebtAmount, uint256 _numAllowedBorrowers)` | `nonpayable` | `uint256` | `uint256` |
| `setGlobalDebtLimits(uint256 _perUserDebtLimit, uint256 _globalDebtLimit, uint256 _minDebtAmount, uint256 _numAllowedBorrowers, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setIsDaowryEnabled(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setIsDaowryEnabled(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setKeeperConfig(uint256 _keeperFeeRatio, uint256 _minKeeperFee, uint256 _maxKeeperFee)` | `nonpayable` | `uint256` | `uint256` |
| `setKeeperConfig(uint256 _keeperFeeRatio, uint256 _minKeeperFee, uint256 _maxKeeperFee, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setLtvPaybackBuffer(uint256 _ltvPaybackBuffer)` | `nonpayable` | `uint256` | `uint256` |
| `setLtvPaybackBuffer(uint256 _ltvPaybackBuffer, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setMaxLtvDeviation(uint256 _newDeviation)` | `nonpayable` | `uint256` | `uint256` |
| `setMaxLtvDeviation(uint256 _newDeviation, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityLiqAssetVaults((uint256,address)[] _priorityLiqAssetVaults)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityLiqAssetVaults((uint256,address)[] _priorityLiqAssetVaults, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityPriceSourceIds(uint256[] _priorityIds)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityPriceSourceIds(uint256[] _priorityIds, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityStabVaults((uint256,address)[] _priorityStabVaults)` | `nonpayable` | `uint256` | `uint256` |
| `setPriorityStabVaults((uint256,address)[] _priorityStabVaults, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setPythMaxConfidenceRatio(uint256 _ratio)` | `nonpayable` | `uint256` | `uint256` |
| `setRewardsPointsEnabled(bool _shouldEnable)` | `nonpayable` | `bool` | `bool` |
| `setRewardsPointsEnabled(bool _shouldEnable, address _missionControl)` | `nonpayable` | `bool` | `bool` |
| `setRipeGovVaultConfig(address _asset, uint256 _assetWeight, bool _shouldFreezeWhenBadDebt, uint256 _minLockDuration, uint256 _maxLockDuration, uint256 _maxLockBoost, uint256 _exitFee, bool _canExit)` | `nonpayable` | `uint256` | `uint256` |
| `setRipeGovVaultConfig(address _asset, uint256 _assetWeight, bool _shouldFreezeWhenBadDebt, uint256 _minLockDuration, uint256 _maxLockDuration, uint256 _maxLockBoost, uint256 _exitFee, bool _canExit, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setRipePerBlock(uint256 _ripePerBlock)` | `nonpayable` | `uint256` | `uint256` |
| `setRipePerBlock(uint256 _ripePerBlock, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setRipeRewardsAllocs(uint256 _borrowersAlloc, uint256 _stakersAlloc, uint256 _votersAlloc, uint256 _genDepositorsAlloc)` | `nonpayable` | `uint256` | `uint256` |
| `setRipeRewardsAllocs(uint256 _borrowersAlloc, uint256 _stakersAlloc, uint256 _votersAlloc, uint256 _genDepositorsAlloc, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setStaleTime(uint256 _staleTime)` | `nonpayable` | `uint256` | `uint256` |
| `setStaleTime(uint256 _staleTime, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `setUndyVaultDiscount(uint256 _discount)` | `nonpayable` | `uint256` | `uint256` |
| `setVaultLimits(uint256 _perUserMaxVaults, uint256 _perUserMaxAssetsPerVault)` | `nonpayable` | `uint256` | `uint256` |
| `setVaultLimits(uint256 _perUserMaxVaults, uint256 _perUserMaxAssetsPerVault, address _missionControl)` | `nonpayable` | `uint256` | `uint256` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `BorrowIntervalConfigSet` | `uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval` |
| `BuybackRatioSet` | `uint256 ratio` |
| `CanBorrowSet` | `bool canBorrow, address caller indexed` |
| `CanBuyInAuctionSet` | `bool canBuyInAuction, address caller indexed` |
| `CanClaimInStabPoolSet` | `bool canClaimInStabPool, address caller indexed` |
| `CanClaimLootSet` | `bool canClaimLoot, address caller indexed` |
| `CanDepositSet` | `bool canDeposit, address caller indexed` |
| `CanLiquidateSet` | `bool canLiquidate, address caller indexed` |
| `CanPerformLiteAction` | `address user indexed, bool canDo` |
| `CanRedeemCollateralSet` | `bool canRedeemCollateral, address caller indexed` |
| `CanRedeemInStabPoolSet` | `bool canRedeemInStabPool, address caller indexed` |
| `CanRepaySet` | `bool canRepay, address caller indexed` |
| `CanWithdrawSet` | `bool canWithdraw, address caller indexed` |
| `DynamicRateConfigSet` | `uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate` |
| `ExpirationSet` | `uint256 expiration` |
| `GenAuctionParamsSet` | `uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration` |
| `GlobalDebtLimitsSet` | `uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, uint256 numAllowedBorrowers` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `IsDaowryEnabledSet` | `bool isDaowryEnabled, address caller indexed` |
| `KeeperConfigSet` | `uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee` |
| `LtvPaybackBufferSet` | `uint256 ltvPaybackBuffer` |
| `MaxLtvDeviationSet` | `uint256 newDeviation` |
| `PendingBorrowIntervalConfigChange` | `uint256 maxBorrowPerInterval, uint256 numBlocksPerInterval, uint256 confirmationBlock, uint256 actionId` |
| `PendingBuybackRatioChange` | `uint256 ratio, uint256 confirmationBlock, uint256 actionId` |
| `PendingCanPerformLiteAction` | `address user, bool canDo, uint256 confirmationBlock, uint256 actionId` |
| `PendingDefaultAuctionParamsChange` | `uint256 startDiscount, uint256 maxDiscount, uint256 delay, uint256 duration, uint256 confirmationBlock, uint256 actionId` |
| `PendingDynamicRateConfigChange` | `uint256 minDynamicRateBoost, uint256 maxDynamicRateBoost, uint256 increasePerDangerBlock, uint256 maxBorrowRate, uint256 confirmationBlock, uint256 actionId` |
| `PendingGlobalDebtLimitsChange` | `uint256 perUserDebtLimit, uint256 globalDebtLimit, uint256 minDebtAmount, uint256 numAllowedBorrowers, uint256 confirmationBlock, uint256 actionId` |
| `PendingKeeperConfigChange` | `uint256 keeperFeeRatio, uint256 minKeeperFee, uint256 maxKeeperFee, uint256 confirmationBlock, uint256 actionId` |
| `PendingLtvPaybackBufferChange` | `uint256 ltvPaybackBuffer, uint256 confirmationBlock, uint256 actionId` |
| `PendingMaxLtvDeviationChange` | `uint256 newDeviation, uint256 confirmationBlock, uint256 actionId` |
| `PendingPriorityLiqAssetVaultsChange` | `uint256 numPriorityLiqAssetVaults, uint256 confirmationBlock, uint256 actionId` |
| `PendingPriorityPriceSourceIdsChange` | `uint256 numPriorityPriceSourceIds, uint256 confirmationBlock, uint256 actionId` |
| `PendingPriorityStabVaultsChange` | `uint256 numPriorityStabVaults, uint256 confirmationBlock, uint256 actionId` |
| `PendingPythMaxConfidenceRatioChange` | `uint256 ratio, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeGovVaultConfigChange` | `address asset, uint256 assetWeight, bool shouldFreezeWhenBadDebt, uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeRewardsAllocsChange` | `uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeRewardsAutoStakeParamsChange` | `uint256 autoStakeRatio, uint256 autoStakeDurationRatio, uint256 stabPoolRipePerDollarClaimed, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeRewardsPerBlockChange` | `uint256 ripePerBlock, uint256 confirmationBlock, uint256 actionId` |
| `PendingStaleTimeChange` | `uint256 priceStaleTime, uint256 confirmationBlock, uint256 actionId` |
| `PendingUndyVaultDiscountChange` | `uint256 discount, uint256 confirmationBlock, uint256 actionId` |
| `PendingVaultLimitsChange` | `uint256 perUserMaxVaults, uint256 perUserMaxAssetsPerVault, uint256 confirmationBlock, uint256 actionId` |
| `PriceSnapshotAdded` | `address asset indexed, uint256 priceSourceId indexed, address priceSourceAddr indexed, bool didUpdate` |
| `PriorityLiqAssetVaultsSet` | `uint256 numVaults` |
| `PriorityPriceSourceIdsModified` | `uint256 numIds` |
| `PriorityStabVaultsSet` | `uint256 numVaults` |
| `PythMaxConfidenceRatioSet` | `uint256 ratio` |
| `RewardsPointsEnabledModified` | `bool arePointsEnabled, address caller indexed` |
| `RipeGovVaultConfigSet` | `address asset, uint256 assetWeight, bool shouldFreezeWhenBadDebt, uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `RipeRewardsAllocsSet` | `uint256 borrowersAlloc, uint256 stakersAlloc, uint256 votersAlloc, uint256 genDepositorsAlloc` |
| `RipeRewardsAutoStakeParamsSet` | `uint256 autoStakeRatio, uint256 autoStakeDurationRatio, uint256 stabPoolRipePerDollarClaimed` |
| `RipeRewardsPerBlockSet` | `uint256 ripePerBlock` |
| `StaleTimeSet` | `uint256 staleTime` |
| `UndyVaultDiscountSet` | `uint256 discount` |
| `VaultLimitsSet` | `uint256 perUserMaxVaults, uint256 perUserMaxAssetsPerVault` |

### Structs declared by this source

- `GenConfigLite(perUserMaxVaults: uint256, perUserMaxAssetsPerVault: uint256, priceStaleTime: uint256)`
- `CanPerform(user: address, canDo: bool)`
- `PendingRipeGovVaultConfig(asset: address, assetWeight: uint256, shouldFreezeWhenBadDebt: bool, lockTerms: cs.LockTerms)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `already set`
- `cannot cancel action`
- `invalid auction params`
- `invalid auto stake params`
- `invalid borrow interval config`
- `invalid debt limits`
- `invalid discount`
- `invalid dynamic rate config`
- `invalid keeper config`
- `invalid ltv payback buffer`
- `invalid max deviation`
- `invalid price source id`
- `invalid priority price source ids`
- `invalid priority sources`
- `invalid priority stab vaults`
- `invalid priority vaults`
- `invalid ratio`
- `invalid rewards allocs`
- `invalid ripe per block`
- `invalid ripe vault config`
- `invalid stale time`
- `invalid stale time range`
- `invalid vault limits`
- `no perms`
- `pyth disabled`
- `ratio must be < 100%`
- `use empty for current mission control`

<!-- END GENERATED API REFERENCE: SwitchboardAlpha -->
