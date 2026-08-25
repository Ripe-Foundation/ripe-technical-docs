# Teller

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/Teller.vy)

## Purpose

`Teller` is the primary user gateway. It validates caller authority and action timing, coordinates exact token custody, and delegates accounting to VaultBook, CreditEngine, AuctionHouse, CreditRedeem, Stability Pool, Deleverage, Lootbox, BondRoom, and governance-vault components.

Teller is deliberately thin on persistent business state: downstream departments remain authoritative for debt, auctions, balances, rewards, and configuration.

## Vault operations

- `deposit`, `depositMany`, and `depositFromTrusted` validate the current vault/asset registration and deposit permission before crediting a user.
- `withdraw` and `withdrawMany` apply authority, balance, and CreditEngine maximum-withdrawal checks.
- `rebalance` moves eligible value between vaults under current configuration.

Deposits use measured custody and a transient guard. When Teller already holds the input, the request must consume that exact amount; validation does not silently clamp a partial deposit. Registration and support are rechecked at the point of use, and the credited vault amount must reconcile with custody.

For generic deposits and withdrawals, `_vaultId == 0` is a resolution sentinel,
not vault ID zero. If both the vault address and ID are omitted, TellerUtils uses
MissionControl's first configured vault for the asset. If a vault address is
supplied with ID zero, TellerUtils resolves its registered ID; a nonzero ID is
resolved through VaultBook and, when an address is also supplied, the two must
match.

## Credit and liquidation operations

Teller exposes user routes for borrowing, repayment, collateral redemption,
liquidation, fungible-auction purchases, and deleveraging. The following
operations use batch selectors; a one-item batch handles a single operation:

- `redeemCollateralFromMany`
- `buyManyFungibleAuctions`
- `claimManyFromStabilityPool`
- `redeemManyFromStabilityPool`
- `deleverageManyUsers`
- `deleverageWithSpecificAssets`

Credit-redemption and auction-purchase rows may be skipped individually, but
their batch reverts when aggregate GREEN spent is zero. The general deleverage
batch similarly reverts when no user repays anything. Liquidation differs:
`liquidateManyUsers` returns zero when every user is skipped, although Teller's
final caller-housekeeping step can still independently revert. General
deleverage batches accept at most 25 users, and specific-asset deleverage
accepts at most 25 asset rows.

`deleverageManyUsers` is not an owner-only convenience call. Teller forwards
the actual caller, and Deleverage permits an untrusted caller to process a
non-liquidating, non-quarantined near-redemption account under a calculated
repayment cap. A registered Ripe caller, a registered Underscore self-call, or
cross-user `canBorrow` delegation selects the trusted general branch. The
`deleverageWithSpecificAssets` route has no permissionless branch and requires
self, registered-Ripe, or `canBorrow` authority.

Unused GREEN from batch redemption or auction purchase is returned to the
actual payer under the selected GREEN/sGREEN handling. Downstream checks at
execution determine the final result; a Teller call does not reserve a price,
debt amount, or collateral balance in advance.

### Defaults that change execution

- Default deposit and withdrawal amounts are `max_value(uint256)`, which asks
  the route for the maximum it can execute under the current balance, limits,
  and checks; it is not an unconditional whole-balance instruction.
- `borrow()` requests the current maximum, prefers sGREEN, and does not enter
  the Stability Pool. `repay()` requests the current maximum, pays in GREEN,
  and prefers any refund in sGREEN.
- Liquidation keeper rewards prefer sGREEN by default. `claimLoot` and
  `claimLootForManyUsers` default to staking the RIPE payout.
- Stability Pool claims default to external delivery rather than automatic
  deposit.
- Collateral redemption and fungible-auction purchases default to GREEN
  payment, external token delivery (`_shouldTransferBalance == false`), an
  sGREEN-preferred refund, and `msg.sender` as recipient.

The sGREEN Booleans select a preference, not a guaranteed output token.
CreditEngine, AuctionHouse, CreditRedeem, and StabVault's redemption-refund
helper deliver raw GREEN when the handled amount is at or below `10**9` base
units because wrapping that dust can fail.

## Stability, rewards, governance, and bonds

Additional routes convert sGREEN and Stability positions, claim/redeem across Stability vaults, claim Lootbox rewards, deposit into governance vaults, and manage governance locks.

Lock operations are vault-aware: `adjustLock` and `releaseLock` include a vault
ID so integrations do not assume a single fixed RipeGov vault. For these two
routes, `_vaultId == 0` means MissionControl's current core RipeGov vault; a
nonzero value must be a current or historical RipeGov vault ID. Bond purchases
also resolve the current core RipeGov vault dynamically. `purchaseRipeBond`
takes an explicit payment amount and an optional `minRipePayout`; Teller checks
the minimum after BondRoom returns, so a short payout reverts atomically.
`_minRipePayout` defaults to zero, so payout-slippage protection is opt-in and
callers that omit it accept any otherwise-valid nonzero payout. Omitted
`_lockDuration` is zero and omitted `_recipient` is `msg.sender`.

## User configuration and Underscore

`setUserConfig` defaults `canAnyoneDeposit`, `canAnyoneRepayDebt`, and
`canAnyoneBondForUser` to `false`; those third-party permissions are opt-in.

> **Integration warning:** Every call writes the complete three-flag struct. An
> omitted trailing flag is written as `false`, not preserved from the user's
> previous config. In particular, `setUserConfig(user)` clears all three
> permissions; clients must resubmit every intended value.

`setUserDelegation(delegate)` defaults `_user` to `msg.sender` and all four
delegation flags to `true`. For example, specifying only
`_canWithdraw = false` still grants borrow, Stability-claim, and Lootbox-claim
authority. Every call replaces the complete four-flag struct rather than
preserving omitted values. A zero delegate or self-delegation returns `false`
without writing state or emitting `UserDelegationSet`; clients should check the
return value.

`setUndyLegoAccess` lets an Underscore wallet or vault caller record all three
public-action settings and, for a different nonzero target, withdrawal, borrow,
Stability-claim, and Lootbox delegation. It does not prove that target's
current registry/LegoBook membership. The recorded delegations are directly
actionable wherever MissionControl reads `userDelegation`; only routes that
separately call `isUnderscoreOwnerOrLego` also require current Underscore
membership.

`setUndyLegoAccess` is deliberately fail-soft: a missing MissionControl address,
a zero Lego address, or a caller that is not a current Underscore wallet or
vault returns `false` without applying access. A self-target is a narrower edge:
the public settings are written, the internal self-delegation returns `false`
without an event, that result is ignored, and the outer call returns `true`.
Consequently, even a `true` result does not by itself prove a delegation was
written; clients should read MissionControl state or observe
`UserDelegationSet` when that distinction matters.

## `lastTouch` route matrix

`_performHousekeeping` has three materially different `lastTouch` outcomes. The
table names the account whose Ledger row is affected, which is not always the
economic target of the operation.

| Class | Routes and affected account | `lastTouch` effect |
| --- | --- | --- |
| Gated | `withdraw`, `withdrawMany`, `rebalance`, `borrow`, `claimManyFromStabilityPool`, and `releaseLock` for their `_user`; any valid Ripe caller using `performHousekeeping(True, user, ...)` | On success, always writes the current action block. It first rejects an existing touch in that action block only when MissionControl enables the check, the call is higher-risk, and the affected account is not a current Underscore wallet or vault. |
| Always write, never same-action gated | Self-targeted `deposit`, `depositMany`, `repay`, `redeemCollateralFromMany` (recipient), `buyManyFungibleAuctions` (recipient), `convertToSavingsGreenAndDepositIntoStabPool`, `redeemManyFromStabilityPool` (recipient), `claimLoot`, `depositIntoGovVault`, and `purchaseRipeBond`; `adjustLock` for its `_user`; `liquidateUser`/`liquidateManyUsers` and `claimLootForManyUsers` for `msg.sender`; `Deleverage.swapCollateral` for its `_user`; any valid Ripe caller using `performHousekeeping(False, user, ...)` | Calls `checkAndUpdateLastTouch(..., False)`: it writes and enforces Ledger pause/lock state, but does not reject a prior same-action-block touch. |
| Never write the target | Third-party targets of the conditional low-risk routes in the prior row; liquidation subjects; collateral-redemption borrowers; fungible-auction sellers; the individual target rows in `claimLootForManyUsers` (the separate final write is only for `msg.sender`, including when that address is also a row); `depositFromTrusted` and the five low-level migration selectors; Teller's `deleverageManyUsers` and `deleverageWithSpecificAssets`; direct `Deleverage.deleverageWithVolAssets` and `Deleverage.deleverageForWithdrawal` | No target `lastTouch` write. Conditional third-party Teller housekeeping still checks Ledger pause/lock state; routes with no housekeeping do not gain that check implicitly. A coordinating department may perform separate housekeeping, as VaultMigrator does after a successful move. |

The action block is Ledger's constructor-selected clock: native EVM
`block.number` when `ACTION_BLOCK_SOURCE` is zero, otherwise
`ArbSys(0x64).arbBlockNumber()`. It is separate from other duration
calculations. `isUnderscoreWalletOwner` exposes the owner test used by
integrations.

After its receipt-measurement guard, every `_performHousekeeping` call applies
the selected Ledger branch: either it checks and writes `lastTouch`, or it
checks Ledger pause and account lock state without writing. Teller then resolves
its constructor-bound Curve source ID through PriceDesk's registry and, when
that address is nonzero, calls
`addGreenRefPoolSnapshot()` before the optional debt update. A `false` snapshot
return is ignored, while registry/interface/permission or downstream Curve
reverts propagate and roll back the enclosing Teller action. A successful call
can update Curve source state and emit its snapshot event even on a route whose
primary purpose is unrelated to pricing.

## Migration routes

The migration deposit/withdrawal entry points are callable only by [VaultMigrator](./VaultMigrator.md) and require the prescribed paused/unpaused states. They are not general user escape hatches and should not be called as ordinary vault routes.

## Constructor and dynamic roles

The constructor binds a Curve price-source ID. Core, preferred Stability, and
RipeGov vault IDs are read from MissionControl when their routes execute.

## Security properties

- Exact custody and nonreentrant/transient guards prevent partial-credit and reentry inconsistencies.
- Teller revalidates current registry and permission state before downstream calls.
- Department contracts, not Teller or front-end quotes, remain authoritative for final accounting.
- Batch-only actions use a one-row batch when operating on one item.

<!-- BEGIN GENERATED API REFERENCE: Teller -->
## Exact API reference

> Generated from `contracts/core/Teller.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, bool _shouldPause, uint256 _curvePricesId)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `adjustLock(address _asset, uint256 _newLockDuration, address _user, uint256 _vaultId)` | `2–4` | `_user = msg.sender`, `_vaultId = 0` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen, bool _shouldEnterStabPool)` | `0–4` | `_greenAmount = max_value(uint256)`, `_user = msg.sender`, `_wantsSavingsGreen = True`, `_shouldEnterStabPool = False` |
| `buyManyFungibleAuctions(tuple[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `1–6` | `_paymentAmount = max_value(uint256)`, `_isPaymentSavingsGreen = False`, `_shouldTransferBalance = False`, `_shouldRefundSavingsGreen = True`, `_recipient = msg.sender` |
| `claimLoot(address _user, bool _shouldStake)` | `0–2` | `_user = msg.sender`, `_shouldStake = True` |
| `claimLootForManyUsers(address[] _users, bool _shouldStake)` | `1–2` | `_shouldStake = True` |
| `claimManyFromStabilityPool(uint256 _vaultId, tuple[] _claims, address _user, bool _shouldAutoDeposit)` | `2–4` | `_user = msg.sender`, `_shouldAutoDeposit = False` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user, uint256 _greenAmount)` | `0–2` | `_user = msg.sender`, `_greenAmount = max_value(uint256)` |
| `deleverageWithSpecificAssets(tuple[] _assets, address _user)` | `1–2` | `_user = msg.sender` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `1–5` | `_amount = max_value(uint256)`, `_user = msg.sender`, `_vaultAddr = empty(address)`, `_vaultId = 0` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration, Addys _a)` | `5–6` | `_a = empty(addys.Addys)` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration, address _user)` | `3–4` | `_user = msg.sender` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault, Addys _a)` | `5–6` | `_a = empty(addys.Addys)` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault, Addys _a)` | `4–5` | `_a = empty(addys.Addys)` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault, Addys _a)` | `4–5` | `_a = empty(addys.Addys)` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `2–3` | `_mc = empty(address)` |
| `liquidateManyUsers(address[] _liqUsers, bool _wantsSavingsGreen)` | `1–2` | `_wantsSavingsGreen = True` |
| `liquidateUser(address _liqUser, bool _wantsSavingsGreen)` | `1–2` | `_wantsSavingsGreen = True` |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt, Addys _a)` | `3–4` | `_a = empty(addys.Addys)` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient, uint256 _minRipePayout)` | `2–5` | `_lockDuration = 0`, `_recipient = msg.sender`, `_minRipePayout = 0` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount, address _user)` | `4–7` | `_depositAmount = max_value(uint256)`, `_withdrawAmount = max_value(uint256)`, `_user = msg.sender` |
| `redeemCollateralFromMany(tuple[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `1–6` | `_paymentAmount = max_value(uint256)`, `_isPaymentSavingsGreen = False`, `_shouldTransferBalance = False`, `_shouldRefundSavingsGreen = True`, `_recipient = msg.sender` |
| `redeemManyFromStabilityPool(uint256 _vaultId, tuple[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `2–7` | `_paymentAmount = max_value(uint256)`, `_recipient = msg.sender`, `_shouldAutoDeposit = False`, `_isPaymentSavingsGreen = False`, `_shouldRefundSavingsGreen = True` |
| `releaseLock(address _asset, address _user, uint256 _vaultId)` | `1–3` | `_user = msg.sender`, `_vaultId = 0` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `0–4` | `_paymentAmount = max_value(uint256)`, `_user = msg.sender`, `_isPaymentSavingsGreen = False`, `_shouldRefundSavingsGreen = True` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt, bool _canAnyoneBondForUser)` | `0–4` | `_user = msg.sender`, `_canAnyoneDeposit = False`, `_canAnyoneRepayDebt = False`, `_canAnyoneBondForUser = False` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool, bool _canClaimLoot)` | `1–6` | `_user = msg.sender`, `_canWithdraw = True`, `_canBorrow = True`, `_canClaimFromStabPool = True`, `_canClaimLoot = True` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `1–5` | `_amount = max_value(uint256)`, `_user = msg.sender`, `_vaultAddr = empty(address)`, `_vaultId = 0` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault, Addys _a)` | `3–4` | `_a = empty(addys.Addys)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `adjustLock(address _asset, uint256 _newLockDuration)` | `nonpayable` | — | — |
| `adjustLock(address _asset, uint256 _newLockDuration, address _user)` | `nonpayable` | — | — |
| `adjustLock(address _asset, uint256 _newLockDuration, address _user, uint256 _vaultId)` | `nonpayable` | — | — |
| `borrow()` | `nonpayable` | `uint256` | `uint256` |
| `borrow(uint256 _greenAmount)` | `nonpayable` | `uint256` | `uint256` |
| `borrow(uint256 _greenAmount, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen, bool _shouldEnterStabPool)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `nonpayable` | `uint256` | `uint256` |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `claimLoot()` | `nonpayable` | `uint256` | `uint256` |
| `claimLoot(address _user)` | `nonpayable` | `uint256` | `uint256` |
| `claimLoot(address _user, bool _shouldStake)` | `nonpayable` | `uint256` | `uint256` |
| `claimLootForManyUsers(address[] _users)` | `nonpayable` | `uint256` | `uint256` |
| `claimLootForManyUsers(address[] _users, bool _shouldStake)` | `nonpayable` | `uint256` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims)` | `nonpayable` | `uint256` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims, address _user, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool()` | `nonpayable` | `uint256` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user)` | `nonpayable` | `uint256` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user, uint256 _greenAmount)` | `nonpayable` | `uint256` | `uint256` |
| `deleverageManyUsers((address,uint256)[] _users)` | `nonpayable` | `uint256` | `uint256` |
| `deleverageWithSpecificAssets((uint256,address,uint256)[] _assets)` | `nonpayable` | `uint256` | `uint256` |
| `deleverageWithSpecificAssets((uint256,address,uint256)[] _assets, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `deposit(address _asset)` | `nonpayable` | `uint256` | `uint256` |
| `deposit(address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr)` | `nonpayable` | `uint256` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `nonpayable` | `uint256` | `uint256` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `depositMany(address _user, (address,uint256,address,uint256)[] _deposits)` | `nonpayable` | `uint256` | `uint256` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault)` | `nonpayable` | `uint256` | `uint256` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault)` | `nonpayable` | `uint256` | `uint256` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault)` | `nonpayable` | `(uint256 amount, uint256 govPoints, uint256 unlock, (uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee) lastTerms)` | `RipeGovMigrationData` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256 amount, uint256 govPoints, uint256 unlock, (uint256 minLockDuration, uint256 maxLockDuration, uint256 maxLockBoost, bool canExit, uint256 exitFee) lastTerms)` | `RipeGovMigrationData` |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getRipeHq()` | `view` | `address` | — |
| `importPositionForMigration(address _user, address _asset, address _sourceVault, uint256 _targetVaultId, address _targetVault, (uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256)) _migration, address _ledger)` | `nonpayable` | `uint256` | `uint256` |
| `isPaused()` | `view` | `bool` | — |
| `isUnderscoreWalletOwner(address _user, address _caller)` | `view` | `bool` | `bool` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `view` | `bool` | `bool` |
| `liquidateManyUsers(address[] _liqUsers)` | `nonpayable` | `uint256` | `uint256` |
| `liquidateManyUsers(address[] _liqUsers, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `liquidateUser(address _liqUser)` | `nonpayable` | `uint256` | `uint256` |
| `liquidateUser(address _liqUser, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt)` | `nonpayable` | — | — |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — | — |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount)` | `nonpayable` | `uint256` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration)` | `nonpayable` | `uint256` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient)` | `nonpayable` | `uint256` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient, uint256 _minRipePayout)` | `nonpayable` | `uint256` | `uint256` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount, address _user)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `releaseLock(address _asset)` | `nonpayable` | — | — |
| `releaseLock(address _asset, address _user)` | `nonpayable` | — | — |
| `releaseLock(address _asset, address _user, uint256 _vaultId)` | `nonpayable` | — | — |
| `repay()` | `nonpayable` | `bool` | `bool` |
| `repay(uint256 _paymentAmount)` | `nonpayable` | `bool` | `bool` |
| `repay(uint256 _paymentAmount, address _user)` | `nonpayable` | `bool` | `bool` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen)` | `nonpayable` | `bool` | `bool` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `nonpayable` | `bool` | `bool` |
| `setUndyLegoAccess(address _legoAddr)` | `nonpayable` | `bool` | `bool` |
| `setUserConfig()` | `nonpayable` | `bool` | `bool` |
| `setUserConfig(address _user)` | `nonpayable` | `bool` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit)` | `nonpayable` | `bool` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt)` | `nonpayable` | `bool` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt, bool _canAnyoneBondForUser)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate, address _user)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool)` | `nonpayable` | `bool` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool, bool _canClaimLoot)` | `nonpayable` | `bool` | `bool` |
| `withdraw(address _asset)` | `nonpayable` | `uint256` | `uint256` |
| `withdraw(address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr)` | `nonpayable` | `uint256` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `nonpayable` | `uint256` | `uint256` |
| `withdrawMany(address _user, (address,uint256,address,uint256)[] _withdrawals)` | `nonpayable` | `uint256` | `uint256` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `TellerDeposit` | `address user indexed, address depositor indexed, address asset indexed, uint256 amount, address vaultAddr, uint256 vaultId` |
| `TellerRebalance` | `address user indexed, address caller indexed, address depositAsset indexed, address withdrawAsset, uint256 depositAmount, uint256 withdrawAmount, uint256 depositVaultId, uint256 withdrawVaultId` |
| `TellerWithdrawal` | `address user indexed, address asset indexed, address caller indexed, uint256 amount, address vaultAddr, uint256 vaultId, bool isDepleted` |
| `UserConfigSet` | `address user indexed, bool canAnyoneDeposit, bool canAnyoneRepayDebt, bool canAnyoneBondForUser, address caller indexed` |
| `UserDelegationSet` | `address user indexed, address delegate indexed, bool canWithdraw, bool canBorrow, bool canClaimFromStabPool, bool canClaimLoot, address caller indexed` |

### Structs declared by this source

- `RipeGovMigrationData(amount: uint256, govPoints: uint256, unlock: uint256, lastTerms: cs.LockTerms)`
- `DepositLedgerData(isParticipatingInVault: bool, numUserVaults: uint256)`
- `DepositAction(asset: address, amount: uint256, vaultAddr: address, vaultId: uint256)`
- `TellerWithdrawConfig(canWithdrawGeneral: bool, canWithdrawAsset: bool, isUserAllowed: bool, canWithdrawForUser: bool, minDepositBalance: uint256)`
- `WithdrawalAction(asset: address, amount: uint256, vaultAddr: address, vaultId: uint256)`
- `CollateralRedemption(user: address, vaultId: uint256, asset: address, maxGreenAmount: uint256)`
- `FungAuctionPurchase(liqUser: address, vaultId: uint256, asset: address, maxGreenAmount: uint256)`
- `StabPoolClaim(stabAsset: address, claimAsset: address, maxUsdValue: uint256)`
- `StabPoolRedemption(claimAsset: address, maxGreenAmount: uint256)`
- `DeleverageUserRequest(user: address, targetRepayAmount: uint256)`
- `DeleverageAsset(vaultId: uint256, asset: address, targetRepayAmount: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `account locked`
- `bad debt health`
- `cannot delegate to owner`
- `cannot deposit 0`
- `cannot deposit 0 green`
- `cannot transfer 0 amount`
- `cannot withdraw 0`
- `contract paused`
- `could not transfer`
- `custody mismatch`
- `deposit failed`
- `empty batch`
- `green approval failed`
- `invalid recipient`
- `invalid vault`
- `invalid vault id`
- `minimum payout not met`
- `no perms`
- `not activated`
- `not owner of underscore wallet`
- `only ripe addr allowed`
- `only vault migrator allowed`
- `receipt measurement active`
- `receipt window active`
- `savings green redeem failed`
- `teller not paused`
- `token transfer failed`
- `too small a balance`

<!-- END GENERATED API REFERENCE: Teller -->
