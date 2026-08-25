# Boardroom

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/Boardroom.vy)

## Contract surface

`Boardroom` is a department and governance-vault callback target. It exports the
standard Addys and DeptBasics interfaces and cannot mint GREEN.

Its only contract-specific method is:

- `govPowerDidChangeForUser(user, userGovPoints, totalGovPoints)`

The callback accepts governance-point updates but does not store, aggregate,
vote with, or otherwise act on those values.

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

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `govPowerDidChangeForUser(address _user, uint256 _userGovPoints, uint256 _totalGovPoints)` | `nonpayable` | — |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

<!-- END GENERATED API REFERENCE: Boardroom -->
