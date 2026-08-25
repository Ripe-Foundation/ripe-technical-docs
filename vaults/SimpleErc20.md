# SimpleErc20 vault

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/vaults/SimpleErc20.vy)

## Overview

`SimpleErc20` is the concrete exact-balance vault built from Addys, VaultData,
and BasicVault. A recorded unit equals one token unit, and its custody checks
make any under-backed asset unusable through the collateral/reward amount
views. CreditEngine turns that condition into debt quarantine only when the
asset's current LTV is positive.

## Authority

- Teller alone may deposit.
- Teller, AuctionHouse, or CreditEngine may withdraw.
- AuctionHouse or CreditEngine may transfer balances between users.
- Switchboard controls inherited pause, asset deregistration, and eligible fund recovery.

The three mutating balance routes are nonreentrant and unavailable while the vault is paused.

## Deposit, withdrawal, and transfer

Teller transfers custody before calling `depositTokensInVault`. The vault credits exactly the supplied amount only if raw custody covers all prior nominal liabilities plus that amount.

Withdrawal snapshots vault and recipient balances and accepts only exact requested outflow and exact recipient delivery. Tokens with transfer fees or other delta behavior revert atomically.

Internal transfer moves nominal accounting between distinct users without moving custody and requires the asset to remain fully backed.

Events record exact credited/debited amounts and user depletion status.

## Under-backing behavior

When custody falls below recorded total:

- collateral/reward amount views return zero;
- CreditEngine enumeration preserves the asset address but returns zero usable amount; and
- new deposits, withdrawals, and internal transfers cannot silently legitimize the deficit.

The preserved address lets CreditEngine load current debt terms before deciding
how to handle the unusable amount. A positive-LTV nominal position can surface
`hasQuarantinedAsset`; CreditEngine skips a zero-LTV asset before its quarantine
scan, so the same custody deficit suppresses its usable amount and reward share
without quarantining account debt.

## Integration requirements

- Treat nominal balances and actual custody as separate values.
- Use the returned amount/depletion result rather than assuming request success.
- Do not use `getUserAssetAtIndexAndHasBalance` as a usable-collateral valuation.
- Resolve authorized department addresses through current RipeHq rather than caching permanent numeric vault IDs.

<!-- BEGIN GENERATED API REFERENCE: SimpleErc20 -->
## Exact API reference

> Generated from `contracts/vaults/SimpleErc20.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, Addys _a)` | `3–4` | `_a = empty(addys.Addys)` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, Addys _a)` | `4–5` | `_a = empty(addys.Addys)` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, Addys _a)` | `4–5` | `_a = empty(addys.Addys)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `depositTokensInVault(address _user, address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `deregisterUserAsset(address _user, address _asset)` | `nonpayable` | `bool` | — |
| `deregisterVaultAsset(address _asset)` | `nonpayable` | `bool` | — |
| `doesUserHaveBalance(address _user, address _asset)` | `view` | `bool` | — |
| `doesVaultHaveAnyFunds()` | `view` | `bool` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getNumUserAssets(address _user)` | `view` | `uint256` | — |
| `getNumVaultAssets()` | `view` | `uint256` | — |
| `getRipeHq()` | `view` | `address` | — |
| `getTotalAmountForUser(address _user, address _asset)` | `view` | `uint256` | `uint256` |
| `getTotalAmountForVault(address _asset)` | `view` | `uint256` | `uint256` |
| `getUserAssetAndAmountAtIndex(address _user, uint256 _index)` | `view` | `(address, uint256)` | `(address, uint256)` |
| `getUserAssetAtIndexAndHasBalance(address _user, uint256 _index)` | `view` | `(address, bool)` | `(address, bool)` |
| `getUserLootBoxShare(address _user, address _asset)` | `view` | `uint256` | `uint256` |
| `getVaultDataOnDeposit(address _user, address _asset)` | `view` | `(bool hasPosition, uint256 numAssets, uint256 userBalance, uint256 totalBalance)` | `Vault.VaultDataOnDeposit` |
| `indexOfAsset(address arg0)` | `view` | `uint256` | — |
| `indexOfUserAsset(address arg0, address arg1)` | `view` | `uint256` | — |
| `isPaused()` | `view` | `bool` | — |
| `isSupportedVaultAsset(address _asset)` | `view` | `bool` | — |
| `isUserInVaultAsset(address _user, address _asset)` | `view` | `bool` | — |
| `numAssets()` | `view` | `uint256` | — |
| `numUserAssets(address arg0)` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `totalBalances(address arg0)` | `view` | `uint256` | — |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |
| `userAssets(address arg0, uint256 arg1)` | `view` | `address` | — |
| `userBalances(address arg0, address arg1)` | `view` | `uint256` | — |
| `vaultAssets(uint256 arg0)` | `view` | `address` | — |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` | `(uint256, bool)` |

### Events

| Event | Fields |
| --- | --- |
| `SimpleErc20VaultDeposit` | `address user indexed, address asset indexed, uint256 amount` |
| `SimpleErc20VaultTransfer` | `address fromUser indexed, address toUser indexed, address asset indexed, uint256 transferAmount, bool isFromUserDepleted` |
| `SimpleErc20VaultWithdrawal` | `address user indexed, address asset indexed, uint256 amount, bool isDepleted` |
| `VaultFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `VaultPauseModified` | `bool isPaused` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `not allowed`
- `only Teller allowed`

<!-- END GENERATED API REFERENCE: SimpleErc20 -->
