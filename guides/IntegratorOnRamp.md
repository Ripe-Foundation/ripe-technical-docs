# Integration guide

This guide maps common integration work to the contract surface. Use the
generated API inventories on each component page for exact overloads, tuple
order, return types, events, and mutability.

## Resolve dependencies through RipeHq

Protocol departments are resolved through semantic `RipeHq` registry slots.
The address assigned to a slot can change through governance, so integrations
should resolve dependencies at call time instead of embedding department
addresses.

| Role | Registry read | Integration use |
| --- | --- | --- |
| MissionControl | `RipeHq.getAddr(5)` | Asset, vault, user, delegation, and current/historical vault-role configuration |
| PriceDesk | `RipeHq.getAddr(7)` | Canonical protocol price routing and token-scale handling |
| VaultBook | `RipeHq.getAddr(8)` | Vault-ID resolution, registration, and vault metadata |
| Teller | `RipeHq.getAddr(17)` | Normal user transaction gateway |

MissionControl's vault-role pointers are mutable:

- `preferredStabVaultId()` selects the automatic Stability Pool route;
- `coreRipeGovVaultId()` selects the core governance vault; and
- `isStabVaultId(id)` and `isRipeGovVaultId(id)` also recognize historical
  classifications used by existing positions and migrations.

Changing a pointer does not move balances, shares, locks, claim liabilities,
user configuration, or delegation. A client displaying positions should
enumerate the user's actual vault IDs instead of showing only the preferred or
core vault.

## User transaction map

Vyper default arguments create multiple selectors, so a function name alone is
not a complete ABI reference. Use the exact accepted arity and tuple order from
the linked API inventory.

| Intent | Entry point | Contract behavior to account for |
| --- | --- | --- |
| Deposit | [`Teller.deposit` / `depositMany`](../core/Teller.md#exact-api-reference) | Resolve a registered vault and supported asset, then satisfy approval, permission, limit, and pause checks. Credit is based on measured custody. |
| Withdraw | [`Teller.withdraw` / `withdrawMany`](../core/Teller.md#exact-api-reference) | Read the actual vault position and `CreditEngine.getMaxWithdrawableForAsset`. Debt-bearing positive-LTV collateral is account-wide and quarantine-sensitive; the zero-LTV branch remains bounded by actual balance and Teller/vault checks. |
| Borrow | [`Teller.borrow`](../core/Teller.md#exact-api-reference) | Account for debt limits, minimums, interval limits, account lock, pause state, and `hasQuarantinedAsset`. Omitted amount requests the current maximum; delivery prefers sGREEN without Stability Pool entry, but amounts at or below `10**9` GREEN base units remain GREEN. |
| Repay | [`Teller.repay`](../core/Teller.md#exact-api-reference) | Repayment remains available to quarantined accounts. Omitted amount requests the current maximum; payment defaults to GREEN and refunds prefer sGREEN, subject to the same `10**9`-base-unit dust fallback. Bind payer, handling choices, and allowance. |
| Rebalance | [`Teller.rebalance`](../core/Teller.md#exact-api-reference) | Bind both vault IDs and assets. The composed withdrawal and deposit apply both sides' support, limit, custody, and account-health checks. |
| Enter Stability Pool | [`convertToSavingsGreenAndDepositIntoStabPool`](../core/Teller.md#exact-api-reference) or an ordinary deposit | The convenience route resolves the preferred Stability Pool. Existing positions may remain in historically classified pools. |
| Claim liquidated collateral | [`claimManyFromStabilityPool`](../core/Teller.md#exact-api-reference) | Supply the vault ID and one or more `(stabAsset, claimAsset, maxUsdValue)` rows. Active and dormant claim pairs can be claimed; automatic deposit defaults to `false`. |
| Redeem Stability claims with GREEN | [`redeemManyFromStabilityPool`](../core/Teller.md#exact-api-reference) | Supply the vault ID and `(claimAsset, maxGreenAmount)` rows. Recipient defaults to the caller, automatic deposit and sGREEN payment to `false`, and sGREEN refund preference to `true`; an unspent refund at or below `10**9` GREEN base units remains GREEN. |
| Trigger liquidation | [`liquidateUser` / `liquidateManyUsers`](../core/Teller.md#exact-api-reference) | Liquidation is account-wide. A positive-LTV account with unusable backing or price is quarantined until restored. Keeper payout prefers sGREEN by default, with raw GREEN used at or below the dust guard. An all-skipped batch returns zero, though final Teller housekeeping can still revert. |
| Buy fungible auctions | [`buyManyFungibleAuctions`](../core/Teller.md#exact-api-reference) | Use a one-row batch for one auction: `(liqUser, vaultId, asset, maxGreenAmount)`. Rows can skip, but an all-skipped batch reverts. Payment defaults to GREEN, collateral delivery to an external withdrawal, refund preference to sGREEN (with the dust fallback), and recipient to the caller. Set `_shouldTransferBalance=true` to retain in-vault custody and add/checkpoint the recipient. A quote does not reserve debt, price, or collateral. |
| Redeem collateral | [`redeemCollateralFromMany`](../core/Teller.md#exact-api-reference) | Use `(user, vaultId, asset, maxGreenAmount)` rows. Rows can skip, but an all-skipped batch reverts. The payment, delivery, refund, and recipient defaults match auction purchase; in-vault delivery adds/checkpoints the recipient, while external delivery checkpoints only the borrower. CreditRedeem rejects accounts already in liquidation. |
| Deleverage | [`deleverageManyUsers` / `deleverageWithSpecificAssets`](../core/Teller.md#exact-api-reference) | Use `(user, targetRepayAmount)` or `(vaultId, asset, targetRepayAmount)` rows. General batches accept at most 25 users; specific and direct volatile lists accept at most 25 assets. The general route permits a capped permissionless path for a non-liquidating, non-quarantined account near redemption, but reverts if every user skips. Specific-asset calls require self, registered-Ripe, or `canBorrow` authority and, after account screening, revert if no asset is processed. Trusted general/specific, volatile-asset, and admitted withdrawal-time routes may operate during liquidation. Direct withdrawal-time deleverage resolves vault ID zero through MissionControl; `swapCollateral` rejects zero vault IDs. |
| Deposit into RipeGov | [`depositIntoGovVault`](../core/Teller.md#exact-api-reference) | New deposits use the core RipeGov vault. Existing locks may be held by a historically classified vault. |
| Adjust or release a RipeGov lock | [`adjustLock` / `releaseLock`](../core/Teller.md#exact-api-reference) | Pass the explicit vault-ID overload for a historical position. A zero or omitted ID resolves the core RipeGov vault. |
| Buy a RIPE bond | [`purchaseRipeBond`](../core/Teller.md#exact-api-reference) | Pass the payment amount and, where needed, recipient, lock duration, and `minRipePayout`. Omitted lock duration and minimum payout are zero; an omitted recipient is the caller. |
| Claim RIPE rewards | [`claimLoot` / `claimLootForManyUsers`](../core/Teller.md#exact-api-reference) | Account for reward funding, point state, target authority, stake choice, and the core RipeGov route; staking defaults to `true`. A multi-user call performs final Teller housekeeping for the caller rather than a universal Ledger lock check for every target. |

## User permissions and delegated calls

`setUserConfig` defaults third-party deposit, repayment, and bonding permissions
to `false`, and every call replaces the complete three-flag struct. Calling
`setUserConfig(user)` therefore clears all three permissions rather than
preserving prior values.

`setUserDelegation(delegate)` has the opposite defaults: `_user` is the caller
and all four authority flags default to `true`. Every call replaces the full
struct, so passing only `_canWithdraw=false` still grants borrow,
Stability-claim, and Lootbox-claim authority. Zero-address or self-delegation
returns `false` without a state change or event; check the return value.

`setUndyLegoAccess` records all public-action settings and normally writes
withdrawal, borrow, Stability-claim, and Lootbox delegation. Some routes consume
those recorded delegations directly; routes that call
`isUnderscoreOwnerOrLego` also require current Underscore membership. There is
no universal delegation rule shared by all routes.

`setUndyLegoAccess` also fails softly. Missing MissionControl, a zero Lego
address, or an ineligible caller returns `false` instead of reverting. If the
target equals the caller, however, public settings are written while the
self-delegation silently returns `false` without an event, and the outer call
still returns `true`. Read MissionControl state or observe the delegation event
rather than treating the return value alone as proof of both writes.

For an action on another account, identify:

1. the target user;
2. the caller, payer, recipient, and refund recipient;
3. the applicable public permission or delegation;
4. the target account's Ledger lock and action-block state; and
5. whether that route performs housekeeping for the target or caller.

When Teller does perform housekeeping, it runs the selected Ledger
last-touch/pause-lock branch, then calls the configured Curve source's
`addGreenRefPoolSnapshot()` when that registry slot is nonzero, and only then
performs an optional debt update. A `false` snapshot return is ignored, but a
registry/interface/permission or downstream Curve revert rolls back the action.

Fungible-auction delay, duration, discount, purchase, and expiry checks use
native EVM `block.number`. Do not substitute Ledger's action-block identity;
the two may differ on Arbitrum.

## Read and quote path

- Use [MissionControl](../governance/MissionControl.md) for policy and vault-role
  classification.
- Use [VaultBook](../core-modules/VaultBook.md) and the concrete vault for
  registration, supported assets, shares, balances, and position enumeration.
- Decode [`CreditEngine.getUserBorrowTerms`](../core/CreditEngine.md#exact-api-reference)
  as the six-field tuple ending in `hasQuarantinedAsset`.
- Use [PriceDesk](../pricing/PriceDesk.md), rather than a source adapter or a
  monitoring-only RIPE/WETH view, for protocol price resolution.
- Treat `CreditEngine.getDynamicBorrowRate` base-rate fallback narrowly: it
  applies when the Curve slot is zero or the reported weighted ratio is zero or
  below its danger trigger. Typed registry, CurvePrices, and MissionControl
  failures may still revert; CurvePrices pause alone does not force fallback.
- Interpret [`Ledger.lastTouch`](../core/Ledger.md) using the action-block source
  bound by the Ledger constructor.
- Treat quotes and eligibility views as observations, not execution
  reservations. Apply explicit output bounds where the ABI supports them.

## Vault migration

Vault replacement uses the controlled contract path:

```text
governance
  -> SwitchboardEcho
  -> VaultMigrator
  -> Teller migration-only helpers
  -> source and target vaults
```

The Teller migration helpers are callable only by `VaultMigrator` and have
their own pause matrix. Generic vault migration and RipeGov migration are
distinct; RipeGov migration also preserves lock terms and point state. Updating
a MissionControl pointer alone does not transfer any position data.

## Transaction construction checklist

Before submitting a transaction:

1. select the full ABI signature and verify tuple field order;
2. resolve department and vault dependencies through the registries;
3. bind every user, payer, recipient, vault ID, asset, refund choice, allowance,
   and output bound;
4. check the route's permissions, pause guards, limits, account lock,
   liquidation state, quarantine state, and price requirements;
5. simulate the exact calldata against the intended state; and
6. decode returns and events, then verify the route's documented custody, debt,
   share, lock, claim, and housekeeping postconditions.
