# PriceSource interface

`PriceSource.vyi` defines the common PriceDesk-facing surface for price-source
implementations, including reads, feed lifecycle operations, snapshots,
timelock inspection, pause, and recovery.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/PriceSource.vyi)

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
## Exact API reference

> Generated from declarations in `interfaces/PriceSource.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def actionTimeLock() -> uint256`
- `def addPriceSnapshot(_asset: address) -> bool`
- `def cancelDisablePriceFeed(_asset: address) -> bool`
- `def cancelNewPendingPriceFeed(_asset: address) -> bool`
- `def cancelPriceFeedUpdate(_asset: address) -> bool`
- `def confirmDisablePriceFeed(_asset: address) -> bool`
- `def confirmNewPriceFeed(_asset: address) -> bool`
- `def confirmPriceFeedUpdate(_asset: address) -> bool`
- `def disablePriceFeed(_asset: address) -> bool`
- `def getActionConfirmationBlock(_actionId: uint256) -> uint256`
- `def getPrice(_asset: address, _staleTime: uint256 = 0, _oracleRegistry: address = empty(address)) -> uint256`
- `def getPriceAndHasFeed(_asset: address, _staleTime: uint256 = 0, _oracleRegistry: address = empty(address)) -> (uint256, bool)`
- `def getPricedAssets() -> DynArray[address, 50]`
- `def hasPendingAction(_actionId: uint256) -> bool`
- `def hasPendingPriceFeedUpdate(_asset: address) -> bool`
- `def hasPriceFeed(_asset: address) -> bool`
- `def isPaused() -> bool`
- `def pause(_shouldPause: bool)`
- `def recoverFunds(_recipient: address, _asset: address)`
- `def recoverFundsMany(_recipient: address, _assets: DynArray[address, 20])`
- `def setActionTimeLock(_numBlocks: uint256) -> bool`
- `def setActionTimeLockAfterSetup(_numBlocks: uint256 = 0) -> bool`

<!-- END GENERATED API REFERENCE: PriceSource -->
