# RipeTokenPool

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/solidity/src/RipeTokenPool.sol)

## Overview

`RipeTokenPool.sol` is a configurable-capability CCIP burn/mint pool. It
inherits the vendored `BurnMintTokenPool 1.5.1` implementation and adds two
immutable capability flags consumed by `RipeHq`.

## Behavior

The constructor accepts these capability flags:

```text
canMintGreen_
canMintRipe_
```

The corresponding views return those stored values. RipeHq reads them when granting mint privileges and on every mint authorization check.

The class permits every Boolean combination, including both true and both
false. It also inherits an arbitrary token constructor argument. The
constructor does not validate that the token identity matches the selected
capabilities.

New integrations should prefer the token-specific pool classes. They compile
the intended GREEN or RIPE capability pair into separate contracts and remove
the configurable flag-mismatch hazard, although callers must still bind each
class to the corresponding token.

## Constructor

```text
constructor(
  token,
  localTokenDecimals,
  allowlist,
  rmnProxy,
  router,
  canMintGreen,
  canMintRipe
)
```

The two capability values are immutable after construction. All CCIP execution,
ownership, remote-chain, allowlist, RMN, router, and rate-limit behavior is
inherited. The token-specific classes in
[RipeCcipBurnMintTokenPools](RipeCcipBurnMintTokenPools.md) remove the two
capability arguments by compiling the GREEN and RIPE pairs into separate
contracts.

See the [composed BurnMintTokenPool 1.5.1 reference](BurnMintTokenPool151.md)
for the inherited execution, ownership, remote-chain, allowlist, router, RMN,
rate-limit, event, and error surface.

<!-- BEGIN GENERATED API REFERENCE: RipeTokenPool -->
## Ripe-specific source delta

> Generated from declarations written directly in `solidity/src/RipeTokenPool.sol`. The concrete contracts also expose the inherited operational surface documented in the [composed BurnMintTokenPool 1.5.1 reference](BurnMintTokenPool151.md).

### `RipeTokenPool`

- `constructor(IBurnMintERC20 token, uint8 localTokenDecimals, address[] memory allowlist, address rmnProxy, address router, bool canMintGreen_, bool canMintRipe_) BurnMintTokenPool(token, localTokenDecimals, allowlist, rmnProxy, router)`
- `function canMintGreen() external view returns (bool)`
- `function canMintRipe() external view returns (bool)`

<!-- END GENERATED API REFERENCE: RipeTokenPool -->
