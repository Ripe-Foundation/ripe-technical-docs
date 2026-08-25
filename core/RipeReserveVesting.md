# RipeReserveVesting

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/RipeReserveVesting.vy)

`RipeReserveVesting` stores block-based vesting positions created by the current
`RipeReserveEngine` and records the amounts that engine may settle. It does not
hold or mint RIPE.

## Construction and authority

Construction binds RipeHq, starts the department paused with neither GREEN nor
RIPE mint capability, and initializes position IDs at one. Only the contract
currently registered at RipeHq ID 26 may create positions or record claims.
Registered Switchboards may replace the remaining allocation budget, which
starts at its zero-value default. The engine resolves its vesting store through
RipeHq ID 27; the vesting contract does not independently assert that it
currently occupies that slot.

Because engine authority is resolved from RipeHq on every write, replacing ID 26
immediately removes the old engine's ability to mutate vesting state and grants
the new current engine claim-recording authority over every existing position.
`sourceEngine` is creation-event metadata, not stored position authorization. A
replacement engine must preserve outstanding-position settlement semantics: an
incompatible implementation can strand claims, while a malicious current engine
can advance claim accounting without completing RIPE settlement.

## Position lifecycle

`createVestingPosition` requires an unpaused contract, a nonzero beneficiary and
allocation, enough remaining budget, a nonzero minimum vesting length, and a
vesting length at least as long as that minimum. It records creation,
claim-start, and maturity blocks, decrements the current budget, and increments
`totalAllocatedRipe`.

Positions have monotonic nonzero IDs, while the per-user storage index is a
compact one-based array. When a position is fully claimed, the final position is
moved into the removed slot. Integrators should resolve an ID through
`indexOfPosition`; numeric storage indexes are not stable identifiers. Both an
unknown ID and a fully removed ID return zero from `getVestedRipe` and
`getClaimableRipe`, so `indexOfPosition` is also the absence discriminator.

## Vesting and claims

Nothing is claimable before `claimStartBlock`. From that block until maturity,
the vested total is the allocation multiplied by elapsed blocks since creation
and divided by the full creation-to-maturity duration, rounded down with
full-precision multiplication and division. At or after maturity the full
allocation is vested. This means the first permitted claim includes vesting
accrued since creation, not only since the claim-start block.

`recordClaim` computes newly claimable RIPE, rejects a zero result, updates the
position and global claimed total, and removes a fully claimed position. It
returns the amount claimed, cumulative claimed amount for that position, and
the original allocation so the engine can emit and settle the complete claim
record. `recordClaim` also requires this vesting contract to be unpaused, so
pausing vesting freezes claims even after positions have matured.

## Budget and retirement

`remainingAllocationBudget` limits future position creation. Governance may
replace it with any amount, including zero; it is not a lifetime ceiling and is
not a cross-chain RIPE supply cap. `totalOutstandingRipe` is allocated minus
claimed RIPE for this vesting program. `canRetire` is true only while the
contract is paused and that outstanding liability is zero.

Replacing RipeHq ID 27 changes the vesting store used by the current engine and
does not migrate positions from the prior store. `canRetire` is an advisory
readiness view; neither this contract nor the generic RipeHq registry-update path
automatically requires it before replacement.

<!-- BEGIN GENERATED API REFERENCE: RipeReserveVesting -->
## Exact API reference

> Generated from `contracts/core/RipeReserveVesting.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `canRetire()` | `view` | `bool` | `bool` |
| `createVestingPosition(address _user, uint256 _ripeAllocation, uint256 _vestingLength, uint256 _minVestingLength)` | `nonpayable` | `uint256` | `uint256` |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getClaimableRipe(address _user, uint256 _positionId)` | `view` | `uint256` | `uint256` |
| `getNumUserPositions(address _user)` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `getVestedRipe(address _user, uint256 _positionId)` | `view` | `uint256` | `uint256` |
| `indexOfPosition(address arg0, uint256 arg1)` | `view` | `uint256` | — |
| `isPaused()` | `view` | `bool` | — |
| `nextPositionId()` | `view` | `uint256` | — |
| `numUserPositions(address arg0)` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `positions(address arg0, uint256 arg1)` | `view` | `(uint256 id, uint256 ripeAllocation, uint256 ripeClaimed, uint256 creationBlock, uint256 claimStartBlock, uint256 maturityBlock)` | — |
| `recordClaim(address _user, uint256 _positionId)` | `nonpayable` | `(uint256, uint256, uint256)` | `(uint256, uint256, uint256)` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `remainingAllocationBudget()` | `view` | `uint256` | — |
| `setRemainingAllocationBudget(uint256 _amount)` | `nonpayable` | — | — |
| `totalAllocatedRipe()` | `view` | `uint256` | — |
| `totalClaimedRipe()` | `view` | `uint256` | — |
| `totalOutstandingRipe()` | `view` | `uint256` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `ClaimRecorded` | `address user indexed, uint256 positionId indexed, uint256 amountClaimed, uint256 totalClaimedForPosition, uint256 ripeAllocation, bool fullyClaimed` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `RemainingAllocationBudgetSet` | `uint256 amount` |
| `VestingPositionCreated` | `address user indexed, uint256 positionId indexed, address sourceEngine indexed, uint256 ripeAllocation, uint256 creationBlock, uint256 claimStartBlock, uint256 maturityBlock` |

### Structs declared by this source

- `VestingPosition(id: uint256, ripeAllocation: uint256, ripeClaimed: uint256, creationBlock: uint256, claimStartBlock: uint256, maturityBlock: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `allocation budget`
- `claim start overflow`
- `duplicate position`
- `invalid allocation`
- `invalid engine`
- `invalid last position`
- `invalid minimum vesting`
- `invalid position`
- `invalid user`
- `invalid vesting length`
- `maturity overflow`
- `no perms`
- `no positions`
- `nothing to claim`
- `occupied position`
- `paused`
- `result overflows`
- `zero denominator`

<!-- END GENERATED API REFERENCE: RipeReserveVesting -->
