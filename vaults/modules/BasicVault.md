# BasicVault module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/vaults/modules/BasicVault.vy)

## Overview

`BasicVault` uses exact nominal token balances: one recorded unit equals one
asset unit. It binds those nominal balances to real custody and fails closed
when the vault is under-backed.

## Deposit custody binding

The trusted caller transfers tokens into the concrete vault before calling the module. `_depositTokensInVault(user, asset, amount)` requires:

```text
actual custody before >= recorded total before + amount
```

It then credits exactly `amount`; the accounting credit is never clipped to the
raw balance present. Zero amount or zero user/asset is rejected.

The check permits pre-existing surplus custody, but a deposit cannot create an accounting liability not backed at call time.

## Exact withdrawal delivery

Before reducing user accounting, withdrawal requires current custody at least equal to the recorded total. It snapshots recipient and vault balances, reduces the user's nominal amount, transfers the selected amount, then requires:

```text
vaultBefore - vaultAfter == withdrawalAmount
recipientAfter - recipientBefore == withdrawalAmount
```

Fee-on-transfer, rebasing-during-transfer, or otherwise non-exact delivery is rejected atomically. The module returns the actual nominal amount and whether the user's position was depleted.

## Internal balance transfers

AuctionHouse and CreditEngine can move accounting between users without moving custody. The users must be distinct and nonzero, the asset/amount must be nonzero, and actual custody must cover the recorded total before the move.

## Under-backing and downstream quarantine

If raw custody is below the recorded total for an asset:

- `getUserLootBoxShare` returns zero;
- `getTotalAmountForUser` returns zero;
- `getTotalAmountForVault` returns zero; and
- `getUserAssetAndAmountAtIndex` returns the **registered asset address with amount zero**.

Preserving the asset address is intentional. CreditEngine reads that asset's
current debt terms while treating its usable amount as zero. When LTV is
positive, a remaining nominal balance with zero vault-wide usable amount feeds
the `hasQuarantinedAsset` flag and blocks unsafe risk paths. CreditEngine skips
zero-LTV assets before the quarantine scan, so an under-backed zero-LTV position
still returns zero usable/reward amount but does not quarantine account debt.

`getUserAssetAtIndexAndHasBalance` remains a nominal registration/balance query; it is not the usable-collateral view.

## Integration requirements

- Transfer the exact deposit amount into custody before crediting it.
- Do not support fee-on-transfer semantics through BasicVault.
- Use CreditEngine-facing amount views for collateral safety; do not replace them with nominal balance getters.
- Treat an asset-plus-zero result as under-backed/unusable, not absent; consult
  current debt terms before classifying the account as quarantined.

<!-- BEGIN GENERATED API REFERENCE: BasicVault -->
## Exact API reference

> Generated from declarations in `contracts/vaults/modules/BasicVault.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- None.

<!-- END GENERATED API REFERENCE: BasicVault -->
