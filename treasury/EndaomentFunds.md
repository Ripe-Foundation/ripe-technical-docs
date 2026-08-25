# EndaomentFunds

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/EndaomentFunds.vy)

## Purpose

`EndaomentFunds` is the minimal custody contract for protocol-owned ERC-20 tokens and native currency. It deliberately contains no strategy, pricing, swap, yield, governance, pause, or independent recovery logic. [Endaoment](./Endaoment.md) is the authorized executor.

The payable default function accepts native currency. `hasBalance(asset)` reports whether the contract currently holds the selected ERC-20, or native currency when the zero address is supplied.

## Transfers

Only the address currently registered as Endaoment through Addys may call `transfer`. The destination is that same current Endaoment address; the caller cannot choose another recipient.

For both ERC-20 and native currency, the actual transfer is:

```text
min(requested amount, current balance)
```

A zero actual amount reverts. A successful transfer emits `EndaomentFundsMoved` and returns the measured amount sent.

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
| `hasBalance(address _asset)` | `0–1` | `_asset` |
| `transfer(address _asset, uint256 _amount)` | `0–2` | `_asset`, `_amount` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `hasBalance()` | `view` | `bool` |
| `hasBalance(address _asset)` | `view` | `bool` |
| `transfer()` | `nonpayable` | `uint256` |
| `transfer(address _asset)` | `nonpayable` | `uint256` |
| `transfer(address _asset, uint256 _amount)` | `nonpayable` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `EndaomentFundsMoved` | `address token indexed, address to indexed, uint256 amount` |

<!-- END GENERATED API REFERENCE: EndaomentFunds -->
