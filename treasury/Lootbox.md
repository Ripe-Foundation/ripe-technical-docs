# Lootbox

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/Lootbox.vy)

## Purpose

`Lootbox` checkpoints borrow and deposit participation, allocates RIPE rewards, settles claims, optionally stakes RIPE into the current core RipeGov vault, and can distribute a separately configured RIPE amount to Underscore.

The main reward buckets are borrowers, RipeGov stakers, voters, and general depositors. MissionControl supplies whether points/rewards are enabled, per-block emissions, category allocations, user claim permissions, auto-stake ratio, and reward lock duration.

## Claims

Teller and other registered Ripe addresses call `claimLootForUser` or `claimLootForManyUsers` (up to 25 users). A caller claiming for another user needs the current user permission or Underscore-owner relationship, except for the explicitly privileged Switchboard route. `claimDepositLootForAsset` and `claimBorrowLoot` are likewise department-gated settlement helpers, not permissionless user mint functions.

A full claim settles borrow loot and enumerated deposit loot before minting. The final RIPE may be sent to the user, staked through Teller, or split according to current claim configuration. Staked rewards use MissionControl's dynamic `coreRipeGovVaultId`; historical RipeGov vaults can still contribute deposit points, but there is no hardcoded current ID.

## Atomic deposit-category settlement

A user's deposit `balancePoints` are one shared ticket backing the staker, voter, and general-depositor categories. Lootbox does not consume that ticket after paying only some categories.

For each asset, every attributable category must either:

- produce a payout; or
- be terminally resolvable because its bucket cannot refill, or because the user exited and only funded rounding dust remains.

If a nonzero category rounds to zero, the entire ticket is deferred. Points
remain discoverable for a future claim. Asset/vault cleanup occurs only after
the user has no balance and the entitlement has been fully paid or terminally
resolved, preventing deregistration from hiding recoverable rewards.

The implementation uses full-precision multiplication/division and guarantees point progress on a committed settlement, while preserving the public `calcSpecificLoot` basis-point-compatible interface.

## Valuing vault positions

Deposit checkpoints obtain supported balances and USD value from current vault/PriceDesk state. Stability vault totals use their total-balance accounting. Share/converter topology is validated; a missing or malformed converter, vault token, or underlying asset fails closed and cannot fabricate reward-bearing value.

## Reward budget and minting

Global reward updates allocate only available RIPE budget. Claims reduce the appropriate buckets before minting. Underscore distribution reserves its share in Ledger before minting or calling the external distributor so a callback cannot consume the same capacity.

## Underscore distribution

`distributeUnderscoreRewards` is Switchboard-only, requires the contract to be unpaused and Underscore rewards enabled, and enforces a configurable block interval no lower than the constructor's immutable minimum. The current Underscore Loot Distributor is resolved dynamically. Deposit and yield portions are reduced proportionally if the remaining RIPE reward budget cannot cover the requested total.

## Security and lifecycle notes

- Claim and point mutation routes require registered protocol authority and current claim permissions.
- Reward capacity is reconciled in Ledger before mint/external distribution.
- Dynamic vault and Underscore resolution avoids stale hardcoded IDs/addresses.
- Pausing blocks claim/accounting entry points; operators must consider accrued checkpoint behavior before a later unpause.
- `getClaimableLoot` and category views are calculations at call time, not
  reserved payouts.

Principal events include `DepositLootClaimed`, `BorrowLootClaimed`, `UnderscoreRewardsDistributed`, and the Underscore configuration events.

<!-- BEGIN GENERATED API REFERENCE: Lootbox -->
## Exact API reference

> Generated from `contracts/core/Lootbox.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _minUnderscoreSendInterval, uint256 _underscoreSendInterval, uint256 _undyDepositRewardsAmount, uint256 _undyYieldBonusAmount)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `claimLootForManyUsers(address[] _users, address _caller, bool _shouldStake, Addys _a)` | `3–4` | `_a` |
| `claimLootForUser(address _user, address _caller, bool _shouldStake, Addys _a)` | `3–4` | `_a` |
| `getLatestDepositPoints(address _user, uint256 _vaultId, address _asset, Addys _a)` | `3–4` | `_a` |
| `updateBorrowPoints(address _user, Addys _a)` | `1–2` | `_a` |
| `updateDepositPoints(address _user, uint256 _vaultId, address _vaultAddr, address _asset, Addys _a)` | `4–5` | `_a` |
| `updateRipeRewards(Addys _a)` | `0–1` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `calcSpecificLoot(uint256 _userShareOfAsset, uint256 _assetPoints, uint256 _globalPoints, uint256 _rewardsAvailable)` | `view` | `(uint256, uint256, uint256, uint256)` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `claimBorrowLoot(address _user)` | `nonpayable` | `uint256` |
| `claimDepositLootForAsset(address _user, uint256 _vaultId, address _asset)` | `nonpayable` | `uint256` |
| `claimLootForManyUsers(address[] _users, address _caller, bool _shouldStake)` | `nonpayable` | `uint256` |
| `claimLootForManyUsers(address[] _users, address _caller, bool _shouldStake, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `claimLootForUser(address _user, address _caller, bool _shouldStake)` | `nonpayable` | `uint256` |
| `claimLootForUser(address _user, address _caller, bool _shouldStake, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `distributeUnderscoreRewards()` | `nonpayable` | `(uint256, uint256)` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getClaimableBorrowLoot(address _user)` | `view` | `uint256` |
| `getClaimableDepositLootForAsset(address _user, uint256 _vaultId, address _asset)` | `view` | `uint256` |
| `getClaimableLoot(address _user)` | `view` | `uint256` |
| `getLatestDepositPoints(address _user, uint256 _vaultId, address _asset)` | `view` | `((uint256,uint256,uint256), (uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256), (uint256,uint256,uint256,uint256,uint256))` |
| `getLatestDepositPoints(address _user, uint256 _vaultId, address _asset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `((uint256,uint256,uint256), (uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256), (uint256,uint256,uint256,uint256,uint256))` |
| `getLatestGlobalRipeRewards()` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256)` |
| `getRipeHq()` | `view` | `address` |
| `hasUnderscoreRewards()` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `lastUnderscoreSend()` | `view` | `uint256` |
| `minUnderscoreSendInterval()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `resetAssetPoints(address _asset, uint256 _vaultId)` | `nonpayable` | — |
| `resetUserBalancePoints(address _user, address _asset, uint256 _vaultId)` | `nonpayable` | — |
| `resetUserBorrowPoints(address _user)` | `nonpayable` | — |
| `setHasUnderscoreRewards(bool _hasRewards)` | `nonpayable` | — |
| `setUnderscoreSendInterval(uint256 _numBlocks)` | `nonpayable` | — |
| `setUndyDepositRewardsAmount(uint256 _amount)` | `nonpayable` | — |
| `setUndyYieldBonusAmount(uint256 _amount)` | `nonpayable` | — |
| `underscoreSendInterval()` | `view` | `uint256` |
| `undyDepositRewardsAmount()` | `view` | `uint256` |
| `undyYieldBonusAmount()` | `view` | `uint256` |
| `updateBorrowPoints(address _user)` | `nonpayable` | — |
| `updateBorrowPoints(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `updateDepositPoints(address _user, uint256 _vaultId, address _vaultAddr, address _asset)` | `nonpayable` | — |
| `updateDepositPoints(address _user, uint256 _vaultId, address _vaultAddr, address _asset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `updateRipeRewards()` | `nonpayable` | `(uint256,uint256,uint256,uint256,uint256,uint256)` |
| `updateRipeRewards((address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256,uint256,uint256,uint256,uint256,uint256)` |

### Events

| Event | Fields |
| --- | --- |
| `BorrowLootClaimed` | `address user indexed, uint256 ripeAmount` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `DepositLootClaimed` | `address user indexed, uint256 vaultId, address asset indexed, uint256 ripeStakerLoot, uint256 ripeVoteLoot, uint256 ripeGenLoot` |
| `HasUnderscoreRewardsUpdated` | `bool hasRewards` |
| `UnderscoreRewardsDistributed` | `address underscoreAddr indexed, uint256 depositAmount, uint256 yieldAmount, uint256 blockNumber` |
| `UnderscoreSendIntervalUpdated` | `uint256 numBlocks` |
| `UndyDepositRewardsAmountUpdated` | `uint256 amount` |
| `UndyYieldBonusAmountUpdated` | `uint256 amount` |

### Structs declared by this source

- `RipeRewards(borrowers: uint256, stakers: uint256, voters: uint256, genDepositors: uint256, newRipeRewards: uint256, lastUpdate: uint256)`
- `GlobalDepositPoints(lastUsdValue: uint256, ripeStakerPoints: uint256, ripeVotePoints: uint256, ripeGenPoints: uint256, lastUpdate: uint256)`
- `AssetDepositPoints(balancePoints: uint256, lastBalance: uint256, lastUsdValue: uint256, ripeStakerPoints: uint256, ripeVotePoints: uint256, ripeGenPoints: uint256, lastUpdate: uint256, precision: uint256)`
- `UserDepositPoints(balancePoints: uint256, lastBalance: uint256, lastUpdate: uint256)`
- `BorrowPoints(lastPrincipal: uint256, points: uint256, lastUpdate: uint256)`
- `BorrowPointsBundle(userPoints: BorrowPoints, globalPoints: BorrowPoints, userDebtPrincipal: uint256)`
- `DepositPointsBundle(userPoints: UserDepositPoints, assetPoints: AssetDepositPoints, globalPoints: GlobalDepositPoints)`
- `RipeRewardsBundle(ripeRewards: RipeRewards, ripeAvailForRewards: uint256)`
- `UserDepositLoot(ripeStakerLoot: uint256, ripeVoteLoot: uint256, ripeGenLoot: uint256)`
- `RewardsConfig(arePointsEnabled: bool, ripePerBlock: uint256, borrowersAlloc: uint256, stakersAlloc: uint256, votersAlloc: uint256, genDepositorsAlloc: uint256, stakersPointsAllocTotal: uint256, voterPointsAllocTotal: uint256)`
- `DepositPointsConfig(stakersPointsAlloc: uint256, voterPointsAlloc: uint256, isNft: bool)`
- `ClaimLootConfig(canClaimLoot: bool, canClaimLootForUser: bool, autoStakeRatio: uint256, rewardsLockDuration: uint256)`

<!-- END GENERATED API REFERENCE: Lootbox -->
