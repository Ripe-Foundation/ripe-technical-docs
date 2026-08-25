# Erc20Token module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/tokens/modules/Erc20Token.vy)

## Overview

`Erc20Token` is the shared implementation behind GREEN, RIPE, and Savings GREEN shares. It provides ERC-20 balances and allowances, EIP-2612/1271 permits, pause and blacklist controls, timelocked RipeHq rotation, protected burns, and the CCIP admin discovery hook.

## Initialization

The module stores immutable name, symbol, decimals, HQ timelock bounds, and
EIP-712 domain data. Construction forbids setting both `ripeHq` and `initialGov`
to nonzero addresses. It permits three initial states:

- a nonzero RipeHq with no temporary governor; or
- a temporary governor with no RipeHq, followed once by `finishTokenSetup`; or
- both control addresses unset.

The third state is permanently control-orphaned: `tempGov` remains zero, so no
caller can complete setup, and HQ-dependent mint, pause, blacklist, rotation,
and CCIP-admin routes have no usable authority. Ordinary holder operations
remain subject to their own token-state checks.

If `initialSupply` is nonzero and its recipient is neither zero nor the token contract, the constructor mints it and emits the standard transfer-from-zero event. The base module does not require a nonzero initial supply.

## Transfers

`transfer` and `transferFrom` reject:

- a paused token;
- zero amount;
- zero or self recipient;
- blacklisted sender or recipient; and
- insufficient balance.

`transferFrom` also rejects a blacklisted spender and consumes allowance unless it is `max_value(uint256)`. Infinite allowance is not decremented.

## Approval and revocation behavior

Creating or increasing spend authority requires an unpaused token and non-blacklisted owner and spender.

Revocation is intentionally more available:

- `approve(spender, 0)` requires only a nonzero spender;
- `permit(..., value = 0, ...)` uses the same reduced spender check, while still requiring a valid, unexpired signature; and
- `decreaseAllowance` requires only a nonzero spender and floors at zero.

This allows an owner to reduce risk while the token or either party is paused/blacklisted. `increaseAllowance`, including a zero increase, uses the full new-approval checks. Nonzero `approve` and `permit` also use the full checks.

## Permit validation

The domain separator is cached for the chain ID observed at construction and
recomputed if `chain.id` changes. Nonces increment only after successful
signature validation.

- Contract owners use ERC-1271 and must return `0x1626ba7e`.
- EOA signatures must be exactly 65 bytes.
- `v` is normalized from 0/1 to 27/28 when needed and must end as 27 or 28.
- `s` must be nonzero and in the lower half of the secp256k1 order.
- the recovered signer must equal `owner`.

The owner must be nonzero and the deadline must not have passed.

## Minting and burning

Concrete token contracts expose their own mint authorization and call the module's `_mint`. Minting rejects a zero/self or blacklisted recipient and a paused token.

`burn(amount)` is available while unpaused. Balance/supply underflow protects against burning more than the caller owns.

For a token that also exposes an ERC-4626 `asset()` function:

- a blacklisted share owner cannot use the ordinary burn route; and
- burning the entire outstanding share supply is prohibited while the vault still holds underlying assets.

Bare tokens such as GREEN and RIPE expose no `asset()` function, so a
blacklisted holder may still burn its own bare-token balance.

That full-supply guard prevents a nonzero underlying balance from becoming permanently unowned.

## Blacklist administration and backing guards

An address authorized by `RipeHq.canSetTokenBlacklist` may set blacklist state, except for zero and the token contract itself. RipeHq governance alone may call `burnBlacklistTokens` for a blacklisted holder.

Two backing guards are critical:

- GREEN governance cannot burn GREEN held by the Savings GREEN vault, because those tokens back sGREEN shares; and
- for any ERC-4626 token using this module, governance cannot burn the full share supply while underlying remains in the vault.

The blacklist burn amount is capped to the holder's actual balance and must be nonzero.

## RipeHq lifecycle

HQ rotation is block-timelocked and controlled by current RipeHq governance. A candidate must be a contract with settled governance and no pending governance change, expose the required mint/blacklist interfaces, and register a complete nonzero GREEN/sGREEN/RIPE suite containing this token.

When rotating from an existing HQ, the entire token suite must be identical in old and new HQ. This continuity is especially important for the GREEN backing guard, which must continue to recognize the same Savings GREEN contract. The current HQ also cannot have a pending governance change.

Confirmation revalidates the candidate. If it is no longer valid, the pending change is cleared and the function returns false.

`finishTokenSetup(newHq, timeLock = 0)` is a one-time temporary-governor route. Zero time lock selects the immutable minimum; any explicit value must satisfy the immutable min/max bounds. The temporary governor is then cleared.

## Pause control

Current RipeHq governance alone may change `isPaused`, and the value must actually change. Pause blocks transfers, new approvals, minting, ordinary burns, and ERC-4626 entry/exit paths that rely on this module. Approval reduction/revocation remains available as described above.

## CCIP admin discovery

Once RipeHq is set, `getCCIPAdmin()` returns its current governance address.
Chainlink's TokenAdminRegistry ownership module can use this getter to propose
the token's CCIP administrator, who in turn can register or replace a token
pool. Before temporary-governor setup is finished, the stored RipeHq is zero and
the getter reverts.

This getter does not register a pool, configure a remote chain, or change rate
limits. Those operations belong to the Chainlink administration contracts.

## Integration requirements

- Do not assume every approval operation is blocked during pause; reductions are deliberately permitted.
- Preserve the full GREEN/sGREEN/RIPE suite across any HQ rotation.
- Never burn Savings GREEN's backing GREEN through blacklist administration.
- Treat `getCCIPAdmin` as an admin-discovery hook, not proof of CCIP activation.

<!-- BEGIN GENERATED API REFERENCE: Erc20Token -->
## Exact API reference

> Generated from `contracts/tokens/modules/Erc20Token.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(string _tokenName, string _tokenSymbol, uint8 _tokenDecimals, address _ripeHq, address _initialGov, uint256 _minHqTimeLock, uint256 _maxHqTimeLock, uint256 _initialSupply, address _initialSupplyRecipient)`

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

### Structs declared by this source

- `PendingHq(newHq: address, initiatedBlock: uint256, confirmBlock: uint256)`

<!-- END GENERATED API REFERENCE: Erc20Token -->
