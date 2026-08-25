# SharesVault module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/vaults/modules/SharesVault.vy)

## Overview

`SharesVault` tracks users in internal shares while raw ERC-20 custody determines the current asset value. It is used for rebasing/yield-bearing custody where nominal token balances should accrue proportionally to share holders.

The module uses full-precision conversion arithmetic, rejects zero-share
deposits, and binds burned shares to measured vault outflow and recipient
delivery.

## Share conversion

The module uses a virtual offset:

```text
virtual total shares = recorded shares + 1e8
virtual total assets = raw custody + 1
```

Conversions use 512-bit-style full-precision `mulDiv`, with explicit up/down rounding. This avoids intermediate multiplication overflow when the final quotient fits.

`amountToShares` and `sharesToAmount` expose the same conversion rules using
custody at call time.

## Deposits

The trusted caller transfers assets before invoking `_depositTokensInVault`. The module derives the pre-deposit custody by subtracting the admitted deposit amount from current custody, calculates shares with downward rounding, and rejects a zero-share result.

It credits shares to the user and total share accounting, while returning both admitted asset amount and new shares.

## Withdrawals and custody deltas

The module first determines requested shares/assets, snapshots vault and recipient balances, and transfers the requested assets **before** reducing recorded shares. It then measures:

```text
actualOutflow = vaultBefore - vaultAfter
actualDelivery = recipientAfter - recipientBefore
```

Each may differ from the requested amount by at most two token units. Larger deltas revert. Credited withdrawal amount is the minimum of request, outflow, and delivery and must be nonzero.

If actual outflow differs from the request, burned shares are recomputed from actual outflow with upward rounding. If that exceeds the user's shares, it may be capped only when that user owns the entire outstanding share supply; otherwise the operation reverts to prevent remaining-holder loss.

The recipient cannot be the vault itself.

## Internal transfers

An internal user-to-user transfer moves shares, not custody. For a partial asset request it rounds shares down, then recomputes the asset amount represented by those shares. Dust that maps to zero shares/amount returns `(0, 0, false)` instead of overcharging the sender.

## Consumer views

- Deposit data and user amounts use raw custody at call time.
- CreditEngine enumeration returns the asset value represented by user shares
  at call time.
- Lootbox share uses internal shares divided by the `1e8` decimal offset.
- total vault amount is raw token custody, not recorded total shares.

## Integration requirements

- Treat `totalBalances` as shares for this module.
- Use returned credited amount rather than assuming requested transfer amount.
- Do not widen the two-unit transfer tolerance without asset-specific analysis.
- Preserve upward rounding for external withdrawals and downward rounding for internal transfers.
- Do not credit a deposit that produces zero shares.

<!-- BEGIN GENERATED API REFERENCE: SharesVault -->
## Exact source-declared API reference

> Generated from declarations in `contracts/vaults/modules/SharesVault.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__()`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def amountToShares(_asset: address, _amount: uint256, _shouldRoundUp: bool) -> uint256` | `3` | `view` | `uint256` |
| `def sharesToAmount(_asset: address, _shares: uint256, _shouldRoundUp: bool) -> uint256` | `3` | `view` | `uint256` |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `amountToShares(address _asset, uint256 _amount, bool _shouldRoundUp)` | `view` | `uint256` |
| `sharesToAmount(address _asset, uint256 _shares, bool _shouldRoundUp)` | `view` | `uint256` |

### Constants declared by this source

- `DECIMAL_OFFSET: uint256 = 10 ** 8`
- `MAX_TRANSFER_DELTA: uint256 = 2`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot receive 0 shares`
- `cannot withdraw 0 shares`
- `contract paused`
- `invalid deposit amount`
- `invalid recipient`
- `invalid recipient delivery`
- `invalid user or asset`
- `invalid user, asset, or recipient`
- `invalid users or asset`
- `invalid vault outflow`
- `no asset to withdraw`
- `no credited withdrawal amount`
- `no withdrawal amount`
- `remaining holder loss`
- `result overflows`
- `token transfer failed`
- `user has no shares`
- `zero denominator`

<!-- END GENERATED API REFERENCE: SharesVault -->
