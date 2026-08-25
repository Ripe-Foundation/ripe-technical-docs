# Boardroom

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/Boardroom.vy)

## Contract surface

`Boardroom` is a department and governance-vault callback target. It exports the
standard Addys and DeptBasics interfaces and cannot mint GREEN or RIPE.

Its only contract-specific method is:

- `govPowerDidChangeForUser(user, userGovPoints, totalGovPoints)`

The callback accepts governance-point updates but does not store, aggregate,
vote with, or otherwise act on those values. It does not read Boardroom's pause
flag, so pausing the department does not disable this callback.

## Caller validation

The callback is not permissionless. Boardroom resolves `msg.sender` through VaultBook, requires a nonzero registered vault ID, and then requires MissionControl to classify that ID as a RipeGov vault. This classification is dynamic and includes the protocol's recognized current/historical RipeGov topology; callers should not assume a fixed numeric vault ID.

## Integration note

Governance vaults may call the hook as their users' power changes. Proposal,
voting, delegation, quorum, and reward behavior are not part of this contract's
API or state machine.

<!-- BEGIN GENERATED API REFERENCE: Boardroom -->
## Exact API reference

> Generated from `contracts/core/Boardroom.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getRipeHq()` | `view` | `address` | — |
| `govPowerDidChangeForUser(address _user, uint256 _userGovPoints, uint256 _totalGovPoints)` | `nonpayable` | — | — |
| `isPaused()` | `view` | `bool` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `no perms`

<!-- END GENERATED API REFERENCE: Boardroom -->
