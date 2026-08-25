# VaultMigrator

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/VaultMigrator.vy)

## Purpose and authority

`VaultMigrator` moves protocol-custodied positions between registered vault implementations while preserving balances and related accounting. Every migration entry point is Switchboard-only. The contract is a lifecycle tool, not a user-facing transfer route, and it must itself be unpaused.

Ordinary and RipeGov migrations use Teller's migration-only custody paths, which are callable only by VaultMigrator and require the route-specific pause state.

## Ordinary vault migration

`migrateVaultPositions` enumerates registered assets for up to 25 users but
skips a source position when the target does not support that asset.
`migrateVaultPositionsForUserByAssets` is the strict alternative: every
selected position must exist and be supported by the target or the call
reverts.

Teller must be paused for its ordinary migration custody routes. The source and target must be different registered vaults, both unpaused, and must have matching Stability-vault classification. Neither may be a current or historical RipeGov vault. The target must support the asset being imported.

For every asset actually selected for movement, VaultMigrator snapshots the
source position, withdraws through the migration route, verifies exact custody
and source depletion, deposits into the target, and verifies the resulting
position. Asset-list and housekeeping state are updated as part of the
migration.

## RipeGov migration

`migrateRipeGovPositions` and `migrateRipeGovPositionsForUserByAssets` move
recognized RipeGov positions into MissionControl's current
`coreRipeGovVaultId`. The enumerated form skips positions unsupported by the
target; the explicit-asset form requires every selected position and target
route. Both require Teller, the source RipeGov vault, and the target RipeGov
vault to be paused. The source must differ from the target and must not be the
immutable legacy vault handled by the dedicated Base route.

In addition to token amounts, the migration preserves governance-specific state including points, unlock information, last lock terms, and the user's point-accrual disable state. The target position must be empty before import, and the source position must be fully exported.

Current and historical RipeGov roles are resolved through MissionControl. The normal route does not hardcode a numeric current vault ID.

## Legacy Base RipeGov route

`migrateLegacyRipeGovPositions` is a special compatibility path. It is enabled
only on Base (`chain.id == 8453`) when the immutable legacy vault address was
supplied at construction. It verifies that this address is the registered
legacy source, requires the legacy source to be unpaused, and requires Teller
and the current target RipeGov vault to be paused.

This exceptional route reflects the operational constraints of the historical vault. It must not be generalized into a claim that all RipeGov migrations use an unpaused source or a fixed vault ID.

## Bounds

- at most 25 users per batch;
- at most 20 explicit assets;
- at most 20 registered assets per ordinary user enumeration;
- at most 20 registered RipeGov asset slots for each user in an enumerated
  migration; and
- at most 20 registered RipeGov asset slots in aggregate across all nonzero
  user rows in either the current/historical RipeGov batch or the legacy Base
  batch.

The RipeGov batch limits count registered slots, not only nonzero, supported, or
ultimately migrated positions. Both per-user and aggregate counts are checked
for the entire batch before the first position is mutated. The explicit
`migrateRipeGovPositionsForUserByAssets` route is instead limited to one user
and a caller-supplied list of at most 20 assets; it is not a way to enlarge the
cross-user enumerated batch.

Callers must use the explicit-asset method when bounded enumeration is not valid
or when the operation must fail rather than skip an unsupported selected asset.

## Security properties

- Switchboard-only authority and explicit pause-state gates make migration an operationally coordinated action.
- Exact token deltas, source depletion, target import, Teller residue, and allowance cleanup are verified.
- Lootbox and Ledger checkpoints keep reward and membership state aligned with the moved position.
- Source/target registration, asset support, vault classification, and special legacy identity are revalidated on-chain.

<!-- BEGIN GENERATED API REFERENCE: VaultMigrator -->
## Exact API reference

> Generated from `contracts/core/VaultMigrator.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, bool _shouldPause, address _legacyRipeGovVault)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | — |
| `migrateLegacyRipeGovPositions(address[] _users)` | `nonpayable` | `uint256` | `uint256` |
| `migrateRipeGovPositions(address[] _users, uint256 _sourceVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateRipeGovPositionsForUserByAssets(address _user, address[] _assets, uint256 _sourceVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateVaultPositions(address[] _users, uint256 _sourceVaultId, uint256 _targetVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateVaultPositionsForUserByAssets(address _user, address[] _assets, uint256 _sourceVaultId, uint256 _targetVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `LegacyRipeGovPositionMigrationExecuted` | `address user indexed, address asset indexed, uint256 amount, uint256 targetShares, uint256 govPoints, uint256 unlock` |
| `RipeGovPositionMigrationExecuted` | `address user indexed, address asset indexed, uint256 sourceVaultId, uint256 targetVaultId, address sourceVault, address targetVault, uint256 amount, uint256 targetShares, uint256 govPoints, uint256 unlock` |
| `RipeGovUserPointAccrualDisableInherited` | `address user indexed, address sourceVault indexed, address targetVault indexed, uint256 disabledBlock` |
| `VaultPositionMigrationExecuted` | `address user indexed, address asset indexed, uint256 sourceVaultId, uint256 targetVaultId, uint256 amount` |

### Structs declared by this source

- `GovData(govPoints: uint256, lastShares: uint256, lastPointsUpdate: uint256, unlock: uint256, lastTerms: cs.LockTerms)`
- `PrevSourceSnapshot(sourceShares: uint256, sourceAmount: uint256, govPoints: uint256, unlock: uint256, lastTerms: cs.LockTerms)`
- `LegacyMigrationPosition(asset: address, sourceSnapshot: PrevSourceSnapshot)`
- `RipeGovMigrationData(amount: uint256, govPoints: uint256, unlock: uint256, lastTerms: cs.LockTerms)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `contract paused`
- `duplicate asset`
- `inexact migration deposit`
- `inexact migration receipt`
- `invalid asset`
- `invalid legacy vault`
- `invalid migration amount`
- `invalid migration receipt`
- `invalid migration result`
- `invalid source vault`
- `invalid source vault id`
- `invalid target vault`
- `invalid target vault id`
- `invalid user`
- `invalid vault id`
- `legacy migration disabled`
- `legacy user asset capacity exceeded`
- `migration amount mismatch`
- `no migrations`
- `no source position`
- `only switchboard allowed`
- `same vault`
- `source amount remains`
- `source balance remains`
- `source is not ripe gov`
- `source is ripe gov`
- `source position not depleted`
- `source shares remain`
- `source vault balance remains`
- `source vault not paused`
- `source vault paused`
- `stab vault mismatch`
- `target asset not registered`
- `target global total mismatch`
- `target is ripe gov`
- `target last shares mismatch`
- `target last update mismatch`
- `target ledger missing`
- `target points mismatch`
- `target position missing`
- `target shares mismatch`
- `target terms mismatch`
- `target unlock mismatch`
- `target user disable missing`
- `target user total mismatch`
- `target vault balance remains`
- `target vault not paused`
- `target vault paused`
- `teller allowance residue`
- `teller balance remains`
- `teller balance residue`
- `teller not paused`
- `too many migration asset slots`
- `unsupported target asset`
- `use explicit asset migration`
- `use legacy ripe gov migration`

<!-- END GENERATED API REFERENCE: VaultMigrator -->
