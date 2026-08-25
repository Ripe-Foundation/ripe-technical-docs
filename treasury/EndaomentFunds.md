# EndaomentFunds

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/EndaomentFunds.vy)

## Purpose

`EndaomentFunds` is the minimal custody contract for protocol-owned ERC-20 tokens and native currency. It deliberately contains no strategy, pricing, swap, yield, governance, pause, or independent recovery logic. [Endaoment](./Endaoment.md) is the authorized executor.

The payable default function accepts native currency. `hasBalance(asset)` reports whether the contract currently holds the selected ERC-20, or native currency when the zero address is supplied.

## Transfers

Only the address currently registered as Endaoment through Addys may call `transfer`. The destination is that same current Endaoment address; the caller cannot choose another recipient.

For both ERC-20 and native currency, the actual transfer is:

```text
min(requested amount, current balance)
```

A zero nominal amount reverts. A successful ERC-20 transfer emits
`EndaomentFundsMoved` and returns the clipped nominal amount passed to
`transfer`, not a measured recipient balance delta. A fee-on-transfer token may
therefore deliver less than the return and event amount. Native transfers use
and return the exact clipped amount.

This contract exposes neither an `API_VERSION` constant nor the Department
pause and recovery surface.

<!-- BEGIN GENERATED API REFERENCE: EndaomentFunds -->
## Exact API reference

> Generated from `contracts/core/EndaomentFunds.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Fallback and receive

- `fallback()` — `payable`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `hasBalance(address _asset)` | `0–1` | `_asset = empty(address)` |
| `transfer(address _asset, uint256 _amount)` | `0–2` | `_asset = empty(address)`, `_amount = max_value(uint256)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getRipeHq()` | `view` | `address` | — |
| `hasBalance()` | `view` | `bool` | `bool` |
| `hasBalance(address _asset)` | `view` | `bool` | `bool` |
| `transfer()` | `nonpayable` | `uint256` | `uint256` |
| `transfer(address _asset)` | `nonpayable` | `uint256` | `uint256` |
| `transfer(address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `EndaomentFundsMoved` | `address token indexed, address to indexed, uint256 amount` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `insufficient balance`
- `not authorized`
- `transfer failed`

<!-- END GENERATED API REFERENCE: EndaomentFunds -->
