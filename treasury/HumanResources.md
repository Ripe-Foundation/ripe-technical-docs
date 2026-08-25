# HumanResources

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/HumanResources.vy)

## Purpose

`HumanResources` governs creation of [Contributor](./Contributor.md) vesting instances and provides their privileged RIPE mint, governance-vault transfer, and cancellation accounting routes. It can mint RIPE but not GREEN.

## Timelocked contributor creation

Governance calls `initiateNewContributor` to store proposed terms under an action ID. `confirmNewContributor` revalidates those terms after the configured timelock and creates a clone from the currently configured contributor blueprint. If terms have become invalid before confirmation, the pending action is cancelled and confirmation returns false.

Validation includes:

- a configured contributor template and valid owner/manager;
- nonzero compensation within the HR reserve and configured cap;
- nonzero cliff and vesting lengths within configured bounds;
- `cliffLength <= unlockLength <= vestingLength`;
- start-delay and arithmetic overflow bounds; and
- a contributor lock agreement satisfying `0 < depositLockDuration <=` the
  current RipeGov maximum.

A contributor agreement may be below the current general RipeGov minimum lock.
Once confirmed, later changes to the general minimum or maximum do not rewrite
its agreed lock term.

## Paychecks and current RipeGov vault

Only a registered Contributor instance may call `cashRipeCheck`, `transferContributorRipeTokens`, or `refundAfterCancelPaycheck`. Cashing a check mints the exact RIPE amount and deposits it through Teller into MissionControl's current `coreRipeGovVaultId`. There is no hardcoded current vault ID.

Contributor-position transfers preserve the supplied agreement lock, update Ledger membership, and checkpoint Lootbox points for sender and recipient.

## Historical contributor positions

`legacyContributorRipeGovVaultId` lets an existing contributor continue to address a balance held in a recognized historical RipeGov vault. The general `getRipeGovVaultId(0)` lookup resolves to the current core vault. Contributor settlement routes given vault ID zero first consult the contributor's legacy mapping and fall back to the current core vault only when that mapping is also zero. Any nonzero ID must pass MissionControl's historical/current RipeGov classification.

`setLegacyContributorRipeGovVaultId` may be called by Switchboard or by that contributor's owner or manager. A nonzero choice must identify a registered RipeGov vault in which the contributor actually has RIPE. The mapping is used for balance, transfer, refund, and burn routing and is cleared when the defaulted legacy position is consumed.

## Cancellation accounting

When a contributor cancels its paycheck, HumanResources credits no more than the uint256-safe remaining HR reserve capacity. If the position must be burned, it withdraws through the selected RipeGov vault, burns no more RIPE than it actually received, checkpoints Lootbox, and performs Teller housekeeping.

`getTotalClaimed` and `getTotalCompensation` aggregate registered contributors and saturate at `max_value(uint256)` instead of overflowing.

## Authority and lifecycle

Governance controls pending contributor creation/cancellation through the
timelock. Switchboard is recognized by Contributor instances as the external HR
modifier for freeze and cancellation actions. Department pause state gates
creation and contributor settlement routes. Events distinguish initiation,
confirmation, cancellation, and historical-vault selection; callers should not
treat an initiated action as completed creation.

<!-- BEGIN GENERATED API REFERENCE: HumanResources -->
## Exact API reference

> Generated from `contracts/core/HumanResources.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `getRipeGovVaultId(uint256 _vaultId)` | `0–1` | `_vaultId = 0` |
| `hasRipeBalance(address _contributor, uint256 _vaultId)` | `1–2` | `_vaultId = 0` |
| `refundAfterCancelPaycheck(uint256 _amount, bool _shouldBurnPosition, uint256 _vaultId)` | `2–3` | `_vaultId = 0` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |
| `transferContributorRipeTokens(address _owner, uint256 _lockDuration, uint256 _vaultId)` | `2–3` | `_vaultId = 0` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `areValidContributorTerms(address _owner, address _manager, uint256 _compensation, uint256 _startDelay, uint256 _vestingLength, uint256 _cliffLength, uint256 _unlockLength, uint256 _depositLockDuration)` | `view` | `bool` | `bool` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `canModifyHrContributor(address _addr)` | `view` | `bool` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelNewContributor(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `cashRipeCheck(uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `bool` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `confirmNewContributor(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `expiration()` | `view` | `uint256` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getRipeGovVaultId()` | `view` | `uint256` | `uint256` |
| `getRipeGovVaultId(uint256 _vaultId)` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `getTotalClaimed()` | `view` | `uint256` | `uint256` |
| `getTotalCompensation()` | `view` | `uint256` | `uint256` |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `hasRipeBalance(address _contributor)` | `view` | `bool` | `bool` |
| `hasRipeBalance(address _contributor, uint256 _vaultId)` | `view` | `bool` | `bool` |
| `initiateNewContributor(address _owner, address _manager, uint256 _compensation, uint256 _startDelay, uint256 _vestingLength, uint256 _cliffLength, uint256 _unlockLength, uint256 _depositLockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `isExpired(uint256 _actionId)` | `view` | `bool` | — |
| `isPaused()` | `view` | `bool` | — |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `legacyContributorRipeGovVaultId(address arg0)` | `view` | `uint256` | — |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingContributor(uint256 arg0)` | `view` | `(address owner, address manager, uint256 compensation, uint256 startDelay, uint256 vestingLength, uint256 cliffLength, uint256 unlockLength, uint256 depositLockDuration)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `refundAfterCancelPaycheck(uint256 _amount, bool _shouldBurnPosition)` | `nonpayable` | — | — |
| `refundAfterCancelPaycheck(uint256 _amount, bool _shouldBurnPosition, uint256 _vaultId)` | `nonpayable` | — | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setLegacyContributorRipeGovVaultId(address _contributor, uint256 _vaultId)` | `nonpayable` | — | — |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `transferContributorRipeTokens(address _owner, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `transferContributorRipeTokens(address _owner, uint256 _lockDuration, uint256 _vaultId)` | `nonpayable` | `uint256` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `LegacyContributorRipeGovVaultSet` | `address contributor indexed, uint256 vaultId, address changedBy indexed` |
| `NewContributorCancelled` | `address owner indexed, address manager indexed, uint256 compensation, uint256 startDelay, uint256 vestingLength, uint256 cliffLength, uint256 unlockLength, uint256 depositLockDuration, uint256 confirmationBlock, uint256 actionId` |
| `NewContributorConfirmed` | `address contributorAddr indexed, address owner indexed, address manager indexed, uint256 compensation, uint256 startDelay, uint256 vestingLength, uint256 cliffLength, uint256 unlockLength, uint256 depositLockDuration, uint256 actionId` |
| `NewContributorInitiated` | `address owner indexed, address manager indexed, uint256 compensation, uint256 startDelay, uint256 vestingLength, uint256 cliffLength, uint256 unlockLength, uint256 depositLockDuration, uint256 confirmationBlock, uint256 actionId` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `ContributorTerms(owner: address, manager: address, compensation: uint256, startDelay: uint256, vestingLength: uint256, cliffLength: uint256, unlockLength: uint256, depositLockDuration: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot cancel action`
- `contract paused`
- `could not deploy`
- `invalid terms`
- `invalid vault id`
- `no balance`
- `no pending contributor`
- `no perms`
- `not a contributor`
- `ripe approval failed`
- `ripe burn failed`
- `time lock not reached`

<!-- END GENERATED API REFERENCE: HumanResources -->
