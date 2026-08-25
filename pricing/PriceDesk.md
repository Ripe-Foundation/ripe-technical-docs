# PriceDesk

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/registries/PriceDesk.vy)

## Overview

PriceDesk is the protocol's price-source registry and aggregation boundary. It resolves price sources in MissionControl priority order, falls back through the remaining registered sources, converts between token amounts and 18-decimal USD values, and coordinates price snapshots.

PriceDesk is also a fault-containment boundary. Calls into a registered source are isolated with bounded gas and strict ABI validation so a reverting, out-of-gas, or malformed source cannot automatically break all later sources.

## Constructor and inherited controls

```text
__init__(ripeHq, tempGov, ethAddr, minRegistryTimeLock, maxRegistryTimeLock)
```

`ethAddr` is the chain's ETH sentinel and must be nonzero. PriceDesk initializes LocalGov, the timelocked AddressRegistry, Addys, and a non-minting Department configuration. Registry add, update, and disable operations are governance-controlled and unavailable while PriceDesk is paused.

PriceDesk does not itself choose a global freshness policy. It obtains `staleTime` and `priorityPriceSourceIds` from MissionControl's current price configuration.

## Price aggregation

### Source order

For each read, PriceDesk:

1. reads the current MissionControl price configuration;
2. tries each configured priority source ID in order;
3. if none returns a usable price, tries every other active registry ID in numeric order; and
4. returns the first nonzero usable price.

Duplicate priority IDs are not queried again during fallback.

### Isolated source calls

The aggregate read calls each candidate's canonical function:

```text
getPriceAndHasFeed(asset, globalStaleTime, priceDesk)
```

The call is static, does not bubble a source revert, and is limited to 250,000 gas. The response must be exactly two ABI words. PriceDesk rejects malformed Boolean values and the inconsistent combination `price != 0` with `hasFeed == false`.

Source status is interpreted as:

| Status | Meaning |
| --- | --- |
| `0` | call succeeded and source reports no feed |
| `1` | call succeeded and source reports a feed; price may still be zero because it is stale or otherwise unusable |
| `2` | call failed or returned malformed data |

An unhealthy source does not prevent a later healthy source from supplying the price. If every candidate returns zero and any source either reports feed coverage or fails/malforms, a strict read reverts with `has price config, no price`. This fail-closed rule prevents a failed source from being misclassified as proof that no configured feed exists. A non-strict read returns zero.

### Caller stale-time parameter

The public selector is:

```text
getPrice(asset, shouldRaise = false, staleTime = 0)
```

For a real asset, the caller-side `staleTime` argument must be zero. A nonzero
value returns zero in non-strict mode and reverts with
`caller stale time unsupported` in strict mode. Source freshness is governed by
MissionControl plus each source's feed configuration.

`qualifyCallerPriceSource(asset, staleTime = 0)` is an admission helper used by
a candidate source itself. It tests that caller directly under the 250,000-gas
stipend, avoiding aggregate fallback that could mask an unexecutable source. A
nonzero caller stale time returns `(0, 2)`.

## Global and feed-specific freshness

PriceDesk forwards MissionControl's global stale time only through the canonical three-argument source call and identifies itself as the forwarding registry. Supported oracle sources accept a nonzero global value only from the currently registered PriceDesk.

Within those sources:

- a feed-specific nonzero stale time is an **absolute override**;
- a feed-specific zero inherits the MissionControl global value; and
- the implementation does not take the minimum of the two.

Feed configuration and protocol-wide stale-time governance remain separate
controls. Oracle-source code constrains local overrides to five minutes through
seven days and rejects an effective or global nonzero value above seven days.

## Token scale cache

PriceDesk uses a stored `tokenScale[asset]` instead of calling `decimals()`
during each valuation:

- `0` means unset;
- `1` is a valid scale for a zero-decimal token; and
- `10 ** decimals` is stored for all other supported tokens.

`syncTokenScale(asset)` rejects the zero address and the ETH sentinel. Governance and Switchboard callers may initialize or refresh a scale. Any other caller may initialize it only when PriceDesk can find a feed for the asset and the scale is still unset. Permissionless callers cannot overwrite an existing value.

The token must return decimals no greater than 77. Successful synchronization emits:

```text
TokenScaleSet(asset, decimals, scale)
```

For non-ETH assets, a missing scale returns zero in non-strict conversion calls and reverts with `missing token scale` in strict calls. ETH always uses `1e18`.

Feed registration and token-scale synchronization are independent. A usable
valuation route requires both.

## Amount conversion

### `getUsdValue(asset, amount, shouldRaise = false)`

Returns:

```text
price * amount / tokenScale
```

Zero amount, zero asset, missing scale, or unavailable price returns zero in non-strict mode. If a nonzero amount and price produce a positive numerator smaller than the scale, PriceDesk returns **1 USD wei** instead of rounding to zero. This floor is intentional: downstream Stability Pool accounting must not mistake positive dust for no value.

### `getAssetAmount(asset, usdValue, shouldRaise = false)`

Returns:

```text
usdValue * tokenScale / price
```

The result rounds down. Zero input or unavailable scale/price returns zero in non-strict mode.

### ETH helpers

`getEthUsdValue` and `getEthAmount` use the immutable ETH sentinel and an 18-decimal ETH scale. They share the same strict/non-strict aggregate-price behavior.

## Feed discovery and snapshots

`hasPriceFeed(asset)` probes every registered source with 75,000 gas. Only an exact, canonical Boolean response counts. A failed or malformed source is ignored for this discovery view.

`addPriceSnapshot(asset)` may be called by a valid Ripe address or the Underscore Appraiser resolved from MissionControl's current Underscore registry. It first isolates `hasPriceFeed`, then calls `addPriceSnapshot` on qualifying sources with 150,000 gas. Reverts and malformed responses are contained per source; the function returns true if at least one source reports a successful snapshot.

Snapshot permission does not imply permission to change feed configuration.

## Registry lifecycle

Price-source addresses use the inherited timelocked registry lifecycle:

- start, confirm, or cancel a new address;
- start, confirm, or cancel an address replacement; and
- start, confirm, or cancel an address disable.

Only an unpaused governance caller can initiate or execute these operations. Consumers should resolve active registry addresses and MissionControl priority IDs at runtime; numeric membership is configuration, not a permanent protocol guarantee.

## Security and integration requirements

- Use strict reads for safety-critical protocol decisions and handle the documented revert paths.
- Treat zero from non-strict reads as unavailable, never as evidence of a zero-dollar asset.
- Synchronize token scale during onboarding and after any intentional token implementation/decimal change.
- A successful `hasPriceFeed` probe does not guarantee a current nonzero price.
- A failed source may make coverage uncertain; strict aggregation therefore fails closed only if no later healthy source succeeds.
- Source gas stipends are part of the compatibility boundary. A source that succeeds with unlimited gas can still be unusable through PriceDesk.

<!-- BEGIN GENERATED API REFERENCE: PriceDesk -->
## Exact API reference

> Generated from `contracts/registries/PriceDesk.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, address _ethAddr, uint256 _minRegistryTimeLock, uint256 _maxRegistryTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock` |
| `getAssetAmount(address _asset, uint256 _usdValue, bool _shouldRaise)` | `2–3` | `_shouldRaise` |
| `getEthAmount(uint256 _usdValue, bool _shouldRaise)` | `1–2` | `_shouldRaise` |
| `getEthUsdValue(uint256 _amount, bool _shouldRaise)` | `1–2` | `_shouldRaise` |
| `getPrice(address _asset, bool _shouldRaise, uint256 _staleTime)` | `1–3` | `_shouldRaise`, `_staleTime` |
| `getUsdValue(address _asset, uint256 _amount, bool _shouldRaise)` | `2–3` | `_shouldRaise` |
| `qualifyCallerPriceSource(address _asset, uint256 _staleTime)` | `1–2` | `_staleTime` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `0–1` | `_numBlocks` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `ETH()` | `view` | `address` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` |
| `addrInfo(uint256 arg0)` | `view` | `(address,uint256,uint256,string)` |
| `addrToRegId(address arg0)` | `view` | `uint256` |
| `canGovern(address _addr)` | `view` | `bool` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `cancelAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — |
| `cancelNewAddressToRegistry(address _addr)` | `nonpayable` | `bool` |
| `confirmAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — |
| `confirmNewAddressToRegistry(address _addr)` | `nonpayable` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getAddr(uint256 _regId)` | `view` | `address` |
| `getAddrDescription(uint256 _regId)` | `view` | `string` |
| `getAddrInfo(uint256 _regId)` | `view` | `(address,uint256,uint256,string)` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getAssetAmount(address _asset, uint256 _usdValue)` | `view` | `uint256` |
| `getAssetAmount(address _asset, uint256 _usdValue, bool _shouldRaise)` | `view` | `uint256` |
| `getEthAmount(uint256 _usdValue)` | `view` | `uint256` |
| `getEthAmount(uint256 _usdValue, bool _shouldRaise)` | `view` | `uint256` |
| `getEthUsdValue(uint256 _amount)` | `view` | `uint256` |
| `getEthUsdValue(uint256 _amount, bool _shouldRaise)` | `view` | `uint256` |
| `getGovernors()` | `view` | `address[]` |
| `getLastAddr()` | `view` | `address` |
| `getLastRegId()` | `view` | `uint256` |
| `getNumAddrs()` | `view` | `uint256` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, bool _shouldRaise)` | `view` | `uint256` |
| `getPrice(address _asset, bool _shouldRaise, uint256 _staleTime)` | `view` | `uint256` |
| `getRegId(address _addr)` | `view` | `uint256` |
| `getRegistryDescription()` | `view` | `string` |
| `getRipeHq()` | `view` | `address` |
| `getRipeHqFromGov()` | `view` | `address` |
| `getUsdValue(address _asset, uint256 _amount)` | `view` | `uint256` |
| `getUsdValue(address _asset, uint256 _amount, bool _shouldRaise)` | `view` | `uint256` |
| `govChangeTimeLock()` | `view` | `uint256` |
| `governance()` | `view` | `address` |
| `hasPendingGovChange()` | `view` | `bool` |
| `hasPriceFeed(address _asset)` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `isValidAddr(address _addr)` | `view` | `bool` |
| `isValidAddressDisable(uint256 _regId)` | `view` | `bool` |
| `isValidAddressUpdate(uint256 _regId, address _newAddr)` | `view` | `bool` |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidNewAddress(address _addr)` | `view` | `bool` |
| `isValidRegId(uint256 _regId)` | `view` | `bool` |
| `isValidRegistryTimeLock(uint256 _numBlocks)` | `view` | `bool` |
| `maxGovChangeTimeLock()` | `view` | `uint256` |
| `maxRegistryTimeLock()` | `view` | `uint256` |
| `minGovChangeTimeLock()` | `view` | `uint256` |
| `minRegistryTimeLock()` | `view` | `uint256` |
| `numAddrs()` | `view` | `uint256` |
| `numGovChanges()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingAddrDisable(uint256 arg0)` | `view` | `(uint256,uint256)` |
| `pendingAddrUpdate(uint256 arg0)` | `view` | `(address,uint256,uint256)` |
| `pendingGov()` | `view` | `(address,uint256,uint256)` |
| `pendingNewAddr(address arg0)` | `view` | `(string,uint256,uint256)` |
| `qualifyCallerPriceSource(address _asset)` | `view` | `(uint256, uint256)` |
| `qualifyCallerPriceSource(address _asset, uint256 _staleTime)` | `view` | `(uint256, uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `registryChangeTimeLock()` | `view` | `uint256` |
| `relinquishGov()` | `nonpayable` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setRegistryTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `startAddNewAddressToRegistry(address _addr, string _description)` | `nonpayable` | `bool` |
| `startAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` |
| `startAddressUpdateToRegistry(uint256 _regId, address _newAddr)` | `nonpayable` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — |
| `syncTokenScale(address _asset)` | `nonpayable` | — |
| `tokenScale(address arg0)` | `view` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `AddressDisableCancelled` | `uint256 regId, string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressDisableConfirmed` | `uint256 regId, string description, address addr indexed, uint256 version, string registry` |
| `AddressDisablePending` | `uint256 regId, string description, address addr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `AddressUpdateCancelled` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressUpdateConfirmed` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, string registry` |
| `AddressUpdatePending` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewAddressCancelled` | `string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `NewAddressConfirmed` | `address addr indexed, uint256 regId, string description, string registry` |
| `NewAddressPending` | `address addr indexed, string description, uint256 confirmBlock, string registry` |
| `RegistryTimeLockModified` | `uint256 newTimeLock, uint256 prevTimeLock, string registry` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |
| `TokenScaleSet` | `address asset indexed, uint256 decimals indexed, uint256 scale indexed` |

### Structs declared by this source

- `PriceConfig(staleTime: uint256, priorityPriceSourceIds: DynArray[uint256, MAX_PRIORITY_PRICE_SOURCES])`

<!-- END GENERATED API REFERENCE: PriceDesk -->
