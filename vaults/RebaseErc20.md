# RebaseErc20 vault

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/vaults/RebaseErc20.vy)

## Overview

`RebaseErc20` is the concrete share-accounting vault built from Addys, VaultData, and SharesVault. Users own internal shares of raw token custody, allowing rebases or donated yield to accrue proportionally.

## Authority

- Teller alone may deposit.
- Teller, AuctionHouse, or CreditEngine may withdraw.
- AuctionHouse or CreditEngine may transfer user balances internally.
- Switchboard controls inherited vault pause and eligible administration.

All three balance mutations are nonreentrant.

## Accounting behavior

Deposits mint internal shares with a `1e8` virtual-share/one-unit virtual-asset offset and reject a zero-share result. User value and total vault amount are derived from current custody rather than treating stored shares as token amounts.

Withdrawal transfers the requested token amount, measures actual vault outflow and recipient delivery, and permits at most a two-unit delta. Burned shares are bound to actual outflow, with a remaining-holder loss guard. The returned amount is the conservative credited amount, not blindly the request.

Internal transfers round shares down and may return zero for dust instead of taking more value than requested.

## Events and views

Deposit, withdrawal, and transfer events include both asset amounts and share
changes. Public conversion helpers expose `amountToShares` and `sharesToAmount`
behavior using custody at call time.

CreditEngine and Lootbox views use the asset value at call time or the
normalized reward-share unit; raw `userBalances` remain shares.

## Integration requirements

- Never interpret stored user/total balances as token amounts.
- Use returned credited amount and share values.
- Expect share value to move with custody rebases or donations.
- Verify the asset's transfer behavior fits the two-unit delta policy.

<!-- BEGIN GENERATED API REFERENCE: RebaseErc20 -->
## Exact API reference

> Generated from `contracts/vaults/RebaseErc20.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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
| `amountToShares(address _asset, uint256 _amount, bool _shouldRoundUp)` | `view` | `uint256` | — |
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
| `sharesToAmount(address _asset, uint256 _shares, bool _shouldRoundUp)` | `view` | `uint256` | — |
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
| `RebaseErc20VaultDeposit` | `address user indexed, address asset indexed, uint256 amount, uint256 shares` |
| `RebaseErc20VaultTransfer` | `address fromUser indexed, address toUser indexed, address asset indexed, uint256 transferAmount, bool isFromUserDepleted, uint256 transferShares` |
| `RebaseErc20VaultWithdrawal` | `address user indexed, address asset indexed, uint256 amount, bool isDepleted, uint256 shares` |
| `VaultFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `VaultPauseModified` | `bool isPaused` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `not allowed`
- `only Teller allowed`

<!-- END GENERATED API REFERENCE: RebaseErc20 -->
