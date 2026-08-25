# Ledger

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/data/Ledger.vy)

## Purpose

`Ledger` is the protocol's authoritative shared state store. It records user vault membership, debt and interest state, reward checkpoints, auction membership, Human Resources data, bond epochs, and Endaoment debt. It is not a general-purpose user entry point: mutators are restricted to the department responsible for each state domain.

## Action-block identity and last touch

The constructor accepts an immutable `actionBlockSource`. Only two modes are valid:

- the zero address, which uses the native `block.number`; or
- Arbitrum's `ArbSys` precompile at `0x0000000000000000000000000000000000000064`, which uses `arbBlockNumber()`.

`getArbActionBlock` performs the exact precompile read. `_getActionBlock` selects the configured source. Teller alone calls `checkAndUpdateLastTouch`; it requires Ledger to be unpaused, rejects a locked account, and can enforce at most one protected action per action-block identity.

On an Arbitrum child chain, the native EVM `block.number` can represent a
repeated L1 ancestor estimate, while `ArbSys.arbBlockNumber()` identifies the
child-chain action block. Therefore `lastTouch` must be interpreted as the
constructor-selected action-block identity, not universally as native block
height.

## State domains and authority

Ledger groups state by domain and restricts each mutator to the corresponding registered protocol address:

- **Vault membership:** user vault lists and asset membership.
- **Credit:** principal, accrued interest, timestamps, liquidation flags, and debt aggregates.
- **Rewards:** user and system checkpoints consumed by Lootbox and related modules.
- **Auctions:** per-user auction membership and active auction references.
- **Human Resources:** contributor and compensation accounting.
- **Bonds:** epoch and purchase accounting.
- **Endaoment:** protocol liquidity debt.

Read methods expose these records to other protocol components and integrations. A caller should not infer authorization from a public getter; the state-changing counterpart remains department-gated.

## Vault IDs

Ledger stores vault IDs, but it does not make a historical numeric ID permanently "current." Current core, RipeGov, Stability, and preferred-vault roles are classified through MissionControl/VaultBook state. Documentation and integrations should resolve those roles rather than assuming IDs such as 1 or 2.

## Security properties

- Constructor validation prevents an arbitrary external contract from becoming the action-block oracle.
- Domain-specific access control prevents one department from writing another department's accounting.
- Ledger pause, account lock, and same-action-block checks centralize cross-module safety rules used by Teller.
- Membership lists are maintained alongside state changes so downstream modules can enumerate current positions.

Events and cached state should be reconciled against current Ledger getters when exact debt, auction, reward, or membership state matters.

<!-- BEGIN GENERATED API REFERENCE: Ledger -->
## Exact API reference

> Generated from `contracts/data/Ledger.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _defaults, address _actionBlockSource)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `checkAndUpdateLastTouch(address _user, bool _shouldCheck, address _mc)` | `2–3` | `_mc` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `ACTION_BLOCK_SOURCE()` | `view` | `address` |
| `addHrContributor(address _contributor, uint256 _compensation)` | `nonpayable` | — |
| `addVaultToUser(address _user, uint256 _vaultId)` | `nonpayable` | — |
| `assetDepositPoints(uint256 arg0, address arg1)` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256)` |
| `badDebt()` | `view` | `uint256` |
| `borrowIntervals(address arg0)` | `view` | `(uint256,uint256)` |
| `borrowers(uint256 arg0)` | `view` | `address` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `checkAndUpdateLastTouch(address _user, bool _shouldCheck)` | `nonpayable` | — |
| `checkAndUpdateLastTouch(address _user, bool _shouldCheck, address _mc)` | `nonpayable` | — |
| `contributors(uint256 arg0)` | `view` | `address` |
| `createNewFungibleAuction((address,uint256,address,uint256,uint256,uint256,uint256,bool) _auc)` | `nonpayable` | `uint256` |
| `didClearBadDebt(uint256 _amount, uint256 _ripeAmount)` | `nonpayable` | — |
| `didGetRewardsFromStabClaims(uint256 _amount)` | `nonpayable` | — |
| `didPurchaseRipeBond(uint256 _amountPaid, uint256 _ripePayout)` | `nonpayable` | — |
| `epochEnd()` | `view` | `uint256` |
| `epochStart()` | `view` | `uint256` |
| `flushUnrealizedYield()` | `nonpayable` | `uint256` |
| `fungLiqUsers(uint256 arg0)` | `view` | `address` |
| `fungibleAuctionIndex(address arg0, uint256 arg1, address arg2)` | `view` | `uint256` |
| `fungibleAuctions(address arg0, uint256 arg1)` | `view` | `(address,uint256,address,uint256,uint256,uint256,uint256,bool)` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getArbActionBlock()` | `view` | `uint256` |
| `getBorrowDataBundle(address _user)` | `view` | `((uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool),(uint256,uint256),bool,uint256,uint256,uint256)` |
| `getBorrowPointsBundle(address _user)` | `view` | `((uint256,uint256,uint256),(uint256,uint256,uint256),uint256)` |
| `getDepositLedgerData(address _user, uint256 _vaultId)` | `view` | `(bool,uint256)` |
| `getDepositPointsBundle(address _user, uint256 _vaultId, address _asset)` | `view` | `((uint256,uint256,uint256),(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256),(uint256,uint256,uint256,uint256,uint256))` |
| `getEpochData()` | `view` | `(uint256, uint256)` |
| `getFungibleAuction(address _liqUser, uint256 _vaultId, address _asset)` | `view` | `(address,uint256,address,uint256,uint256,uint256,uint256,bool)` |
| `getFungibleAuctionDuringPurchase(address _liqUser, uint256 _vaultId, address _asset)` | `view` | `(address,uint256,address,uint256,uint256,uint256,uint256,bool)` |
| `getNumBorrowers()` | `view` | `uint256` |
| `getNumUserVaults(address _user)` | `view` | `uint256` |
| `getRepayDataBundle(address _user)` | `view` | `((uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool),uint256)` |
| `getRipeBondData()` | `view` | `(uint256,uint256,uint256)` |
| `getRipeHq()` | `view` | `address` |
| `getRipeRewardsBundle()` | `view` | `((uint256,uint256,uint256,uint256,uint256,uint256),uint256)` |
| `globalBorrowPoints()` | `view` | `(uint256,uint256,uint256)` |
| `globalDepositPoints()` | `view` | `(uint256,uint256,uint256,uint256,uint256)` |
| `greenPoolDebt(address arg0)` | `view` | `uint256` |
| `hasDebt(address _user)` | `view` | `bool` |
| `hasFungibleAuction(address _liqUser, uint256 _vaultId, address _asset)` | `view` | `bool` |
| `hasFungibleAuctions(address _liqUser)` | `view` | `bool` |
| `indexOfBorrower(address arg0)` | `view` | `uint256` |
| `indexOfContributor(address arg0)` | `view` | `uint256` |
| `indexOfFungLiqUser(address arg0)` | `view` | `uint256` |
| `indexOfVault(address arg0, uint256 arg1)` | `view` | `uint256` |
| `isBorrower(address _user)` | `view` | `bool` |
| `isHrContributor(address _contributor)` | `view` | `bool` |
| `isLockedAccount(address arg0)` | `view` | `bool` |
| `isParticipatingInVault(address _user, uint256 _vaultId)` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `isUserInLiquidation(address _user)` | `view` | `bool` |
| `lastTouch(address arg0)` | `view` | `uint256` |
| `numBorrowers()` | `view` | `uint256` |
| `numContributors()` | `view` | `uint256` |
| `numFungLiqUsers()` | `view` | `uint256` |
| `numFungibleAuctions(address arg0)` | `view` | `uint256` |
| `numUserVaults(address arg0)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `paymentAmountAvailInEpoch()` | `view` | `uint256` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `refundRipeAfterCancelPaycheck(uint256 _amount)` | `nonpayable` | — |
| `removeAllFungibleAuctions(address _liqUser)` | `nonpayable` | — |
| `removeFungibleAuction(address _liqUser, uint256 _vaultId, address _asset)` | `nonpayable` | — |
| `removeVaultFromUser(address _user, uint256 _vaultId)` | `nonpayable` | — |
| `ripeAvailForBonds()` | `view` | `uint256` |
| `ripeAvailForHr()` | `view` | `uint256` |
| `ripeAvailForRewards()` | `view` | `uint256` |
| `ripePaidOutForBadDebt()` | `view` | `uint256` |
| `ripeRewards()` | `view` | `(uint256,uint256,uint256,uint256,uint256,uint256)` |
| `setBadDebt(uint256 _amount)` | `nonpayable` | — |
| `setBorrowPointsAndRipeRewards(address _user, (uint256,uint256,uint256) _userPoints, (uint256,uint256,uint256) _globalPoints, (uint256,uint256,uint256,uint256,uint256,uint256) _ripeRewards)` | `nonpayable` | — |
| `setDepositPointsAndRipeRewards(address _user, uint256 _vaultId, address _asset, (uint256,uint256,uint256) _userPoints, (uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256) _assetPoints, (uint256,uint256,uint256,uint256,uint256) _globalPoints, (uint256,uint256,uint256,uint256,uint256,uint256) _ripeRewards)` | `nonpayable` | — |
| `setEpochData(uint256 _epochStart, uint256 _epochEnd, uint256 _amountAvailInEpoch)` | `nonpayable` | — |
| `setFungibleAuction(address _liqUser, uint256 _vaultId, address _asset, (address,uint256,address,uint256,uint256,uint256,uint256,bool) _auc)` | `nonpayable` | `bool` |
| `setLockedAccount(address _wallet, bool _shouldLock)` | `nonpayable` | — |
| `setRipeAvailForBonds(uint256 _amount)` | `nonpayable` | — |
| `setRipeAvailForHr(uint256 _amount)` | `nonpayable` | — |
| `setRipeAvailForRewards(uint256 _amount)` | `nonpayable` | — |
| `setRipeRewards((uint256,uint256,uint256,uint256,uint256,uint256) _ripeRewards)` | `nonpayable` | — |
| `setUserDebt(address _user, (uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool) _userDebt, uint256 _newYield, (uint256,uint256) _interval)` | `nonpayable` | — |
| `totalDebt()` | `view` | `uint256` |
| `unrealizedYield()` | `view` | `uint256` |
| `updateGreenPoolDebt(address _pool, uint256 _amount, bool _isIncrement)` | `nonpayable` | — |
| `userBorrowPoints(address arg0)` | `view` | `(uint256,uint256,uint256)` |
| `userDebt(address arg0)` | `view` | `(uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool)` |
| `userDepositPoints(address arg0, uint256 arg1, address arg2)` | `view` | `(uint256,uint256,uint256)` |
| `userVaults(address arg0, uint256 arg1)` | `view` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

### Structs declared by this source

- `DepositLedgerData(isParticipatingInVault: bool, numUserVaults: uint256)`
- `RipeRewards(borrowers: uint256, stakers: uint256, voters: uint256, genDepositors: uint256, newRipeRewards: uint256, lastUpdate: uint256)`
- `GlobalDepositPoints(lastUsdValue: uint256, ripeStakerPoints: uint256, ripeVotePoints: uint256, ripeGenPoints: uint256, lastUpdate: uint256)`
- `AssetDepositPoints(balancePoints: uint256, lastBalance: uint256, lastUsdValue: uint256, ripeStakerPoints: uint256, ripeVotePoints: uint256, ripeGenPoints: uint256, lastUpdate: uint256, precision: uint256)`
- `UserDepositPoints(balancePoints: uint256, lastBalance: uint256, lastUpdate: uint256)`
- `BorrowPoints(lastPrincipal: uint256, points: uint256, lastUpdate: uint256)`
- `BorrowPointsBundle(userPoints: BorrowPoints, globalPoints: BorrowPoints, userDebtPrincipal: uint256)`
- `DepositPointsBundle(userPoints: UserDepositPoints, assetPoints: AssetDepositPoints, globalPoints: GlobalDepositPoints)`
- `RipeRewardsBundle(ripeRewards: RipeRewards, ripeAvailForRewards: uint256)`
- `BorrowDataBundle(userDebt: UserDebt, userBorrowInterval: IntervalBorrow, isUserBorrower: bool, numUserVaults: uint256, totalDebt: uint256, numBorrowers: uint256)`
- `RepayDataBundle(userDebt: UserDebt, numUserVaults: uint256)`
- `UserDebt(amount: uint256, principal: uint256, debtTerms: cs.DebtTerms, lastTimestamp: uint256, inLiquidation: bool)`
- `IntervalBorrow(start: uint256, amount: uint256)`
- `FungibleAuction(liqUser: address, vaultId: uint256, asset: address, startDiscount: uint256, maxDiscount: uint256, startBlock: uint256, endBlock: uint256, isActive: bool)`
- `RipeBondData(paymentAmountAvailInEpoch: uint256, ripeAvailForBonds: uint256, badDebt: uint256)`

<!-- END GENERATED API REFERENCE: Ledger -->
