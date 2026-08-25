# Addys

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/modules/Addys.vy)

`Addys` is the shared address-resolution module used by Ripe contracts. It binds
an implementation to one immutable `RipeHq` and resolves protocol components
from that registry when they are needed.

## Registry IDs

The module reserves the following `RipeHq` IDs as protocol routing identifiers.

| ID | Component |
| ---: | --- |
| 1 | Green token |
| 2 | Savings Green |
| 3 | RIPE token |
| 4 | Ledger |
| 5 | MissionControl |
| 6 | Switchboard registry |
| 7 | PriceDesk |
| 8 | VaultBook |
| 9 | AuctionHouse |
| 10 | AuctionHouseNFT |
| 11 | Boardroom |
| 12 | BondRoom |
| 13 | CreditEngine |
| 14 | Endaoment |
| 15 | HumanResources |
| 16 | Lootbox |
| 17 | Teller |
| 18 | Deleverage |
| 19 | CreditRedeem |
| 20 | TellerUtils |
| 21 | EndaomentFunds |
| 22 | EndaomentPSM |
| 23 | RIPE CCIP pool |
| 24 | GREEN CCIP pool |
| 25 | VaultMigrator |
| 26 | RipeReserveEngine |
| 27 | RipeReserveVesting |

IDs 23 and 24 are reserved constants but are not fields in the `Addys` cache
struct. VaultMigrator, RipeReserveEngine, and RipeReserveVesting have explicit
internal ID/address helpers for IDs 25, 26, and 27, respectively.

## Resolution model

- `RIPE_HQ_FOR_ADDYS` is immutable and must be nonzero at construction.
- `getAddys()` builds a fresh `Addys` struct from the current addresses at IDs
  1 through 17.
- `_getAddys(cached)` returns the caller-supplied struct unchanged when its `hq`
  field is nonzero; otherwise it regenerates the struct. A caller that supplies
  a cache is responsible for its provenance and freshness.
- Component-specific internal helpers call `RipeHq.getAddr(id)` directly. An
  unregistered or disabled ID therefore resolves to the zero address.

## Authority helpers

`_isValidRipeAddr` accepts an address only when it is currently registered in
one of three places:

1. the root `RipeHq` registry;
2. the current `VaultBook` registry; or
3. the current `Switchboard` registry.

It is a current-membership test, not a historical-membership test.
`_isSwitchboardAddr` is narrower and accepts only a currently registered
Switchboard configuration contract. Modules such as `DeptBasics` use this to
authorize pause and recovery operations.

These helpers are typed-call checks, not universally fail-closed boolean
probes. A zero VaultBook or Switchboard registry pointer is skipped (and a zero
Switchboard pointer makes `_isSwitchboardAddr` return `false`), but a nonzero
pointer whose target lacks or malforms the expected interface can make the
typed call revert instead of returning `false`. The same boundary applies to
the immutable RipeHq target used by address resolution.

## Integration cautions

- Fixed IDs are part of the protocol's routing convention. Repointing or
  disabling an ID changes what all resolving contracts see.
- The `Addys` struct intentionally stops at Teller. Newer departments must use
  their dedicated internal helpers or query `RipeHq` explicitly.
- Address resolution is separate from configuration authority: being registered
  does not by itself grant minting, blacklist, vault-reward, or lite-action
  permissions.

<!-- BEGIN GENERATED API REFERENCE: Addys -->
## Exact API reference

> Generated from `contracts/modules/Addys.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | `Addys` |
| `getRipeHq()` | `view` | `address` | `address` |

### Structs declared by this source

- `Addys(hq: address, greenToken: address, savingsGreen: address, ripeToken: address, ledger: address, missionControl: address, switchboard: address, priceDesk: address, vaultBook: address, auctionHouse: address, auctionHouseNft: address, boardroom: address, bondRoom: address, creditEngine: address, endaoment: address, humanResources: address, lootbox: address, teller: address)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `invalid ripe hq`

<!-- END GENERATED API REFERENCE: Addys -->
