# SavingsGreen

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/tokens/SavingsGreen.vy)

## Overview

Savings GREEN (`sGREEN`) is an ERC-4626 share token whose underlying is the configured GREEN token. Assets remain as the underlying token balance held directly by the sGREEN contract. The contract does not contain an external yield strategy; share value changes when its custody balance changes relative to outstanding shares.

## Constructor

```text
__init__(
  asset,
  ripeHq,
  initialGov,
  minHqTimeLock,
  maxHqTimeLock,
  initialSupply,
  initialSupplyRecipient
)
```

The share name is `Savings Green USD`, symbol is `sGREEN`, and share decimals equal the underlying token's reported decimals.

The constructor requires `initialSupply == 0`. `initialSupplyRecipient` remains
in the signature for shared constructor compatibility. Initial shares must be
created through an asset-backed ERC-4626 deposit, not through an unbacked
constructor mint.

## ERC-4626 accounting

`totalAssets()` is `GREEN.balanceOf(sGREEN)`. The first deposit is one-for-one. Later conversions use the current pro-rata relationship between GREEN balance and sGREEN supply.

Direct GREEN transfers to sGREEN increase the current share value. There is no
virtual offset and no strategy accounting in this contract.

`maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` return zero when the share token or underlying transfer path is blocked, or when shares exist with zero backing. `maxWithdraw(owner)` returns only that owner's current pro-rata GREEN claim.

Deposits/mints transfer GREEN in before minting shares. Withdrawals/redemptions burn shares and transfer GREEN out atomically. Third-party withdrawals consume allowance and reject a blacklisted spender.

## Backing protections

The contract applies several protections against stranded backing:

- sGREEN cannot start with unbacked initial shares;
- a user cannot burn the complete share supply while GREEN remains in the vault;
- governance cannot burn the complete blacklisted share supply while underlying remains; and
- GREEN governance cannot blacklist-burn the GREEN balance held by the sGREEN contract.

When sGREEN supply is nonzero but its GREEN balance is zero, asset-to-share conversion returns zero and the maximum entry/exit views return zero.

## Shared token controls

sGREEN shares inherit Erc20Token transfers, allowances, permits, blacklist, pause, timelocked HQ rotation, and approval revocation behavior. HQ rotation must preserve the identical GREEN/sGREEN/RIPE suite so the GREEN backing guard continues to recognize this vault.

`getCCIPAdmin()` returns RipeHq governance for Chainlink administrator
nomination. The first-party token-specific pool source defines GREEN and RIPE
pools, not an sGREEN pool.

## Integration requirements

- Do not describe sGREEN as deploying a yield strategy.
- Use `pricePerShare` and conversion views for backing at call time, and
  remember that `lastPricePerShare` updates only on vault operations.
- Consult the `max*` views immediately before entry or exit.
- Treat the sGREEN-held GREEN balance as share backing, not recoverable or burnable surplus.

<!-- BEGIN GENERATED API REFERENCE: SavingsGreen -->
## Exact API reference

> Generated from `contracts/tokens/SavingsGreen.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _asset, address _ripeHq, address _initialGov, uint256 _minHqTimeLock, uint256 _maxHqTimeLock, uint256 _initialSupply, address _initialSupplyRecipient)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `burnBlacklistTokens(address _addr, uint256 _amount)` | `1–2` | `_amount` |
| `deposit(uint256 _assets, address _receiver)` | `1–2` | `_receiver` |
| `finishTokenSetup(address _newHq, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `mint(uint256 _shares, address _receiver)` | `1–2` | `_receiver` |
| `redeem(uint256 _shares, address _receiver, address _owner)` | `1–3` | `_receiver`, `_owner` |
| `withdraw(uint256 _assets, address _receiver, address _owner)` | `1–3` | `_receiver`, `_owner` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `DOMAIN_SEPARATOR()` | `view` | `bytes32` |
| `TOKEN_DECIMALS()` | `view` | `uint8` |
| `TOKEN_NAME()` | `view` | `string` |
| `TOKEN_SYMBOL()` | `view` | `string` |
| `VERSION()` | `view` | `string` |
| `allowance(address arg0, address arg1)` | `view` | `uint256` |
| `approve(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `asset()` | `view` | `address` |
| `balanceOf(address arg0)` | `view` | `uint256` |
| `blacklisted(address arg0)` | `view` | `bool` |
| `burn(uint256 _amount)` | `nonpayable` | `bool` |
| `burnBlacklistTokens(address _addr)` | `nonpayable` | `bool` |
| `burnBlacklistTokens(address _addr, uint256 _amount)` | `nonpayable` | `bool` |
| `cancelHqChange()` | `nonpayable` | — |
| `confirmHqChange()` | `nonpayable` | `bool` |
| `convertToAssets(uint256 _shares)` | `view` | `uint256` |
| `convertToShares(uint256 _assets)` | `view` | `uint256` |
| `decimals()` | `view` | `uint8` |
| `decreaseAllowance(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `deposit(uint256 _assets)` | `nonpayable` | `uint256` |
| `deposit(uint256 _assets, address _receiver)` | `nonpayable` | `uint256` |
| `finishTokenSetup(address _newHq)` | `nonpayable` | `bool` |
| `finishTokenSetup(address _newHq, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getCCIPAdmin()` | `view` | `address` |
| `getLastUnderlying(uint256 _shares)` | `view` | `uint256` |
| `hasPendingHqChange()` | `view` | `bool` |
| `hqChangeTimeLock()` | `view` | `uint256` |
| `increaseAllowance(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `initiateHqChange(address _newHq)` | `nonpayable` | — |
| `isPaused()` | `view` | `bool` |
| `isValidHqChangeTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidNewRipeHq(address _newHq)` | `view` | `bool` |
| `lastPricePerShare()` | `view` | `uint256` |
| `maxDeposit(address _receiver)` | `view` | `uint256` |
| `maxHqTimeLock()` | `view` | `uint256` |
| `maxMint(address _receiver)` | `view` | `uint256` |
| `maxRedeem(address _owner)` | `view` | `uint256` |
| `maxWithdraw(address _owner)` | `view` | `uint256` |
| `minHqTimeLock()` | `view` | `uint256` |
| `mint(uint256 _shares)` | `nonpayable` | `uint256` |
| `mint(uint256 _shares, address _receiver)` | `nonpayable` | `uint256` |
| `name()` | `view` | `string` |
| `nonces(address arg0)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingHq()` | `view` | `(address,uint256,uint256)` |
| `permit(address _owner, address _spender, uint256 _value, uint256 _deadline, bytes _signature)` | `nonpayable` | `bool` |
| `previewDeposit(uint256 _assets)` | `view` | `uint256` |
| `previewMint(uint256 _shares)` | `view` | `uint256` |
| `previewRedeem(uint256 _shares)` | `view` | `uint256` |
| `previewWithdraw(uint256 _assets)` | `view` | `uint256` |
| `pricePerShare()` | `view` | `uint256` |
| `redeem(uint256 _shares)` | `nonpayable` | `uint256` |
| `redeem(uint256 _shares, address _receiver)` | `nonpayable` | `uint256` |
| `redeem(uint256 _shares, address _receiver, address _owner)` | `nonpayable` | `uint256` |
| `ripeHq()` | `view` | `address` |
| `setBlacklist(address _addr, bool _shouldBlacklist)` | `nonpayable` | `bool` |
| `setHqChangeTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `symbol()` | `view` | `string` |
| `totalAssets()` | `view` | `uint256` |
| `totalSupply()` | `view` | `uint256` |
| `transfer(address _recipient, uint256 _amount)` | `nonpayable` | `bool` |
| `transferFrom(address _sender, address _recipient, uint256 _amount)` | `nonpayable` | `bool` |
| `withdraw(uint256 _assets)` | `nonpayable` | `uint256` |
| `withdraw(uint256 _assets, address _receiver)` | `nonpayable` | `uint256` |
| `withdraw(uint256 _assets, address _receiver, address _owner)` | `nonpayable` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `Approval` | `address owner indexed, address spender indexed, uint256 amount` |
| `BlacklistModified` | `address addr indexed, bool isBlacklisted` |
| `Deposit` | `address sender indexed, address owner indexed, uint256 assets, uint256 shares` |
| `HqChangeCancelled` | `address cancelledHq indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqChangeConfirmed` | `address prevHq indexed, address newHq indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqChangeInitiated` | `address prevHq indexed, address newHq indexed, uint256 confirmBlock` |
| `HqChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `InitialRipeHqSet` | `address hq indexed, uint256 timeLock` |
| `TokenPauseModified` | `bool isPaused` |
| `Transfer` | `address sender indexed, address recipient indexed, uint256 amount` |
| `Withdraw` | `address sender indexed, address receiver indexed, address owner indexed, uint256 assets, uint256 shares` |

<!-- END GENERATED API REFERENCE: SavingsGreen -->
