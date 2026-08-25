# GreenToken

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/tokens/GreenToken.vy)

## Overview

GREEN is the protocol's 18-decimal stablecoin token. It is an `Erc20Token`
specialization named `Green USD Stablecoin` with symbol `GREEN` and a
RipeHq-authorized mint route.

## Constructor and supply

```text
__init__(ripeHq, initialGov, minHqTimeLock, maxHqTimeLock, initialSupply, initialSupplyRecipient)
```

Construction follows the mutually exclusive control-address rules described in
the shared token module: RipeHq, a temporary governor, or neither may be set.
Leaving both unset permanently leaves HQ-dependent setup and controls without a
usable authority. A valid nonzero initial-supply and recipient pair is optional
at the base-token level.

## Mint authority

```text
mint(recipient, amount)
```

The caller must pass `RipeHq.canMintGreen(caller)`. RipeHq requires global mint
enablement, nonzero current registry membership, the registry entry's
`canMintGreen` permission, and the caller contract's declared GREEN-mint
capability. The token does not hardcode a permanent minter list.

The shared mint path rejects zero/self or blacklisted recipients and a paused token.

## Shared controls

GREEN inherits transfers, allowances, permits, burns, blacklisting, pause, and timelocked RipeHq rotation from `Erc20Token`.

Important inherited behavior includes:

- zero-value approval/permit and allowance decrease remain available to revoke authority during pause/blacklist conditions;
- EOA permits require an exact 65-byte, nonmalleable signature;
- HQ rotation must preserve the identical GREEN/sGREEN/RIPE suite; and
- governance cannot use `burnBlacklistTokens` against the Savings GREEN vault, because its GREEN balance backs sGREEN shares.

## CCIP administration

Once RipeHq is set, `getCCIPAdmin()` returns its governance address for
Chainlink's TokenAdminRegistry administrator-nomination flow. It does not
register a token pool or configure a remote chain.

The token-specific GREEN pool advertises burn/mint capability without
lock/release capability. Its inherited Chainlink behavior burns GREEN on the
source side and mints GREEN on the destination side.

## Integration requirements

- Resolve mint and governance authority through RipeHq.
- Do not burn or otherwise treat Savings GREEN's GREEN custody as free protocol funds.
- Check token pause/blacklist state and allowance-revocation exceptions.
- Treat `getCCIPAdmin()` as an administrator-discovery hook rather than a pool
  or lane getter.

<!-- BEGIN GENERATED API REFERENCE: GreenToken -->
## Exact API reference

> Generated from `contracts/tokens/GreenToken.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

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

<!-- END GENERATED API REFERENCE: GreenToken -->
