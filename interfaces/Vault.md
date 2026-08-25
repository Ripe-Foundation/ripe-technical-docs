# Vault interface

`Vault.vyi` defines the common custody/accounting surface used by Teller,
CreditEngine, AuctionHouse, Lootbox, VaultBook, and migration code.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/Vault.vyi)

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
## Exact API reference

> Generated from declarations in `interfaces/Vault.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def depositTokensInVault( _user: address, _asset: address, _amount: uint256, _a: addys.Addys = empty(addys.Addys), ) -> uint256`
- `def deregisterUserAsset(_user: address, _asset: address) -> bool`
- `def deregisterVaultAsset(_asset: address) -> bool`
- `def doesUserHaveBalance(_user: address, _asset: address) -> bool`
- `def doesVaultHaveAnyFunds() -> bool`
- `def getNumUserAssets(_user: address) -> uint256`
- `def getNumVaultAssets() -> uint256`
- `def getTotalAmountForUser(_user: address, _asset: address) -> uint256`
- `def getTotalAmountForVault(_asset: address) -> uint256`
- `def getUserAssetAndAmountAtIndex(_user: address, _index: uint256) -> (address, uint256)`
- `def getUserAssetAtIndexAndHasBalance(_user: address, _index: uint256) -> (address, bool)`
- `def getUserLootBoxShare(_user: address, _asset: address) -> uint256`
- `def getVaultDataOnDeposit(_user: address, _asset: address) -> VaultDataOnDeposit`
- `def isPaused() -> bool`
- `def isSupportedVaultAsset(_asset: address) -> bool`
- `def isUserInVaultAsset(_user: address, _asset: address) -> bool`
- `def numUserAssets(_user: address) -> uint256`
- `def pause(_shouldPause: bool)`
- `def recoverFunds(_recipient: address, _asset: address)`
- `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])`
- `def transferBalanceWithinVault( _asset: address, _fromUser: address, _toUser: address, _transferAmount: uint256, _a: addys.Addys = empty(addys.Addys), ) -> (uint256, bool)`
- `def userAssets(_user: address, _index: uint256) -> address`
- `def withdrawTokensFromVault( _user: address, _asset: address, _amount: uint256, _recipient: address, _a: addys.Addys = empty(addys.Addys), ) -> (uint256, bool)`

### Structs declared by this source

- `VaultDataOnDeposit(hasPosition: bool, numAssets: uint256, userBalance: uint256, totalBalance: uint256)`

<!-- END GENERATED API REFERENCE: Vault -->
