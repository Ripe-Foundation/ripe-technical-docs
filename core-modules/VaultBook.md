# VaultBook

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/registries/VaultBook.vy)

`VaultBook` is the registry of protocol vault implementations. A numeric vault
ID is the stable routing identity; its current implementation address may be
updated or disabled through governance-controlled registry operations.

## Composition and authority

VaultBook composes `LocalGov`, `AddressRegistry`, `Addys`, and `DeptBasics`.
Registry mutations require a recognized governor and an unpaused VaultBook.
Registry IDs are one-based and remain allocated even if their current address
is disabled.

Construction starts VaultBook unpaused, with a zero registry delay,
`canMintGreen() = false`, and `canMintRipe() = true`. The zero setup delay lets
registry proposals confirm in the same block until governance calls
`setRegistryTimeLockAfterSetup`. The inherited ABI also exposes
`finishRipeHqSetup`, but that function is permanently inapplicable here:
VaultBook is constructed with a nonzero RipeHq, while the function is usable
only by a `LocalGov` instance initialized as top-level (`RIPE_HQ_FOR_GOV == 0`).

Each proposal snapshots its own `confirmBlock`. Closing setup changes the delay
only for future proposals; it does not add delay to an add, update, or disable
record created while the delay was zero. Operators must inventory and cancel any
unwanted setup-era pending records before treating the setup window as closed.

`isVaultBookAddr(addr)` tests current registry membership. It does not recognize
an implementation that has been replaced or disabled.

## Add, replace, and disable

New vaults use the generic propose/confirm/cancel registry lifecycle. Updates
and disables add custody protections:

- the current vault must have no funds when the action is proposed;
- the no-funds condition is checked again at confirmation; and
- replacement implementations must preserve any specialized interface attached
  to the vault ID's historical classification.

For ordinary vaults, `doesVaultHaveAnyFunds()` is the accounting signal. For an
ID ever classified as RipeGov, nonzero `totalGovPoints()` also blocks update or
disable because zero-share governance-point residue cannot be migrated safely.
The historical-classification lookup comes from the current MissionControl. If
RipeHq resolves MissionControl to zero, both the specialized replacement probes
and the extra RipeGov-point residue check are skipped; the generic vault-funds
check still runs.

Replacement shape is checked at proposal and again after the generic registry
update during confirmation. A failed post-update probe reverts the whole
transaction, including the registry write.

## Current pointers versus historical classifications

MissionControl maintains two different concepts:

| Concept | Meaning |
| --- | --- |
| `coreRipeGovVaultId` | Current destination used for new core RipeGov routing |
| `preferredStabVaultId` | Current preferred StabilityPool routing target |
| `isRipeGovVaultId[id]` | Monotonic historical classification |
| `isStabVaultId[id]` | Monotonic historical classification |

Changing a current pointer does not erase the previous ID's classification.
Historical IDs can retain user balances, maintenance paths, or reward-minting
authority. When MissionControl is present:

- replacing any historically classified RipeGov ID probes the new
  implementation's governance-points interface; and
- replacing any historically classified StabilityPool ID probes its vault,
  claim accounting, liquidation-acceptance, and pause interfaces.

These probes preserve callable shape; they do not assert that the replacement
has the same economic configuration.

## StabilityPool reward minting

`mintRipeForStabPoolClaims` is not available to every registered vault. It
requires all of the following:

1. the caller currently resolves to a nonzero VaultBook ID;
2. MissionControl classifies that ID as a StabilityPool ID;
3. the caller-supplied RIPE token and Ledger equal the canonical addresses from
   `RipeHq`; and
4. the requested amount does not exceed Ledger's remaining reward budget.

On success, VaultBook mints RIPE to the calling StabilityPool and tells Ledger
to account for the reward expenditure. This entry point does not check
VaultBook's own pause flag, and zero is an accepted amount; both downstream
calls still execute for a zero amount.

Those downstream calls enforce additional current-state gates. RIPE minting
asks RipeHq to authorize the calling VaultBook address as a current registry
member with RIPE-mint permission and the matching immutable capability while
global minting is enabled; that check is not intrinsically tied to registry ID
8. The RIPE token must also be unpaused and the recipient StabilityPool must not
be blacklisted. Ledger independently requires its caller to equal the canonical
VaultBook resolved at ID 8 and requires Ledger itself to be unpaused. A failure
in either call reverts the entire transaction, so a successful mint cannot
persist without the matching Ledger accounting update.

## Operational cautions

- `isValidRegId(id)` alone does not prove that `getAddr(id)` is nonzero.
- An apparently empty vault may still be non-retirable because of governance
  point residue.
- Historical StabilityPool classification is intentionally not revoked when a
  preferred or special pool changes.
- An inherited disable proposal is bound only to its vault ID. If that ID is
  updated while the disable remains pending, confirmation checks and disables
  the then-current replacement, not the proposal-time address.
- Update and disable confirmations must be treated as state-sensitive actions;
  conditions are deliberately checked again after the timelock.

<!-- BEGIN GENERATED API REFERENCE: VaultBook -->
## Exact API reference

> Generated from `contracts/registries/VaultBook.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minRegistryTimeLock, uint256 _maxRegistryTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `0–1` | `_numBlocks = 0` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `addrInfo(uint256 arg0)` | `view` | `(address addr, uint256 version, uint256 lastModified, string description)` | — |
| `addrToRegId(address arg0)` | `view` | `uint256` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `cancelAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` | `bool` |
| `cancelAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` | `bool` |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelNewAddressToRegistry(address _addr)` | `nonpayable` | `bool` | `bool` |
| `confirmAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` | `bool` |
| `confirmAddressUpdateToRegistry(uint256 _regId)` | `nonpayable` | `bool` | `bool` |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `confirmNewAddressToRegistry(address _addr)` | `nonpayable` | `uint256` | `uint256` |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getAddr(uint256 _regId)` | `view` | `address` | — |
| `getAddrDescription(uint256 _regId)` | `view` | `string` | — |
| `getAddrInfo(uint256 _regId)` | `view` | `(address addr, uint256 version, uint256 lastModified, string description)` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getLastAddr()` | `view` | `address` | — |
| `getLastRegId()` | `view` | `uint256` | — |
| `getNumAddrs()` | `view` | `uint256` | — |
| `getRegId(address _addr)` | `view` | `uint256` | — |
| `getRegistryDescription()` | `view` | `string` | — |
| `getRipeHq()` | `view` | `address` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `isPaused()` | `view` | `bool` | — |
| `isValidAddr(address _addr)` | `view` | `bool` | — |
| `isValidAddressDisable(uint256 _regId)` | `view` | `bool` | — |
| `isValidAddressUpdate(uint256 _regId, address _newAddr)` | `view` | `bool` | — |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidNewAddress(address _addr)` | `view` | `bool` | — |
| `isValidRegId(uint256 _regId)` | `view` | `bool` | — |
| `isValidRegistryTimeLock(uint256 _numBlocks)` | `view` | `bool` | — |
| `isVaultBookAddr(address _addr)` | `view` | `bool` | `bool` |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `maxRegistryTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `minRegistryTimeLock()` | `view` | `uint256` | — |
| `mintRipeForStabPoolClaims(uint256 _amount, address _ripeToken, address _ledger)` | `nonpayable` | `bool` | `bool` |
| `numAddrs()` | `view` | `uint256` | — |
| `numGovChanges()` | `view` | `uint256` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `pendingAddrDisable(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingAddrUpdate(uint256 arg0)` | `view` | `(address newAddr, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingNewAddr(address arg0)` | `view` | `(string description, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `registryChangeTimeLock()` | `view` | `uint256` | — |
| `relinquishGov()` | `nonpayable` | — | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setRegistryTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setRegistryTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setRegistryTimeLockAfterSetup(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `startAddNewAddressToRegistry(address _addr, string _description)` | `nonpayable` | `bool` | `bool` |
| `startAddressDisableInRegistry(uint256 _regId)` | `nonpayable` | `bool` | `bool` |
| `startAddressUpdateToRegistry(uint256 _regId, address _newAddr)` | `nonpayable` | `bool` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `AddressDisableCancelled` | `uint256 regId, string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressDisableConfirmed` | `uint256 regId, string description, address addr indexed, uint256 version, string registry` |
| `AddressDisablePending` | `uint256 regId, string description, address addr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `AddressUpdateCancelled` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `AddressUpdateConfirmed` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, string registry` |
| `AddressUpdatePending` | `uint256 regId, string description, address newAddr indexed, address prevAddr indexed, uint256 version, uint256 confirmBlock, string registry` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `NewAddressCancelled` | `string description, address addr indexed, uint256 initiatedBlock, uint256 confirmBlock, string registry` |
| `NewAddressConfirmed` | `address addr indexed, uint256 regId, string description, string registry` |
| `NewAddressPending` | `address addr indexed, string description, uint256 confirmBlock, string registry` |
| `RegistryTimeLockModified` | `uint256 newTimeLock, uint256 prevTimeLock, string registry` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `insufficient rewards`
- `invalid ledger`
- `invalid ripe token`
- `no perms`
- `not stab vault`
- `vault has funds`

<!-- END GENERATED API REFERENCE: VaultBook -->
