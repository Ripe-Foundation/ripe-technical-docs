# VaultData module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/vaults/modules/VaultData.vy)

## Overview

`VaultData` provides shared vault storage: per-user balances, per-asset totals, iterable user/vault asset registries, pause state, and tightly constrained ERC-20 recovery. Depending on the consuming vault, stored balances may be nominal token amounts, shares, or a specialized accounting unit.

## Balance storage

`_addBalanceOnDeposit` credits a user and optionally the asset total, then registers the user/asset and vault/asset pair if absent. `_reduceBalanceOnWithdrawal` caps the requested accounting-unit reduction to the user's current balance and reports whether it depleted the user position.

These helpers do not move ERC-20 custody. Concrete vault modules must bind accounting changes to actual incoming/outgoing tokens.

## Iterable registries

User assets and vault assets use 1-based indices; zero means unregistered. Logical counts are the stored next index minus one. Deregistration uses swap-and-pop-style index compression.

Only Lootbox may deregister a user's zero-balance asset. A nonzero balance is not removed. Only Switchboard may call the public vault-asset deregistration route, and `totalBalances[asset]` must be zero.

The module also exposes the same vault-asset removal logic internally through
`_deregisterVaultAsset`. This permits a concrete vault's maintenance lifecycle
to retire a zero-liability asset without making an external self-call.

`doesVaultHaveAnyFunds` checks recorded totals, not raw ERC-20 custody.

## Pause state

Switchboard alone may change pause state, and the value must change. `VaultData` does not automatically guard child methods; each concrete vault/module applies `isPaused` to its own operations.

## Fund recovery

Switchboard may recover up to 20 asset balances per call. Recovery requires:

- nonzero recipient and asset;
- a nonzero raw token balance;
- `indexOfAsset[asset] == 0`; and
- `totalBalances[asset] == 0`.

Thus even a registered asset with zero recorded liability must be deregistered before its raw custody can be recovered. A successful full-balance transfer emits `VaultFundsRecovered`.

Specialized vaults may deliberately override or disable this inherited surface. In particular, current StabilityPool recovery methods always revert.

## Integration requirements

- Do not interpret stored units without the concrete vault module.
- Do not credit deposits until custody has been established by the calling flow.
- Use logical enumeration ranges; stale raw slots outside the range are not authoritative.
- Treat raw custody, recorded total, and user accounting as separate invariants.

<!-- BEGIN GENERATED API REFERENCE: VaultData -->
## Exact API reference

> Generated from declarations in `contracts/vaults/modules/VaultData.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def deregisterUserAsset(_user: address, _asset: address) -> bool`
- `def deregisterVaultAsset(_asset: address) -> bool`
- `def doesUserHaveBalance(_user: address, _asset: address) -> bool`
- `def doesVaultHaveAnyFunds() -> bool`
- `def getNumUserAssets(_user: address) -> uint256`
- `def getNumVaultAssets() -> uint256`
- `def isSupportedVaultAsset(_asset: address) -> bool`
- `def isUserInVaultAsset(_user: address, _asset: address) -> bool`
- `def pause(_shouldPause: bool)`
- `def recoverFunds(_recipient: address, _asset: address)`
- `def recoverFundsMany(_recipient: address, _assets: DynArray[address, MAX_RECOVER_ASSETS])`

### Events declared by this source

- `VaultPauseModified(isPaused: bool)`
- `VaultFundsRecovered(asset: indexed(address), recipient: indexed(address), balance: uint256)`

<!-- END GENERATED API REFERENCE: VaultData -->
