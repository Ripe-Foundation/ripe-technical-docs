# RipeCcipBurnMintTokenPools

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/RipeCcipBurnMintTokenPools.sol)

## Overview

`RipeCcipBurnMintTokenPools.sol` defines token-specific GREEN and RIPE Chainlink
CCIP burn/mint pools. Both inherit the vendored `BurnMintTokenPool 1.5.1`
implementation and add Ripe-specific mint-capability views used by `RipeHq`.

## Token-specific contracts

### `GreenCcipBurnMintTokenPool`

The GREEN pool compiles its Ripe capabilities into pure functions:

```text
canMintGreen() -> true
canMintRipe()  -> false
```

### `RipeCcipBurnMintTokenPool`

The RIPE pool returns the inverse:

```text
canMintGreen() -> false
canMintRipe()  -> true
```

Using separate contracts prevents the GREEN/RIPE capability pair from being
reversed through constructor flags.

## Constructor and binding requirement

Both contracts inherit this constructor shape:

```text
constructor(
  token,
  localTokenDecimals,
  allowlist,
  rmnProxy,
  router
)
```

The inherited constructor accepts an arbitrary burn/mint token. The
token-specific capability answers do not validate that token, so callers must
pair the GREEN class with GREEN and the RIPE class with RIPE. The other
arguments bind the token decimals, initial allowlist, RMN proxy, and router used
by the inherited state machine.

## RipeHq two-factor mint authorization

RipeHq reads `canMintGreen` and `canMintRipe` when a registry configuration is
proposed or confirmed and again on every mint authorization check. Authorization
requires all four conditions:

1. global minting is enabled;
2. the pool has nonzero current registry membership;
3. its registry entry grants the relevant mint permission; and
4. the pool returns the matching capability answer.

The permission/capability pair prevents registry configuration alone from
granting the wrong token authority. These RipeHq checks are independent of
Chainlink ownership, remote-chain, RMN, allowlist, and rate-limit controls.

## Inherited behavior

All CCIP message validation, burn/mint execution, ownership, two-step ownership
transfer, RMN checks, allowlist behavior, remote-chain state, router management,
and rate limiting come from the vendored Chainlink pool implementation. The
Ripe contracts do not override that state machine.

The complete inherited selector, event, and custom-error surface is documented
in the [composed BurnMintTokenPool 1.5.1 reference](BurnMintTokenPool151.md).

For a completed transfer, the source pool burns the transferred amount and the
destination pool mints the corresponding amount. This moves supply between
chain-local token representations. Neither pool maintains a cross-chain supply
total. Rate limits constrain per-lane transfer volume; they do not impose an
aggregate token-supply cap.

## Token administration

GREEN and RIPE expose `getCCIPAdmin()` through their shared token module. Once
the token's RipeHq is set, the getter returns RipeHq governance for Chainlink
TokenAdminRegistry administrator nomination. Administrator nomination and
token-pool registration are distinct operations.

<!-- BEGIN GENERATED API REFERENCE: RipeCcipBurnMintTokenPools -->
## Ripe-specific source delta

> Generated from declarations written directly in `solidity/src/RipeCcipBurnMintTokenPools.sol`. The concrete contracts also expose the inherited operational surface documented in the [composed BurnMintTokenPool 1.5.1 reference](BurnMintTokenPool151.md).

### `GreenCcipBurnMintTokenPool`

- `constructor(IBurnMintERC20 token, uint8 localTokenDecimals, address[] memory allowlist, address rmnProxy, address router) BurnMintTokenPool(token, localTokenDecimals, allowlist, rmnProxy, router)`
- `function canMintGreen() external pure returns (bool)`
- `function canMintRipe() external pure returns (bool)`

### `RipeCcipBurnMintTokenPool`

- `constructor(IBurnMintERC20 token, uint8 localTokenDecimals, address[] memory allowlist, address rmnProxy, address router) BurnMintTokenPool(token, localTokenDecimals, allowlist, rmnProxy, router)`
- `function canMintGreen() external pure returns (bool)`
- `function canMintRipe() external pure returns (bool)`

<!-- END GENERATED API REFERENCE: RipeCcipBurnMintTokenPools -->
