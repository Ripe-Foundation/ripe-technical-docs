# RipeTokenPool

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/solidity/src/RipeTokenPool.sol)

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

<!-- BEGIN GENERATED API REFERENCE: RipeTokenPool -->
## Exact source-declared API reference

> Generated from declarations in `solidity/src/RipeTokenPool.sol`. This file has no first-party tracked ABI under `scripts/abis`; inherited Chainlink members are outside this source-declared inventory.

### `RipeTokenPool`

- `constructor(IBurnMintERC20 token, uint8 localTokenDecimals, address[] memory allowlist, address rmnProxy, address router, bool canMintGreen_, bool canMintRipe_) BurnMintTokenPool(token, localTokenDecimals, allowlist, rmnProxy, router)`
- `function canMintGreen() external view returns (bool)`
- `function canMintRipe() external view returns (bool)`

<!-- END GENERATED API REFERENCE: RipeTokenPool -->
