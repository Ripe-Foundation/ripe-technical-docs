# BurnMintTokenPool 1.5.1 inherited API

This page documents the composed Chainlink surface inherited by both
[`RipeCcipBurnMintTokenPools`](RipeCcipBurnMintTokenPools.md) and
[`RipeTokenPool`](RipeTokenPool.md). It is pinned to the vendored
[`BurnMintTokenPool`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/pools/BurnMintTokenPool.sol),
[`BurnMintTokenPoolAbstract`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/pools/BurnMintTokenPoolAbstract.sol),
[`TokenPool`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/pools/TokenPool.sol),
[`Pool`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/libraries/Pool.sol),
[`IPool`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/interfaces/IPool.sol),
[`RateLimiter`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/ccip/libraries/RateLimiter.sol),
[`Ownable2StepMsgSender`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/shared/access/Ownable2StepMsgSender.sol), and
[`Ownable2Step`](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/v0.8/shared/access/Ownable2Step.sol)
sources. The exact inventory below is generated from a separately compiled,
hash-pinned ABI. Validation derives the recursive import closure, checks the
compiler configuration and every source Git blob, and canonical-compares a
fresh CI build with the reviewed artifact.

## Operational model

The pool burns locally on an authorized CCIP on-ramp and mints locally on an
authorized off-ramp. Router checks, RMN curse checks, allowlisting, supported
chain and remote-pool validation, decimal conversion, and per-chain inbound and
outbound rate limits are enforced by the inherited implementation. The owner
manages router, remote-chain, remote-pool, allowlist, and rate-limit-admin state;
the rate-limit admin or owner may update limiter configurations. Ownership uses
a two-step propose/accept transition.

### Remote-chain and pool changes

One remote chain can accept messages from multiple remote pools. When upgrading
a pool, add the replacement alongside the old pool, leave both accepted while
messages from the old lane drain, and remove the old pool only after no messages
from it remain in flight. Removing a pool immediately causes outstanding
messages that name it as `sourcePoolAddress` to be rejected. Removing a chain
through `applyChainUpdates` deletes the entire chain configuration, including
its remote-pool set and both rate-limit buckets, so every lane for that chain
must be drained before removal to avoid a loss-of-funds condition.

### Allowlist mode

Allowlist mode is selected immutably by the constructor. An empty initial list
creates a permissionless pool, and every later `applyAllowListUpdates` call
reverts with `AllowListNotEnabled`; the owner cannot enable the mode later. A
nonempty initial list permanently enables allowlisting. Removing every member
then leaves an enabled but empty list and blocks every outbound sender. The
outbound check applies to `lockOrBurnIn.originalSender`, not the on-ramp caller,
and zero-address additions are skipped. The mode itself cannot be enabled or
disabled after deployment.

### Decimal conversion and amount domains

Construction compares `localTokenDecimals` with `token.decimals()` when that
optional call succeeds. If the method is missing or reverts, validation is
skipped and the supplied value is trusted. Each outbound message encodes the
local decimals in 32 bytes. On inbound execution, empty `sourcePoolData` assumes
the local decimals for backward compatibility; nonempty data must be exactly 32
bytes, decode as a `uint256`, and fit in `uint8`.

Inbound conversion scales the remote amount into local base units. Reducing
precision divides and rounds down after the source-side amount has already been
burned, so an unrepresentable remainder is destroyed as dust. Increasing
precision multiplies and reverts if the decimal difference or result would
overflow. `releaseOrMint` returns `destinationAmount` and emits `Minted.amount`
using the scaled local amount. Outbound limiting consumes the source/local
`lockOrBurnIn.amount`; inbound limiting consumes the unconverted remote
`releaseOrMintIn.amount` before local decimal conversion.

### Rate limiting

An enabled token-bucket configuration requires `0 < rate < capacity`. A disabled
configuration requires both rate and capacity to be zero. New remote-chain
buckets start full at their configured capacities. Reconfiguration first refills
the existing bucket using its old capacity and rate through the current
timestamp, then clamps its remaining tokens to the new capacity; it does not
refill the bucket to the new capacity. Governance and rate-limit automation must
therefore preserve and account for existing bucket depletion.

The concrete Ripe contracts add only their `canMintGreen` and `canMintRipe`
views and constructor choice. Those deltas are documented on their component
pages.

## Constructor

`constructor(address token, uint8 localTokenDecimals, address[] allowlist,
address rmnProxy, address router)` binds the local token, decimals, optional
sender allowlist, RMN proxy, and router. The configurable Ripe variant appends
two capability booleans; the token-specific variants compile those capability
answers into separate classes.

<!-- BEGIN GENERATED API REFERENCE: BurnMintTokenPool151 -->
## Exact composed ABI reference

> Generated from the hash-pinned `BurnMintTokenPool` ABI in `reference/abis/BurnMintTokenPool151.json`, compiled with Solidity `0.8.26+commit.8a97fa7a`. The baseline records and verifies every compiler-input Git blob used by this inherited surface.

### Constructor

| Inputs | Mutability |
| --- | --- |
| `address token, uint8 localTokenDecimals, address[] allowlist, address rmnProxy, address router` | `nonpayable` |

### Functions

| Function | Inputs | Mutability | Returns |
| --- | --- | --- | --- |
| `acceptOwnership` | — | `nonpayable` | — |
| `addRemotePool` | `uint64 remoteChainSelector, bytes remotePoolAddress` | `nonpayable` | — |
| `applyAllowListUpdates` | `address[] removes, address[] adds` | `nonpayable` | — |
| `applyChainUpdates` | `uint64[] remoteChainSelectorsToRemove, (uint64 remoteChainSelector, bytes[] remotePoolAddresses, bytes remoteTokenAddress, (bool isEnabled, uint128 capacity, uint128 rate) outboundRateLimiterConfig, (bool isEnabled, uint128 capacity, uint128 rate) inboundRateLimiterConfig)[] chainsToAdd` | `nonpayable` | — |
| `getAllowList` | — | `view` | `address[]` |
| `getAllowListEnabled` | — | `view` | `bool` |
| `getCurrentInboundRateLimiterState` | `uint64 remoteChainSelector` | `view` | `(uint128 tokens, uint32 lastUpdated, bool isEnabled, uint128 capacity, uint128 rate)` |
| `getCurrentOutboundRateLimiterState` | `uint64 remoteChainSelector` | `view` | `(uint128 tokens, uint32 lastUpdated, bool isEnabled, uint128 capacity, uint128 rate)` |
| `getRateLimitAdmin` | — | `view` | `address` |
| `getRemotePools` | `uint64 remoteChainSelector` | `view` | `bytes[]` |
| `getRemoteToken` | `uint64 remoteChainSelector` | `view` | `bytes` |
| `getRmnProxy` | — | `view` | `address rmnProxy` |
| `getRouter` | — | `view` | `address router` |
| `getSupportedChains` | — | `view` | `uint64[]` |
| `getToken` | — | `view` | `address token` |
| `getTokenDecimals` | — | `view` | `uint8 decimals` |
| `isRemotePool` | `uint64 remoteChainSelector, bytes remotePoolAddress` | `view` | `bool` |
| `isSupportedChain` | `uint64 remoteChainSelector` | `view` | `bool` |
| `isSupportedToken` | `address token` | `view` | `bool` |
| `lockOrBurn` | `(bytes receiver, uint64 remoteChainSelector, address originalSender, uint256 amount, address localToken) lockOrBurnIn` | `nonpayable` | `(bytes destTokenAddress, bytes destPoolData)` |
| `owner` | — | `view` | `address` |
| `releaseOrMint` | `(bytes originalSender, uint64 remoteChainSelector, address receiver, uint256 amount, address localToken, bytes sourcePoolAddress, bytes sourcePoolData, bytes offchainTokenData) releaseOrMintIn` | `nonpayable` | `(uint256 destinationAmount)` |
| `removeRemotePool` | `uint64 remoteChainSelector, bytes remotePoolAddress` | `nonpayable` | — |
| `setChainRateLimiterConfig` | `uint64 remoteChainSelector, (bool isEnabled, uint128 capacity, uint128 rate) outboundConfig, (bool isEnabled, uint128 capacity, uint128 rate) inboundConfig` | `nonpayable` | — |
| `setChainRateLimiterConfigs` | `uint64[] remoteChainSelectors, (bool isEnabled, uint128 capacity, uint128 rate)[] outboundConfigs, (bool isEnabled, uint128 capacity, uint128 rate)[] inboundConfigs` | `nonpayable` | — |
| `setRateLimitAdmin` | `address rateLimitAdmin` | `nonpayable` | — |
| `setRouter` | `address newRouter` | `nonpayable` | — |
| `supportsInterface` | `bytes4 interfaceId` | `pure` | `bool` |
| `transferOwnership` | `address to` | `nonpayable` | — |
| `typeAndVersion` | — | `view` | `string` |

### Events

| Event | Fields |
| --- | --- |
| `AllowListAdd` | `address sender` |
| `AllowListRemove` | `address sender` |
| `Burned` | `address sender indexed, uint256 amount` |
| `ChainAdded` | `uint64 remoteChainSelector, bytes remoteToken, (bool isEnabled, uint128 capacity, uint128 rate) outboundRateLimiterConfig, (bool isEnabled, uint128 capacity, uint128 rate) inboundRateLimiterConfig` |
| `ChainConfigured` | `uint64 remoteChainSelector, (bool isEnabled, uint128 capacity, uint128 rate) outboundRateLimiterConfig, (bool isEnabled, uint128 capacity, uint128 rate) inboundRateLimiterConfig` |
| `ChainRemoved` | `uint64 remoteChainSelector` |
| `ConfigChanged` | `(bool isEnabled, uint128 capacity, uint128 rate) config` |
| `Locked` | `address sender indexed, uint256 amount` |
| `Minted` | `address sender indexed, address recipient indexed, uint256 amount` |
| `OwnershipTransferRequested` | `address from indexed, address to indexed` |
| `OwnershipTransferred` | `address from indexed, address to indexed` |
| `RateLimitAdminSet` | `address rateLimitAdmin` |
| `Released` | `address sender indexed, address recipient indexed, uint256 amount` |
| `RemotePoolAdded` | `uint64 remoteChainSelector indexed, bytes remotePoolAddress` |
| `RemotePoolRemoved` | `uint64 remoteChainSelector indexed, bytes remotePoolAddress` |
| `RouterUpdated` | `address oldRouter, address newRouter` |
| `TokensConsumed` | `uint256 tokens` |

### Custom errors

| Error | Inputs |
| --- | --- |
| `AggregateValueMaxCapacityExceeded` | `uint256 capacity, uint256 requested` |
| `AggregateValueRateLimitReached` | `uint256 minWaitInSeconds, uint256 available` |
| `AllowListNotEnabled` | — |
| `BucketOverfilled` | — |
| `CallerIsNotARampOnRouter` | `address caller` |
| `CannotTransferToSelf` | — |
| `ChainAlreadyExists` | `uint64 chainSelector` |
| `ChainNotAllowed` | `uint64 remoteChainSelector` |
| `CursedByRMN` | — |
| `DisabledNonZeroRateLimit` | `(bool isEnabled, uint128 capacity, uint128 rate) config` |
| `InvalidDecimalArgs` | `uint8 expected, uint8 actual` |
| `InvalidRateLimitRate` | `(bool isEnabled, uint128 capacity, uint128 rate) rateLimiterConfig` |
| `InvalidRemoteChainDecimals` | `bytes sourcePoolData` |
| `InvalidRemotePoolForChain` | `uint64 remoteChainSelector, bytes remotePoolAddress` |
| `InvalidSourcePoolAddress` | `bytes sourcePoolAddress` |
| `InvalidToken` | `address token` |
| `MismatchedArrayLengths` | — |
| `MustBeProposedOwner` | — |
| `NonExistentChain` | `uint64 remoteChainSelector` |
| `OnlyCallableByOwner` | — |
| `OverflowDetected` | `uint8 remoteDecimals, uint8 localDecimals, uint256 remoteAmount` |
| `OwnerCannotBeZero` | — |
| `PoolAlreadyAdded` | `uint64 remoteChainSelector, bytes remotePoolAddress` |
| `RateLimitMustBeDisabled` | — |
| `SenderNotAllowed` | `address sender` |
| `TokenMaxCapacityExceeded` | `uint256 capacity, uint256 requested, address tokenAddress` |
| `TokenRateLimitReached` | `uint256 minWaitInSeconds, uint256 available, address tokenAddress` |
| `Unauthorized` | `address caller` |
| `ZeroAddressNotAllowed` | — |

<!-- END GENERATED API REFERENCE: BurnMintTokenPool151 -->
