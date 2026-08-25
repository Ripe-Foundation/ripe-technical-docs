# Teller

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/Teller.vy)

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

`setUndyLegoAccess` lets an Underscore wallet or vault caller record the user's
public-action settings plus withdrawal, borrow, Stability-claim, and Lootbox
delegation for any nonzero target. It does not prove that target's current
registry/LegoBook membership. The recorded withdrawal, borrow, Stability-claim,
and Lootbox delegations are directly actionable wherever MissionControl reads
`userDelegation`; only routes that separately call `isUnderscoreOwnerOrLego`
also require current Underscore membership.

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
| `adjustLock(address _asset, uint256 _newLockDuration, address _user, uint256 _vaultId)` | `2–4` | `_user`, `_vaultId` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen, bool _shouldEnterStabPool)` | `0–4` | `_greenAmount`, `_user`, `_wantsSavingsGreen`, `_shouldEnterStabPool` |
| `buyManyFungibleAuctions(tuple[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `1–6` | `_paymentAmount`, `_isPaymentSavingsGreen`, `_shouldTransferBalance`, `_shouldRefundSavingsGreen`, `_recipient` |
| `claimLoot(address _user, bool _shouldStake)` | `0–2` | `_user`, `_shouldStake` |
| `claimLootForManyUsers(address[] _users, bool _shouldStake)` | `1–2` | `_shouldStake` |
| `claimManyFromStabilityPool(uint256 _vaultId, tuple[] _claims, address _user, bool _shouldAutoDeposit)` | `2–4` | `_user`, `_shouldAutoDeposit` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user, uint256 _greenAmount)` | `0–2` | `_user`, `_greenAmount` |
| `deleverageWithSpecificAssets(tuple[] _assets, address _user)` | `1–2` | `_user` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `1–5` | `_amount`, `_user`, `_vaultAddr`, `_vaultId` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration, Addys _a)` | `5–6` | `_a` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration, address _user)` | `3–4` | `_user` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault, Addys _a)` | `5–6` | `_a` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault, Addys _a)` | `4–5` | `_a` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault, Addys _a)` | `4–5` | `_a` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `2–3` | `_mc` |
| `liquidateManyUsers(address[] _liqUsers, bool _wantsSavingsGreen)` | `1–2` | `_wantsSavingsGreen` |
| `liquidateUser(address _liqUser, bool _wantsSavingsGreen)` | `1–2` | `_wantsSavingsGreen` |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt, Addys _a)` | `3–4` | `_a` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient, uint256 _minRipePayout)` | `2–5` | `_lockDuration`, `_recipient`, `_minRipePayout` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount, address _user)` | `4–7` | `_depositAmount`, `_withdrawAmount`, `_user` |
| `redeemCollateralFromMany(tuple[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `1–6` | `_paymentAmount`, `_isPaymentSavingsGreen`, `_shouldTransferBalance`, `_shouldRefundSavingsGreen`, `_recipient` |
| `redeemManyFromStabilityPool(uint256 _vaultId, tuple[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `2–7` | `_paymentAmount`, `_recipient`, `_shouldAutoDeposit`, `_isPaymentSavingsGreen`, `_shouldRefundSavingsGreen` |
| `releaseLock(address _asset, address _user, uint256 _vaultId)` | `1–3` | `_user`, `_vaultId` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `0–4` | `_paymentAmount`, `_user`, `_isPaymentSavingsGreen`, `_shouldRefundSavingsGreen` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt, bool _canAnyoneBondForUser)` | `0–4` | `_user`, `_canAnyoneDeposit`, `_canAnyoneRepayDebt`, `_canAnyoneBondForUser` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool, bool _canClaimLoot)` | `1–6` | `_user`, `_canWithdraw`, `_canBorrow`, `_canClaimFromStabPool`, `_canClaimLoot` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `1–5` | `_amount`, `_user`, `_vaultAddr`, `_vaultId` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault, Addys _a)` | `3–4` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `adjustLock(address _asset, uint256 _newLockDuration)` | `nonpayable` | — |
| `adjustLock(address _asset, uint256 _newLockDuration, address _user)` | `nonpayable` | — |
| `adjustLock(address _asset, uint256 _newLockDuration, address _user, uint256 _vaultId)` | `nonpayable` | — |
| `borrow()` | `nonpayable` | `uint256` |
| `borrow(uint256 _greenAmount)` | `nonpayable` | `uint256` |
| `borrow(uint256 _greenAmount, address _user)` | `nonpayable` | `uint256` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `borrow(uint256 _greenAmount, address _user, bool _wantsSavingsGreen, bool _shouldEnterStabPool)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `nonpayable` | `uint256` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `claimLoot()` | `nonpayable` | `uint256` |
| `claimLoot(address _user)` | `nonpayable` | `uint256` |
| `claimLoot(address _user, bool _shouldStake)` | `nonpayable` | `uint256` |
| `claimLootForManyUsers(address[] _users)` | `nonpayable` | `uint256` |
| `claimLootForManyUsers(address[] _users, bool _shouldStake)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims, address _user)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(uint256 _vaultId, (address,address,uint256)[] _claims, address _user, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool()` | `nonpayable` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user)` | `nonpayable` | `uint256` |
| `convertToSavingsGreenAndDepositIntoStabPool(address _user, uint256 _greenAmount)` | `nonpayable` | `uint256` |
| `deleverageManyUsers((address,uint256)[] _users)` | `nonpayable` | `uint256` |
| `deleverageWithSpecificAssets((uint256,address,uint256)[] _assets)` | `nonpayable` | `uint256` |
| `deleverageWithSpecificAssets((uint256,address,uint256)[] _assets, address _user)` | `nonpayable` | `uint256` |
| `deposit(address _asset)` | `nonpayable` | `uint256` |
| `deposit(address _asset, uint256 _amount)` | `nonpayable` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user)` | `nonpayable` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr)` | `nonpayable` | `uint256` |
| `deposit(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `nonpayable` | `uint256` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `uint256` |
| `depositFromTrusted(address _user, uint256 _vaultId, address _asset, uint256 _amount, uint256 _lockDuration, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration)` | `nonpayable` | `uint256` |
| `depositIntoGovVault(address _asset, uint256 _amount, uint256 _lockDuration, address _user)` | `nonpayable` | `uint256` |
| `depositMany(address _user, (address,uint256,address,uint256)[] _deposits)` | `nonpayable` | `uint256` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault)` | `nonpayable` | `uint256` |
| `depositOnVaultMigration(address _user, address _asset, uint256 _amount, uint256 _targetVaultId, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault)` | `nonpayable` | `uint256` |
| `exportPositionForLegacyRipeGovMigration(address _user, address _asset, address _sourceVault, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault)` | `nonpayable` | `(uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256))` |
| `exportPositionForMigration(address _user, address _asset, address _sourceVault, address _targetVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256))` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `importPositionForMigration(address _user, address _asset, address _sourceVault, uint256 _targetVaultId, address _targetVault, (uint256,uint256,uint256,(uint256,uint256,uint256,bool,uint256)) _migration, address _ledger)` | `nonpayable` | `uint256` |
| `isPaused()` | `view` | `bool` |
| `isUnderscoreWalletOwner(address _user, address _caller)` | `view` | `bool` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `view` | `bool` |
| `liquidateManyUsers(address[] _liqUsers)` | `nonpayable` | `uint256` |
| `liquidateManyUsers(address[] _liqUsers, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `liquidateUser(address _liqUser)` | `nonpayable` | `uint256` |
| `liquidateUser(address _liqUser, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt)` | `nonpayable` | — |
| `performHousekeeping(bool _isHigherRisk, address _user, bool _shouldUpdateDebt, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | — |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount)` | `nonpayable` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration)` | `nonpayable` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient)` | `nonpayable` | `uint256` |
| `purchaseRipeBond(address _paymentAsset, uint256 _paymentAmount, uint256 _lockDuration, address _recipient, uint256 _minRipePayout)` | `nonpayable` | `uint256` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId)` | `nonpayable` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount)` | `nonpayable` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount)` | `nonpayable` | `(uint256, uint256)` |
| `rebalance(address _depositAsset, uint256 _depositVaultId, address _withdrawAsset, uint256 _withdrawVaultId, uint256 _depositAmount, uint256 _withdrawAmount, address _user)` | `nonpayable` | `(uint256, uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _paymentAmount, bool _isPaymentSavingsGreen, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, address _recipient)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(uint256 _vaultId, (address,uint256)[] _redemptions, uint256 _paymentAmount, address _recipient, bool _shouldAutoDeposit, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `releaseLock(address _asset)` | `nonpayable` | — |
| `releaseLock(address _asset, address _user)` | `nonpayable` | — |
| `releaseLock(address _asset, address _user, uint256 _vaultId)` | `nonpayable` | — |
| `repay()` | `nonpayable` | `bool` |
| `repay(uint256 _paymentAmount)` | `nonpayable` | `bool` |
| `repay(uint256 _paymentAmount, address _user)` | `nonpayable` | `bool` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen)` | `nonpayable` | `bool` |
| `repay(uint256 _paymentAmount, address _user, bool _isPaymentSavingsGreen, bool _shouldRefundSavingsGreen)` | `nonpayable` | `bool` |
| `setUndyLegoAccess(address _legoAddr)` | `nonpayable` | `bool` |
| `setUserConfig()` | `nonpayable` | `bool` |
| `setUserConfig(address _user)` | `nonpayable` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit)` | `nonpayable` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt)` | `nonpayable` | `bool` |
| `setUserConfig(address _user, bool _canAnyoneDeposit, bool _canAnyoneRepayDebt, bool _canAnyoneBondForUser)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate, address _user)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool)` | `nonpayable` | `bool` |
| `setUserDelegation(address _delegate, address _user, bool _canWithdraw, bool _canBorrow, bool _canClaimFromStabPool, bool _canClaimLoot)` | `nonpayable` | `bool` |
| `withdraw(address _asset)` | `nonpayable` | `uint256` |
| `withdraw(address _asset, uint256 _amount)` | `nonpayable` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user)` | `nonpayable` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr)` | `nonpayable` | `uint256` |
| `withdraw(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId)` | `nonpayable` | `uint256` |
| `withdrawMany(address _user, (address,uint256,address,uint256)[] _withdrawals)` | `nonpayable` | `uint256` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault)` | `nonpayable` | `(uint256, bool)` |
| `withdrawOnVaultMigration(address _user, address _asset, address _sourceVault, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |

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

<!-- END GENERATED API REFERENCE: Teller -->
