# Ripe Protocol technical documentation

Ripe is a modular, overcollateralized credit protocol that turns supported
vault assets into one account-wide GREEN credit position. These docs describe
the protocol's first-party smart contracts: their responsibilities, state
transitions, permissions, functions, arguments, return values, events, and
integration behavior.

## Documentation scope

This repository is an evergreen description of the contract system. It does
not catalog deployment addresses, enabled features, selected governance
parameters, asset listings, or other runtime configuration. Those values change
without changing the contracts and are published separately in
[Ripe Params](https://params.ripe.finance/).

The component pages pair behavioral explanations with generated API
inventories. Vyper inventories use tracked ABIs where available and source
declarations otherwise. Solidity inventories cover declarations written in the
first-party source file; inherited Chainlink members are generated separately
from a compiled, hash-pinned composed ABI.

Start with:

- [Protocol architecture and behavior](CurrentImplementation.md) for the
  cross-contract system map and important state machines;
- [Integration guide](guides/IntegratorOnRamp.md) for common reads and
  transaction flows; and
- the [table of contents](SUMMARY.md) for every contract and interface page.

Maintainers can use the
[contributor-only baseline guide](https://github.com/Ripe-Foundation/ripe-technical-docs/blob/master/reference/ImplementationBaseline.md)
to reproduce and advance the exact protocol-source pin. It is intentionally
kept outside the published GitBook navigation.

## Architecture

Most account and vault actions enter through `Teller`, which routes deposits,
withdrawals, borrowing, repayment, Stability claims, bonds, liquidations, and
other account actions. Vaults hold or account for assets, `VaultBook` records
registered vaults, and
`MissionControl` preserves historical Stability and RipeGov vault-role
classifications. `CreditEngine` evaluates account-wide collateral, debt, and
liquidation eligibility; `Ledger` stores shared position, debt, and action state.

`PriceDesk` resolves prices through qualified source contracts. Liquidation and
debt resolution are split across `StabilityPool`, `AuctionHouse`,
`CreditRedeem`, and `Deleverage`, each with distinct eligibility and settlement
rules. `VaultMigrator` provides controlled position migration between compatible
vaults.

[`RipeReserveEngine`](core/RipeReserveEngine.md) is a separate direct user
surface: it accepts a configured payment asset and creates block-based RIPE
allocations in [`RipeReserveVesting`](core/RipeReserveVesting.md). Vested claims
either mint RIPE directly to the beneficiary or route it through Teller into
MissionControl's current core RipeGov vault.

`RipeHq`, `MissionControl`, `Switchboard`, and the specialized switchboards
provide address resolution, authority, and configuration. Treasury contracts
cover bonds, rewards, contributor compensation, Endaoment operations, and the
PSM. Token and vault modules provide the shared custody and accounting
primitives used by the composed contracts.

## Component groups

| Group | Responsibility |
| --- | --- |
| [Core](core/CreditEngine.md) | Credit, debt, user entry points, liquidation, redemption, deleveraging, migration, stability, reserve acquisition, and reserve vesting |
| [Core modules](core-modules/Addys.md) | Address resolution, department behavior, vault registration, and shared state routing |
| [Governance](governance/RipeHq.md) | Authority, timelocks, protocol configuration, defaults, and role rotation |
| [Treasury](treasury/Endaoment.md) | Endaoment operations, bonds, rewards, contributor compensation, and the PSM |
| [Tokens](tokens/GreenToken.md) | GREEN, RIPE, sGREEN, ERC-20 behavior, and ERC-4626 behavior |
| [Vaults](vaults/SimpleErc20.md) | Direct custody, share accounting, Stability Pool state, and RIPE governance positions |
| [Pricing](pricing/PriceDesk.md) | Price routing, oracle adapters, yield-token pricing, Curve pricing, and monitoring sources |
| [Interfaces](interfaces/ConfigStructs.md) | Shared first-party Vyper interfaces and configuration types |
| [Cross-chain](cross-chain/RipeCcipBurnMintTokenPools.md) | First-party Solidity CCIP burn/mint pool implementations |

`AuctionHouseNFT` and `Boardroom` are documented because first-party contract
sources exist. `AuctionHouseNFT` supplies only inherited department behavior,
and `Boardroom` implements only the governance-power-change callback described
on its component page.

## Validate this documentation

The exact API blocks are generated from a commit-and-tree-pinned protocol
baseline. From this repository, check API parity against a local protocol clone
and then run tooling, link, heading, fence, and navigation checks:

```sh
protocol_repo=/path/to/ripe-protocol
forge build --root "$protocol_repo/solidity" --force --skip test
python3 scripts/sync_api_reference.py \
  --protocol-repo "$protocol_repo" \
  --compiled-artifact-root "$protocol_repo" \
  --check
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/check_markdown.py
```

CI also recompiles the production Vyper ABIs and the composed Solidity ABI,
then checks them against the tracked artifacts before validating the generated
reference blocks.

## Other resources

- [Ripe user documentation](https://docs.ripe.finance/) covers product concepts
  and user-facing guidance.
- [Ripe Protocol source](https://github.com/Ripe-Foundation/ripe-protocol)
  hosts the implementation.
- [Ripe Params](https://params.ripe.finance/?tab=deployments) publishes current
  addresses and live configuration.
