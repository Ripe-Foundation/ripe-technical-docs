# PriceSourceData module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/priceSources/modules/PriceSourceData.vy)

## Overview

`PriceSourceData` is a shared storage and administration module for enumerable price sources. It provides a 1-based asset registry, a Switchboard-controlled pause flag, and ERC-20 recovery helpers.

It does **not** implement price calculation or enforce a universal “paused means reads revert” policy. Each consuming price source decides where `isPaused` applies. In current sources it commonly gates configuration and snapshot mutations while price reads may remain available.

## Asset registry

The module stores:

```text
assets[index] -> asset
indexOfAsset[asset] -> index
numAssets -> next index / logical count plus sentinel
```

Index zero means “not registered.” The first asset is stored at index 1. Once nonempty, the logical count is `numAssets - 1`.

`_addPricedAsset(asset)` assigns the next index and now explicitly rejects an index above `MAX_ASSETS = 50`. Consuming contracts must separately ensure an asset is nonzero and not already registered before calling it; the module itself does not perform those checks.

`_removePricedAsset(asset)` is a no-op for an empty registry or unknown asset. Otherwise it moves the last logical asset into the removed slot when necessary and updates the reverse index. Enumeration remains contiguous even though raw storage outside the logical range is not an authoritative asset list.

`getPricedAssets()` iterates the current logical range and returns at most 50 addresses.

## Pause state

The constructor accepts an initial Boolean. `pause(shouldPause)`:

- may be called only by an address recognized by the current Switchboard;
- requires the value to change; and
- emits `PriceSourcePauseModified(isPaused)`.

The module does not automatically wrap child functions. Consult the concrete source to learn whether pause blocks feed changes, snapshot writes, reads, recovery, or none of those operations.

## Fund recovery

`recoverFunds(recipient, asset)` and `recoverFundsMany(recipient, assets)` are Switchboard-only. A batch contains at most 20 assets. For each entry, the module:

- rejects a zero recipient or asset;
- requires a nonzero token balance;
- transfers the entire current balance with a default-true ERC-20 return convention; and
- emits `PriceSourceFundsRecovered(asset, recipient, balance)`.

The function does not distinguish “tracked” from “untracked” tokens. It is an administrative full-balance transfer primitive, so the concrete source and governance process must determine whether recovery is safe.

## Integration requirements

- Use `getPricedAssets`, not raw slots beyond the logical range.
- Enforce uniqueness and feed-specific validation before `_addPricedAsset`.
- Do not assume every source has this module; monitoring-only adapters implement inert compatibility surfaces instead.
- Do not infer concrete pause behavior from `PriceSourceData` alone.

<!-- BEGIN GENERATED API REFERENCE: PriceSourceData -->
## Exact source-declared API reference

> Generated from declarations in `contracts/priceSources/modules/PriceSourceData.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__(_shouldPause: bool)`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def getPricedAssets() -> DynArray[address, MAX_ASSETS]` | `0` | `view` | `DynArray[address, MAX_ASSETS]` |
| `def pause(_shouldPause: bool)` | `1` | `nonpayable` | — |
| `def recoverFunds(_recipient: address, _asset: address)` | `2` | `nonpayable` | — |
| `def recoverFundsMany(_recipient: address, _assets: DynArray[address, MAX_RECOVER_ASSETS])` | `2` | `nonpayable` | — |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `getPricedAssets()` | `view` | `DynArray[address, MAX_ASSETS]` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, DynArray[address, MAX_RECOVER_ASSETS] _assets)` | `nonpayable` | — |

### Compiler-generated public getters

| Getter | Mutability | Source return type |
| --- | --- | --- |
| `assets(uint256 key1)` | `view` | `address` |
| `indexOfAsset(address key1)` | `view` | `uint256` |
| `isPaused()` | `view` | `bool` |
| `numAssets()` | `view` | `uint256` |

### Events declared by this source

- `PriceSourcePauseModified(isPaused: bool)`
- `PriceSourceFundsRecovered(asset: indexed(address), recipient: indexed(address), balance: uint256)`

### Constants declared by this source

- `MAX_ASSETS: uint256 = 50`
- `MAX_RECOVER_ASSETS: uint256 = 20`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid recipient or asset`
- `no change`
- `no perms`
- `nothing to recover`
- `recovery failed`
- `too many assets`

<!-- END GENERATED API REFERENCE: PriceSourceData -->
