# Vault interface

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/interfaces/Vault.vyi)

`Vault.vyi` defines the common custody/accounting surface used by Teller,
CreditEngine, AuctionHouse, Lootbox, VaultBook, and migration code.

## Core mutations

The common mutation surface supports:

- deposit on behalf of a user;
- withdrawal to a recipient;
- balance transfer between users within one vault;
- user-asset and vault-asset deregistration; and
- standard Department pause and recovery controls.

Core operations accept an optional cached `Addys` struct. A nonempty cache may
avoid repeated registry reads, but its caller is responsible for supplying the
correct current protocol addresses.

Implementations return measured amounts and, for withdrawal/transfer, a boolean
whose exact position-cleanup meaning is defined by the implementation. Callers
must use the exact ABI and implementation behavior rather than assume the
requested amount was delivered unchanged.

## Read surface

The interface exposes:

- per-user asset enumeration and membership;
- per-vault supported-asset count and membership (host ABIs may separately
  export indexed enumeration);
- user and vault totals;
- deposit pre-state through `VaultDataOnDeposit`;
- Lootbox share and indexed asset/balance helpers;
- `doesVaultHaveAnyFunds()` for registry retirement checks; and
- standard pause state.

`VaultDataOnDeposit` reports whether the user already has the position, the
user's asset count, current user balance, and current vault total balance.

## Safety boundary

This interface specifies callable shape, not custody semantics. Concrete vault
implementations add backing, delivery, transfer-delta, share-mint, quarantine,
and migration checks that are not expressible in `Vault.vyi` alone.

Similarly, `doesVaultHaveAnyFunds()` is only the generic registry signal.
VaultBook adds nonzero RipeGov point residue and historical
RipeGov/StabilityPool interface constraints when replacing or disabling
specialized vault IDs.

<!-- BEGIN GENERATED API REFERENCE: Vault -->
## Exact source-declared API reference

> Generated from declarations in `interfaces/Vault.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def depositTokensInVault(_user: address, _asset: address, _amount: uint256, _a: addys.Addys = empty(addys.Addys)) -> uint256` | `3–4` | `nonpayable` | `uint256` |
| `def deregisterUserAsset(_user: address, _asset: address) -> bool` | `2` | `nonpayable` | `bool` |
| `def deregisterVaultAsset(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def doesUserHaveBalance(_user: address, _asset: address) -> bool` | `2` | `view` | `bool` |
| `def doesVaultHaveAnyFunds() -> bool` | `0` | `view` | `bool` |
| `def getNumUserAssets(_user: address) -> uint256` | `1` | `view` | `uint256` |
| `def getNumVaultAssets() -> uint256` | `0` | `view` | `uint256` |
| `def getTotalAmountForUser(_user: address, _asset: address) -> uint256` | `2` | `view` | `uint256` |
| `def getTotalAmountForVault(_asset: address) -> uint256` | `1` | `view` | `uint256` |
| `def getUserAssetAndAmountAtIndex(_user: address, _index: uint256) -> (address, uint256)` | `2` | `view` | `(address, uint256)` |
| `def getUserAssetAtIndexAndHasBalance(_user: address, _index: uint256) -> (address, bool)` | `2` | `view` | `(address, bool)` |
| `def getUserLootBoxShare(_user: address, _asset: address) -> uint256` | `2` | `view` | `uint256` |
| `def getVaultDataOnDeposit(_user: address, _asset: address) -> VaultDataOnDeposit` | `2` | `view` | `VaultDataOnDeposit` |
| `def isPaused() -> bool` | `0` | `view` | `bool` |
| `def isSupportedVaultAsset(_asset: address) -> bool` | `1` | `view` | `bool` |
| `def isUserInVaultAsset(_user: address, _asset: address) -> bool` | `2` | `view` | `bool` |
| `def numUserAssets(_user: address) -> uint256` | `1` | `view` | `uint256` |
| `def pause(_shouldPause: bool)` | `1` | `nonpayable` | — |
| `def recoverFunds(_recipient: address, _asset: address)` | `2` | `nonpayable` | — |
| `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])` | `2` | `nonpayable` | — |
| `def transferBalanceWithinVault(_asset: address, _fromUser: address, _toUser: address, _transferAmount: uint256, _a: addys.Addys = empty(addys.Addys)) -> (uint256, bool)` | `4–5` | `nonpayable` | `(uint256, bool)` |
| `def userAssets(_user: address, _index: uint256) -> address` | `2` | `view` | `address` |
| `def withdrawTokensFromVault(_user: address, _asset: address, _amount: uint256, _recipient: address, _a: addys.Addys = empty(addys.Addys)) -> (uint256, bool)` | `4–5` | `nonpayable` | `(uint256, bool)` |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `depositTokensInVault(address _user, address _asset, uint256 _amount)` | `nonpayable` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, addys.Addys _a)` | `nonpayable` | `uint256` |
| `deregisterUserAsset(address _user, address _asset)` | `nonpayable` | `bool` |
| `deregisterVaultAsset(address _asset)` | `nonpayable` | `bool` |
| `doesUserHaveBalance(address _user, address _asset)` | `view` | `bool` |
| `doesVaultHaveAnyFunds()` | `view` | `bool` |
| `getNumUserAssets(address _user)` | `view` | `uint256` |
| `getNumVaultAssets()` | `view` | `uint256` |
| `getTotalAmountForUser(address _user, address _asset)` | `view` | `uint256` |
| `getTotalAmountForVault(address _asset)` | `view` | `uint256` |
| `getUserAssetAndAmountAtIndex(address _user, uint256 _index)` | `view` | `(address, uint256)` |
| `getUserAssetAtIndexAndHasBalance(address _user, uint256 _index)` | `view` | `(address, bool)` |
| `getUserLootBoxShare(address _user, address _asset)` | `view` | `uint256` |
| `getVaultDataOnDeposit(address _user, address _asset)` | `view` | `VaultDataOnDeposit` |
| `isPaused()` | `view` | `bool` |
| `isSupportedVaultAsset(address _asset)` | `view` | `bool` |
| `isUserInVaultAsset(address _user, address _asset)` | `view` | `bool` |
| `numUserAssets(address _user)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, DynArray[address, 20] _assets)` | `nonpayable` | — |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount)` | `nonpayable` | `(uint256, bool)` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, addys.Addys _a)` | `nonpayable` | `(uint256, bool)` |
| `userAssets(address _user, uint256 _index)` | `view` | `address` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient)` | `nonpayable` | `(uint256, bool)` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, addys.Addys _a)` | `nonpayable` | `(uint256, bool)` |

### Structs declared by this source

- `VaultDataOnDeposit(hasPosition: bool, numAssets: uint256, userBalance: uint256, totalBalance: uint256)`

<!-- END GENERATED API REFERENCE: Vault -->
