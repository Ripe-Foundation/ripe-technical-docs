# PriceSource interface

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/interfaces/PriceSource.vyi)

`PriceSource.vyi` defines the common PriceDesk-facing surface for price-source
implementations, including reads, feed lifecycle operations, snapshots,
timelock inspection, pause, and recovery.

## Price reads

The common read surface is:

- `getPrice(asset, staleTime, oracleRegistry)`;
- `getPriceAndHasFeed(asset, staleTime, oracleRegistry)`;
- `hasPriceFeed(asset)`;
- `hasPendingPriceFeedUpdate(asset)`; and
- `getPricedAssets()`.

The interface does not guarantee that every implementation actively prices an
asset. Monitoring-only implementations may report no feed and return zero. A
consumer that needs feed validity should use the boolean-returning path or
PriceDesk's canonical routing rather than treating any contract that implements
this interface as an active oracle.

`staleTime == 0` has implementation-specific fallback semantics. It must not be
assumed to disable staleness checks; current configured sources can inherit the
MissionControl stale time.

## Feed lifecycle

The interface includes confirmation/cancellation for new and updated feeds,
disable proposal/confirmation/cancellation, `addPriceSnapshot`, and inherited
TimeLock inspection/configuration. Individual implementations may expose
additional proposal methods and feed-specific validation.

Feed mutations remain subject to the implementation's governance, pause state,
and execution-time validation. Registry or caller-identity requirements are
route-specific: removing a source from PriceDesk does not universally prevent
that source's governor from updating its internal feeds. The interface itself
supplies no authorization.

## Operational controls

Price sources expose standard Department pause and recovery methods. Pause
semantics and the safety of recovering held tokens depend on the implementation.

<!-- BEGIN GENERATED API REFERENCE: PriceSource -->
## Exact source-declared API reference

> Generated from declarations in `interfaces/PriceSource.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def actionTimeLock() -> uint256` | `0` | `view` | `uint256` |
| `def addPriceSnapshot(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def cancelDisablePriceFeed(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def cancelNewPendingPriceFeed(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def cancelPriceFeedUpdate(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def confirmDisablePriceFeed(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def confirmNewPriceFeed(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def confirmPriceFeedUpdate(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def disablePriceFeed(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def getActionConfirmationBlock(_actionId: uint256) -> uint256` | `1` | `view` | `uint256` |
| `def getPrice(_asset: address, _staleTime: uint256 = 0, _oracleRegistry: address = empty(address)) -> uint256` | `1–3` | `view` | `uint256` |
| `def getPriceAndHasFeed(_asset: address, _staleTime: uint256 = 0, _oracleRegistry: address = empty(address)) -> (uint256, bool)` | `1–3` | `view` | `(uint256, bool)` |
| `def getPricedAssets() -> DynArray[address, 50]` | `0` | `view` | `DynArray[address, 50]` |
| `def hasPendingAction(_actionId: uint256) -> bool` | `1` | `view` | `bool` |
| `def hasPendingPriceFeedUpdate(_asset: address) -> bool` | `1` | `view` | `bool` |
| `def hasPriceFeed(_asset: address) -> bool` | `1` | `view` | `bool` |
| `def isPaused() -> bool` | `0` | `view` | `bool` |
| `def pause(_shouldPause: bool)` | `1` | `nonpayable` | — |
| `def recoverFunds(_recipient: address, _asset: address)` | `2` | `nonpayable` | — |
| `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])` | `2` | `nonpayable` | — |
| `def setActionTimeLock(_numBlocks: uint256) -> bool` | `1` | `nonpayable` | `bool` |
| `def setActionTimeLockAfterSetup(_numBlocks: uint256 = 0) -> bool` | `0–1` | `nonpayable` | `bool` |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `actionTimeLock()` | `view` | `uint256` |
| `addPriceSnapshot(address _asset)` | `nonpayable` | `bool` |
| `cancelDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelNewPendingPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `cancelPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `confirmDisablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmNewPriceFeed(address _asset)` | `nonpayable` | `bool` |
| `confirmPriceFeedUpdate(address _asset)` | `nonpayable` | `bool` |
| `disablePriceFeed(address _asset)` | `nonpayable` | `bool` |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` |
| `getPrice(address _asset)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime)` | `view` | `uint256` |
| `getPrice(address _asset, uint256 _staleTime, address _oracleRegistry)` | `view` | `uint256` |
| `getPriceAndHasFeed(address _asset)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime)` | `view` | `(uint256, bool)` |
| `getPriceAndHasFeed(address _asset, uint256 _staleTime, address _oracleRegistry)` | `view` | `(uint256, bool)` |
| `getPricedAssets()` | `view` | `DynArray[address, 50]` |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` |
| `hasPendingPriceFeedUpdate(address _asset)` | `view` | `bool` |
| `hasPriceFeed(address _asset)` | `view` | `bool` |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, DynArray[address, 20] _assets)` | `nonpayable` | — |
| `setActionTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` |
| `setActionTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` |

<!-- END GENERATED API REFERENCE: PriceSource -->
