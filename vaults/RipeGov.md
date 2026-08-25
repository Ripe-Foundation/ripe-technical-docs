# RipeGov vault

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/vaults/RipeGov.vy)

## Overview

`RipeGov` is a share-accounting vault for RIPE and configured ecosystem assets.
It combines custody-based shares with block-based governance points and
per-asset lock terms. It supports irreversible point-accrual shutdown and
full-position migration that preserves points, unlock, and historical terms.

## Position data

Each user/asset has:

```text
GovData:
  govPoints
  lastShares
  lastPointsUpdate
  unlock
  lastTerms
```

The vault also tracks per-user and global governance-point totals. Asset amounts use SharesVault's current custody-based conversion and `1e8` virtual-share offset.

MissionControl supplies `RipeGovVaultConfig` for each asset: `LockTerms`, point weight, and whether withdrawals freeze during bad debt.

## Deposits and locks

Only Teller may call deposit routes. A configured asset must have nonzero `maxLockDuration`. Requested duration is clamped to the current minimum/maximum. When a user already holds shares, the new unlock is a full-precision share-weighted blend of the remaining old duration and new duration.

Before updating the position, the vault accrues points through the current block and refreshes stored terms. A user/asset marked `positionMigratedOut` can never deposit into that same historical vault again.

`depositTokensWithLockDuration` is the explicit-duration route. The ordinary deposit uses zero input and therefore receives at least the configured minimum.

## Governance-point accrual

New points are based on:

```text
base = (lastShares / 1e18) * elapsedBlocks
weighted = base * assetWeight / 100%
newPoints = weighted + remaining-lock bonus
```

Asset weight is always applied. A configured zero weight produces zero points; it does not fall back to an unweighted 100% rate.

The lock bonus scales from zero at/below `minLockDuration` to `maxLockBoost` at `maxLockDuration`, capped by the maximum remaining duration.

`updateUserGovPoints` may be called only by a valid Ripe address and is unavailable while the vault is paused. It updates every registered user asset and, for an accrual-enabled user, notifies Boardroom with the canonical user/global totals.

Boardroom is a minimal callback sink; point totals remain canonical in RipeGov.

## Term refresh and courtesy unlock

`refreshUnlock(previousUnlock, newTerms, previousTerms)` returns zero when the
current configuration becomes adverse in any of these ways:

- exit was available and is removed;
- exit fee increases while exit was already available;
- maximum lock boost decreases;
- minimum lock duration increases; or
- maximum lock duration increases.

Any adverse change wins. The courtesy is lazy: a touch while the adverse
configuration remains current persists the zero unlock. It does not override
Teller pause or the asset's bad-debt freeze.

## Withdrawals and forced transfers

Teller, AuctionHouse, and CreditEngine may withdraw. The normal path requires the unlock block to be reached and, when configured, zero protocol bad debt. HumanResources has a contributor-burn route that bypasses those restrictions and sends all RIPE to HR for the cancellation workflow.

Withdrawal burns custody-based shares and reduces accrued/saved points proportionally. A full per-asset exit clears that asset's remaining points.

AuctionHouse and CreditEngine may transfer balances between users for
liquidation/redemption without respecting the sender's lock. The recipient
receives the current configured minimum lock and no transferred points. This
forced-transfer path remains callable even if lock terms are temporarily
absent.

HumanResources may transfer a contributor's full RIPE position and its
associated point value. The confirmed contributor duration is forwarded
exactly and is not clamped to a later maximum; this preserves the agreement
under a later parameter reduction.

If a forced-transfer sender has point accrual disabled, the vault suppresses both Boardroom callbacks for that transaction while still updating canonical totals. This prevents an external callback from stranding an emergency exit; a later public update may retry the healthy recipient.

## Lock adjustment and early release

Teller may extend a nonzero position's lock while the vault is unpaused. The
requested duration is clamped to stored current terms and the resulting unlock
must be later than the existing unlock.

Early `releaseLock` requires:

- an unpaused vault and Teller caller;
- an unlock still in the future;
- stored terms with `canExit = true` and nonzero exit fee;
- a nonzero position; and
- another outstanding share holder, so the burned fee shares have someone to benefit.

If bad debt exists and the asset would remain frozen anyway, release is rejected to avoid charging a fee that cannot enable withdrawal. The fee burns the precise number of shares needed to leave a floored post-fee claim. Lock state is cleared before Lootbox checkpointing so future rewards see the post-burn, unboosted position.

## Irreversible governance-point shutdown

Switchboard may call:

- `disableGovPointAccrualForUser(user)`; or
- `disableGovPointAccrualGlobally()`.

Each records the current block and cannot be reversed. A global disable prevents adding a later user-specific disable. Governance reaches these sensitive calls through the timelocked Switchboard Echo workflow; direct source reachability does not make them permissionless.

After disablement, no new governance points accrue. Stored points are preserved on a partial withdrawal and cleared for that asset on complete exit. Public point refresh skips accrual/Boardroom but may still refresh terms when the vault is active.

`inheritUserGovPointAccrualDisableForMigration(user, disabledBlock)` is VaultMigrator-only, requires the target vault paused, and accepts a nonzero past/current block. It does not overwrite an existing marker.

## Position migration

### Migration payload

```text
RipeGovMigrationData:
  amount
  govPoints
  unlock
  lastTerms
```

### Export

`exportPositionForMigration` is Teller-only, nonreentrant, and requires the source vault paused. The target must be a distinct registered vault contract. Export:

1. requires a nonzero full position and no prior tombstone;
2. accrues through the export block using the position's stored pre-wind-down lock terms rather than refreshing to temporary wind-down terms;
3. requires exact consistency between stored and actual shares/point totals;
4. removes the complete position and its points from source totals;
5. permanently sets `positionMigratedOut[user][asset]`;
6. transfers the underlying amount to the target vault; and
7. returns the preserved amount, points, unlock, and terms.

The permanent tombstone prevents migration back into that source user/asset position.

### Import

`importPositionForMigration` is Teller-only, nonreentrant, and requires the target vault paused. The source must be a distinct registered vault. The target user/asset must have no balance, no existing governance data, and no target tombstone.

The target must already have received at least `migration.amount`. Shares are calculated against custody immediately before that incoming amount and must be nonzero. Import restores governance points, unlock, and `lastTerms` exactly, while setting `lastPointsUpdate` to the import block.

VaultMigrator separately propagates a user-specific point-disable block when required. It also verifies exact source debit, target receipt, no Teller residue, target shares/terms/points, and Ledger participation around the Teller-mediated calls.

## Migration and pause authority

The RipeGov contract enforces its local Teller/paused/registered-vault conditions. VaultMigrator and Switchboard add the broader policy: historical source classification, current target pointer, Teller pause, source/target pause state, batch limits, and legacy-chain rules. Do not treat the local functions as a complete migration authorization specification.

## Integration requirements

- Resolve the current core vault pointer and historical classification from MissionControl.
- Preserve `RipeGovMigrationData` field order and the source tombstone.
- Do not refresh migration positions into temporary wind-down terms.
- Treat point-disable state as irreversible and migrate it explicitly.
- Interpret raw `userBalances` as shares, not token amounts.

<!-- BEGIN GENERATED API REFERENCE: RipeGov -->
## Exact API reference

> Generated from `contracts/vaults/RipeGov.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `adjustLock(address _user, address _asset, uint256 _newLockDuration, Addys _a)` | `3–4` | `_a` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, Addys _a)` | `3–4` | `_a` |
| `depositTokensWithLockDuration(address _user, address _asset, uint256 _amount, uint256 _lockDuration, Addys _a)` | `4–5` | `_a` |
| `exportPositionForMigration(address _user, address _asset, address _targetVault, Addys _a)` | `3–4` | `_a` |
| `releaseLock(address _user, address _asset, Addys _a)` | `2–3` | `_a` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, Addys _a)` | `4–5` | `_a` |
| `transferContributorRipeTokens(address _contributor, address _toUser, uint256 _lockDuration, Addys _a)` | `3–4` | `_a` |
| `updateUserGovPoints(address _user, Addys _a)` | `1–2` | `_a` |
| `withdrawContributorTokensToBurn(address _user, Addys _a)` | `1–2` | `_a` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, Addys _a)` | `4–5` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `adjustLock(address _user, address _asset, uint256 _newLockDuration)` | `nonpayable` | — |
| `adjustLock(address _user, address _asset, uint256 _newLockDuration, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `amountToShares(address _asset, uint256 _amount, bool _shouldRoundUp)` | `view` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount)` | `nonpayable` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `depositTokensWithLockDuration(address _user, address _asset, uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `uint256` |
| `depositTokensWithLockDuration(address _user, address _asset, uint256 _amount, uint256 _lockDuration, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `deregisterUserAsset(address _user, address _asset)` | `nonpayable` | `bool` |
| `deregisterVaultAsset(address _asset)` | `nonpayable` | `bool` |
| `disableGovPointAccrualForUser(address _user)` | `nonpayable` | — |
| `disableGovPointAccrualGlobally()` | `nonpayable` | — |
| `doesUserHaveBalance(address _user, address _asset)` | `view` | `bool` |
| `doesVaultHaveAnyFunds()` | `view` | `bool` |
| `exportPositionForMigration(address _user, address _asset, address _targetVault)` | `nonpayable` | `(uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256))` |
| `exportPositionForMigration(address _user, address _asset, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256))` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getLatestGovPoints(uint256 _lastShares, uint256 _lastPointsUpdate, uint256 _unlock, (uint256,uint256,uint256,bool,uint256) _terms, uint256 _weight)` | `view` | `uint256` |
| `getLockBonusPoints(uint256 _points, uint256 _unlock, (uint256,uint256,uint256,bool,uint256) _terms)` | `view` | `uint256` |
| `getNumUserAssets(address _user)` | `view` | `uint256` |
| `getNumVaultAssets()` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `getTotalAmountForUser(address _user, address _asset)` | `view` | `uint256` |
| `getTotalAmountForVault(address _asset)` | `view` | `uint256` |
| `getUserAssetAndAmountAtIndex(address _user, uint256 _index)` | `view` | `(address, uint256)` |
| `getUserAssetAtIndexAndHasBalance(address _user, uint256 _index)` | `view` | `(address, bool)` |
| `getUserLootBoxShare(address _user, address _asset)` | `view` | `uint256` |
| `getVaultDataOnDeposit(address _user, address _asset)` | `view` | `(bool,uint256,uint256,uint256)` |
| `getWeightedLockOnTokenDeposit(uint256 _newShares, uint256 _newLockDuration, (uint256,uint256,uint256,bool,uint256) _lockTerms, uint256 _prevShares, uint256 _prevUnlock)` | `view` | `uint256` |
| `govPointAccrualDisabledBlock()` | `view` | `uint256` |
| `importPositionForMigration(address _user, address _asset, address _sourceVault, (uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256)) _migration)` | `nonpayable` | `uint256` |
| `indexOfAsset(address arg0)` | `view` | `uint256` |
| `indexOfUserAsset(address arg0, address arg1)` | `view` | `uint256` |
| `inheritUserGovPointAccrualDisableForMigration(address _user, uint256 _disabledBlock)` | `nonpayable` | `bool` |
| `isPaused()` | `view` | `bool` |
| `isSupportedVaultAsset(address _asset)` | `view` | `bool` |
| `isUserInVaultAsset(address _user, address _asset)` | `view` | `bool` |
| `numAssets()` | `view` | `uint256` |
| `numUserAssets(address arg0)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `positionMigratedOut(address arg0, address arg1)` | `view` | `bool` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `refreshUnlock(uint256 _prevUnlock, (uint256,uint256,uint256,bool,uint256) _newTerms, (uint256,uint256,uint256,bool,uint256) _prevTerms)` | `view` | `uint256` |
| `releaseLock(address _user, address _asset)` | `nonpayable` | — |
| `releaseLock(address _user, address _asset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `sharesToAmount(address _asset, uint256 _shares, bool _shouldRoundUp)` | `view` | `uint256` |
| `totalBalances(address arg0)` | `view` | `uint256` |
| `totalGovPoints()` | `view` | `uint256` |
| `totalUserGovPoints(address arg0)` | `view` | `uint256` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount)` | `nonpayable` | `(uint256, bool)` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |
| `transferContributorRipeTokens(address _contributor, address _toUser, uint256 _lockDuration)` | `nonpayable` | `uint256` |
| `transferContributorRipeTokens(address _contributor, address _toUser, uint256 _lockDuration, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `updateUserGovPoints(address _user)` | `nonpayable` | — |
| `updateUserGovPoints(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `userAssets(address arg0, uint256 arg1)` | `view` | `address` |
| `userBalances(address arg0, address arg1)` | `view` | `uint256` |
| `userGovData(address arg0, address arg1)` | `view` | `(uint256,uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256))` |
| `userGovPointAccrualDisabledBlock(address arg0)` | `view` | `uint256` |
| `vaultAssets(uint256 arg0)` | `view` | `address` |
| `withdrawContributorTokensToBurn(address _user)` | `nonpayable` | `uint256` |
| `withdrawContributorTokensToBurn(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient)` | `nonpayable` | `(uint256, bool)` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |

### Events

| Event | Fields |
| --- | --- |
| `GovPointAccrualDisabledForUser` | `address user indexed, uint256 disabledBlock, address caller indexed` |
| `GovPointAccrualDisabledGlobally` | `uint256 disabledBlock, address caller indexed` |
| `LockModified` | `address user indexed, address asset indexed, uint256 newLockDuration` |
| `LockReleased` | `address user indexed, address asset indexed, uint256 exitFee` |
| `RipeGovPositionExported` | `address user indexed, address asset indexed, address targetVault indexed, uint256 amount, uint256 sourceShares, uint256 govPoints, uint256 unlock` |
| `RipeGovPositionImported` | `address user indexed, address asset indexed, address sourceVault indexed, uint256 amount, uint256 targetShares, uint256 govPoints, uint256 unlock` |
| `RipeGovVaultBurnContributorTokens` | `address user indexed, address asset indexed, uint256 amount, uint256 shares` |
| `RipeGovVaultDeposit` | `address user indexed, address asset indexed, uint256 amount, uint256 shares, uint256 lockDuration` |
| `RipeGovVaultTransfer` | `address fromUser indexed, address toUser indexed, address asset indexed, uint256 transferAmount, bool isFromUserDepleted, uint256 transferShares` |
| `RipeGovVaultWithdrawal` | `address user indexed, address asset indexed, uint256 amount, bool isDepleted, uint256 shares` |
| `RipeTokensTransferred` | `address fromUser indexed, address toUser indexed, uint256 amount` |
| `VaultFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `VaultPauseModified` | `bool isPaused` |

### Structs declared by this source

- `GovData(govPoints: uint256, lastShares: uint256, lastPointsUpdate: uint256, unlock: uint256, lastTerms: cs.LockTerms)`
- `RipeGovMigrationData(amount: uint256, govPoints: uint256, unlock: uint256, lastTerms: cs.LockTerms)`

<!-- END GENERATED API REFERENCE: RipeGov -->
