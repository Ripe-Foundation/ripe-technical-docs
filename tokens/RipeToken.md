# RipeToken

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/tokens/RipeToken.vy)

## Overview

RIPE is the protocol's 18-decimal governance and incentive token. It
specializes `Erc20Token` with name `Ripe DAO Governance Token`, symbol `RIPE`,
and a RipeHq-authorized mint route.

Protocol tokenomics define RIPE's total supply as one billion across chains.
Each `RipeToken` contract maintains only its chain-local ERC-20 `totalSupply`;
the contract does not maintain a cross-chain aggregate or enforce the
one-billion policy as a local supply cap.

## Constructor and supply accounting

```text
__init__(ripeHq, initialGov, minHqTimeLock, maxHqTimeLock, initialSupply, initialSupplyRecipient)
mint(recipient, amount)
```

The constructor can mint `_initialSupply` to `_initialSupplyRecipient`. Later
minting requires `RipeHq.canMintRipe(caller)`. RipeHq requires global mint
enablement, nonzero current registry membership, the registry entry's
`canMintRipe` permission, and the caller contract's declared RIPE-mint
capability. RIPE does not contain a permanent hardcoded minter list or a
maximum-supply check. The shared mint path also enforces pause and recipient
blacklist/address checks.

Minting increases the local `totalSupply`. Holder burns and governance burns of
blacklisted balances decrease it.

## Shared token behavior

RIPE inherits the Erc20Token transfer, allowance, EIP-2612/1271 permit, burn, blacklist, pause, and HQ-rotation behavior.

Important inherited behavior includes:

- approval revocation through zero `approve`/`permit` or `decreaseAllowance` remains possible while ordinary new approval is blocked;
- EOA permits require exactly 65 bytes plus canonical `v` and low-`s` checks;
- a blacklisted RIPE holder may self-burn, while only RipeHq governance may use
  `burnBlacklistTokens` against a blacklisted balance; and
- a RipeHq rotation must retain the same complete GREEN/sGREEN/RIPE token suite and settled governance state.

## Cross-chain administration and accounting

Once RipeHq is set, `getCCIPAdmin()` returns its governance address for Chainlink
TokenAdminRegistry administrator nomination.

The token-specific RIPE CCIP pool advertises burn/mint capability without
lock/release capability. A completed cross-chain transfer burns an amount from
the source-chain representation and mints the same 18-decimal amount on the
destination-chain representation. This moves supply between chain-local
contracts; the pool does not store or calculate the aggregate supply. While a
message is in flight, the burned amount is temporarily absent from the sum of
chain-local `totalSupply` values.

## Integration notes

- Resolve mint and governance authority through RipeHq.
- Check pause and blacklist state for transfers and new approvals.
- Preserve the documented approval-revocation behavior in wallets.
- Treat `totalSupply()` as chain-local rather than protocol-wide.
- Treat `getCCIPAdmin()` as an administrator-discovery hook rather than a pool
  registration function.

<!-- BEGIN GENERATED API REFERENCE: RipeToken -->
## Exact API reference

> Generated from `contracts/tokens/RipeToken.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _initialGov, uint256 _minHqTimeLock, uint256 _maxHqTimeLock, uint256 _initialSupply, address _initialSupplyRecipient)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `burnBlacklistTokens(address _addr, uint256 _amount)` | `1–2` | `_amount` |
| `finishTokenSetup(address _newHq, uint256 _timeLock)` | `1–2` | `_timeLock` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `DOMAIN_SEPARATOR()` | `view` | `bytes32` |
| `TOKEN_DECIMALS()` | `view` | `uint8` |
| `TOKEN_NAME()` | `view` | `string` |
| `TOKEN_SYMBOL()` | `view` | `string` |
| `VERSION()` | `view` | `string` |
| `allowance(address arg0, address arg1)` | `view` | `uint256` |
| `approve(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `balanceOf(address arg0)` | `view` | `uint256` |
| `blacklisted(address arg0)` | `view` | `bool` |
| `burn(uint256 _amount)` | `nonpayable` | `bool` |
| `burnBlacklistTokens(address _addr)` | `nonpayable` | `bool` |
| `burnBlacklistTokens(address _addr, uint256 _amount)` | `nonpayable` | `bool` |
| `cancelHqChange()` | `nonpayable` | — |
| `confirmHqChange()` | `nonpayable` | `bool` |
| `decimals()` | `view` | `uint8` |
| `decreaseAllowance(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `finishTokenSetup(address _newHq)` | `nonpayable` | `bool` |
| `finishTokenSetup(address _newHq, uint256 _timeLock)` | `nonpayable` | `bool` |
| `getCCIPAdmin()` | `view` | `address` |
| `hasPendingHqChange()` | `view` | `bool` |
| `hqChangeTimeLock()` | `view` | `uint256` |
| `increaseAllowance(address _spender, uint256 _amount)` | `nonpayable` | `bool` |
| `initiateHqChange(address _newHq)` | `nonpayable` | — |
| `isPaused()` | `view` | `bool` |
| `isValidHqChangeTimeLock(uint256 _newTimeLock)` | `view` | `bool` |
| `isValidNewRipeHq(address _newHq)` | `view` | `bool` |
| `maxHqTimeLock()` | `view` | `uint256` |
| `minHqTimeLock()` | `view` | `uint256` |
| `mint(address _recipient, uint256 _amount)` | `nonpayable` | `bool` |
| `name()` | `view` | `string` |
| `nonces(address arg0)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pendingHq()` | `view` | `(address,uint256,uint256)` |
| `permit(address _owner, address _spender, uint256 _value, uint256 _deadline, bytes _signature)` | `nonpayable` | `bool` |
| `ripeHq()` | `view` | `address` |
| `setBlacklist(address _addr, bool _shouldBlacklist)` | `nonpayable` | `bool` |
| `setHqChangeTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` |
| `symbol()` | `view` | `string` |
| `totalSupply()` | `view` | `uint256` |
| `transfer(address _recipient, uint256 _amount)` | `nonpayable` | `bool` |
| `transferFrom(address _sender, address _recipient, uint256 _amount)` | `nonpayable` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `Approval` | `address owner indexed, address spender indexed, uint256 amount` |
| `BlacklistModified` | `address addr indexed, bool isBlacklisted` |
| `HqChangeCancelled` | `address cancelledHq indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqChangeConfirmed` | `address prevHq indexed, address newHq indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `HqChangeInitiated` | `address prevHq indexed, address newHq indexed, uint256 confirmBlock` |
| `HqChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `InitialRipeHqSet` | `address hq indexed, uint256 timeLock` |
| `TokenPauseModified` | `bool isPaused` |
| `Transfer` | `address sender indexed, address recipient indexed, uint256 amount` |

<!-- END GENERATED API REFERENCE: RipeToken -->
