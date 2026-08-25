# TrainingWheels

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/TrainingWheels.vy)

`TrainingWheels` is a small protocol whitelist. MissionControl can reference it
as an asset whitelist. At the contract boundary, any currently registered
Switchboard may manage its members; SwitchboardCharlie supplies the normal
governed batch-management route.

## Initialization

The constructor binds the contract to RipeHq and accepts up to 20 initial
addresses. Zero addresses are skipped; each nonzero entry is marked allowed and
emits `TrainingWheelsModified`. The contract uses `DeptBasics` but cannot mint
GREEN or RIPE.

## Membership updates

`setAllowed(user, shouldAllow)` may be called only by a currently registered
Switchboard configuration contract. The user must be nonzero. Writing the same
value is allowed and still emits an event.

Operationally, Charlie's governed
`setManyTrainingWheelsAccess(trainingWheels, rows)` helper can apply up to 25
membership rows to an explicitly supplied TrainingWheels address. This helper
works because Charlie is a registered Switchboard; it does not make Charlie the
only contract that `TrainingWheels.setAllowed` authorizes. Changing
MissionControl's TrainingWheels pointer is a separate timelocked Charlie action.

`isUserAllowed(user, asset)` returns the stored user flag. The asset parameter
is intentionally ignored so that TrainingWheels remains compatible with the
protocol's generic per-asset whitelist interface.

## Security and lifecycle

- TrainingWheels has no independent governor; authority follows current
  Switchboard registry membership.
- Updating MissionControl's `trainingWheels` pointer does not mutate or disable
  an older whitelist contract.
- Membership is global to the TrainingWheels instance, not per asset.

<!-- BEGIN GENERATED API REFERENCE: TrainingWheels -->
## Exact API reference

> Generated from `contracts/config/TrainingWheels.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address[] _initialList)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `allowed(address arg0)` | `view` | `bool` | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | — |
| `isUserAllowed(address _user, address _asset)` | `view` | `bool` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `setAllowed(address _user, bool _shouldAllow)` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `TrainingWheelsModified` | `address user indexed, bool shouldAllow` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid user`
- `no perms`

<!-- END GENERATED API REFERENCE: TrainingWheels -->
