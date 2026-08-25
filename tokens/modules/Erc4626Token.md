# Erc4626Token module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/tokens/modules/Erc4626Token.vy)

## Overview

`Erc4626Token` is the share-accounting module used by Savings GREEN. Its assets are the underlying token balance held directly by the vault contract. It does not deploy assets into a strategy.

The module relies on `Erc20Token` for share balances, allowances, pause/blacklist enforcement, minting, and protected burns.

## Accounting

`totalAssets()` is exactly `underlying.balanceOf(vault)`. Share conversions use the current total share supply and underlying balance:

```text
assets -> shares: assets * totalSupply / totalAssets
shares -> assets: shares * totalAssets / totalSupply
```

The first deposit is one-for-one. Deposit/redeem previews round down; mint/withdraw previews round up. When share supply exists but underlying balance is zero, asset-to-share conversion returns zero, preventing a deposit from receiving shares. Share-to-asset conversion returns zero.

There is no virtual-share offset. Direct underlying transfers to the vault increase the value of existing shares.

## Maximum views

The maximum-operation views reflect safety state:

- `maxDeposit(receiver)` and `maxMint(receiver)` return zero if the share token is paused, the receiver is blacklisted/zero/self, the underlying is blocked, or nonzero shares have zero backing. Otherwise they return `max_value(uint256)`.
- `maxWithdraw(owner)` returns zero under the corresponding pause/blacklist/underlying/zero-backing conditions. Otherwise it returns the owner's current pro-rata asset claim, not the vault's entire asset balance.
- `maxRedeem(owner)` returns zero under those conditions; otherwise it returns the owner's share balance.

“Underlying blocked” means the underlying token reports itself paused or reports this vault as blacklisted. These views assume the underlying implements that Ripe token control surface.

Preview functions are conversion views; they do not substitute for the maximum views and may return a mathematical result while an operation is currently blocked.

## Deposits and minting

`deposit(assets, receiver)` supports `max_value(uint256)` as “the caller's full underlying balance.” `mint(shares, receiver)` computes the required assets with upward rounding.

Both paths:

- reject zero assets or zero resulting shares;
- reject a zero receiver;
- transfer underlying from the caller with default-true ERC-20 semantics;
- mint shares through Erc20Token, which enforces share-token pause and receiver blacklist state; and
- update `lastPricePerShare` after the operation.

The nonreentrant guard covers deposit and mint.

## Withdrawals and redemption

`withdraw(assets, receiver, owner)` computes shares with upward rounding. `redeem(shares, receiver, owner)` supports `max_value(uint256)` as the owner's entire share balance and computes assets with downward rounding.

The shared redemption path rejects zero assets/shares, zero receiver, paused share token, blacklisted owner, and insufficient shares. When caller and owner differ, the caller must not be blacklisted and sufficient allowance is spent. Shares burn before the underlying transfer; a failed transfer reverts the entire transaction.

The underlying token's own pause/blacklist transfer rules provide a second enforcement layer. The maximum views expose that state proactively.

## Price-per-share observations

`pricePerShare()` converts one whole share unit using state at call time.
`lastPricePerShare` is updated only after a successful
deposit/mint/withdraw/redeem. `getLastUnderlying(shares)` uses that stored
observation.

A direct underlying donation changes `pricePerShare` immediately but does not
refresh `lastPricePerShare` until the next successful vault operation.

## Supply/backing safeguards

The shared ERC-20 module prevents:

- ordinary or governance blacklist burning of the entire share supply while the vault still holds underlying; and
- ordinary burns by a blacklisted share holder.

These checks prevent vault assets from becoming stranded without shares.
Savings GREEN additionally requires zero initial share supply at construction.

## Integration requirements

- Consult `max*` immediately before submitting an operation.
- Do not interpret previews as authorization or availability.
- Use owner-specific `maxWithdraw`; it is not total vault liquidity.
- Account for direct donations and the distinction between current and stored
  price per share.
- Verify the underlying exposes the expected pause/blacklist getters.

<!-- BEGIN GENERATED API REFERENCE: Erc4626Token -->
## Exact API reference

> Generated from declarations in `contracts/tokens/modules/Erc4626Token.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def asset() -> address`
- `def convertToAssets(_shares: uint256) -> uint256`
- `def convertToShares(_assets: uint256) -> uint256`
- `def deposit(_assets: uint256, _receiver: address = msg.sender) -> uint256`
- `def getLastUnderlying(_shares: uint256) -> uint256`
- `def maxDeposit(_receiver: address) -> uint256`
- `def maxMint(_receiver: address) -> uint256`
- `def maxRedeem(_owner: address) -> uint256`
- `def maxWithdraw(_owner: address) -> uint256`
- `def mint(_shares: uint256, _receiver: address = msg.sender) -> uint256`
- `def previewDeposit(_assets: uint256) -> uint256`
- `def previewMint(_shares: uint256) -> uint256`
- `def previewRedeem(_shares: uint256) -> uint256`
- `def previewWithdraw(_assets: uint256) -> uint256`
- `def pricePerShare() -> uint256`
- `def redeem(_shares: uint256, _receiver: address = msg.sender, _owner: address = msg.sender) -> uint256`
- `def totalAssets() -> uint256`
- `def withdraw(_assets: uint256, _receiver: address = msg.sender, _owner: address = msg.sender) -> uint256`

### Events declared by this source

- `Deposit(sender: indexed(address), owner: indexed(address), assets: uint256, shares: uint256)`
- `Withdraw(sender: indexed(address), receiver: indexed(address), owner: indexed(address), assets: uint256, shares: uint256)`

<!-- END GENERATED API REFERENCE: Erc4626Token -->
