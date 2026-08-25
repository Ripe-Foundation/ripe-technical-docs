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
first-party source file; inherited Chainlink members are described separately.

Start with:

- [Protocol architecture and behavior](CurrentImplementation.md) for the
  cross-contract system map and important state machines;
- [Integration guide](guides/IntegratorOnRamp.md) for common reads and
  transaction flows; and
- the [table of contents](SUMMARY.md) for every contract and interface page.

## Architecture

Users interact through `Teller`, which routes deposits, withdrawals, borrowing,
repayment, claims, bonds, liquidations, and other account actions. Vaults hold
or account for assets, `VaultBook` records registered vaults, and
`MissionControl` preserves historical Stability and RipeGov vault-role
classifications. `CreditEngine` evaluates account-wide collateral, debt, and
liquidation eligibility; `Ledger` stores shared position, debt, and action state.

`PriceDesk` resolves prices through qualified source contracts. Liquidation and
debt resolution are split across `StabilityPool`, `AuctionHouse`,
`CreditRedeem`, and `Deleverage`, each with distinct eligibility and settlement
rules. `VaultMigrator` provides controlled position migration between compatible
vaults.

`RipeHq`, `MissionControl`, `Switchboard`, and the specialized switchboards
provide address resolution, authority, and configuration. Treasury contracts
cover bonds, rewards, contributor compensation, Endaoment operations, and the
PSM. Token and vault modules provide the shared custody and accounting
primitives used by the composed contracts.

## Component groups

| Group | Responsibility |
| --- | --- |
| [Core](core/CreditEngine.md) | Credit, debt, user entry points, liquidation, redemption, deleveraging, migration, and stability |
| [Core modules](core-modules/Addys.md) | Address resolution, department behavior, vault registration, and shared state routing |
| [Governance](governance/RipeHq.md) | Authority, timelocks, protocol configuration, defaults, and role rotation |
| [Treasury](treasury/Endaoment.md) | Endaoment operations, bonds, rewards, contributor compensation, and the PSM |
| [Tokens](tokens/GreenToken.md) | GREEN, RIPE, sGREEN, ERC-20 behavior, and ERC-4626 behavior |
| [Vaults](vaults/SimpleErc20.md) | Direct custody, share accounting, Stability Pool state, and RIPE governance positions |
| [Pricing](pricing/PriceDesk.md) | Price routing, oracle adapters, yield-token pricing, Curve pricing, and monitoring sources |
| [Interfaces](interfaces/ConfigStructs.md) | Shared first-party Vyper interfaces and configuration types |
| [Cross-chain](cross-chain/RipeCcipBurnMintTokenPools.md) | First-party Solidity CCIP burn/mint pool implementations |

`AuctionHouseNFT` and `Boardroom` are documented because first-party contract
sources exist. `AuctionHouseNFT` supplies only inherited department
behavior, and `Boardroom` implements only the governance-power-change callback
described on its component page.

## Validate this documentation

The exact API blocks are generated from a commit-and-tree-pinned protocol
baseline. From this repository, check API parity against a local protocol clone
and then validate links, headings, fences, and navigation:

```sh
python3 scripts/sync_api_reference.py \
  --protocol-repo /path/to/ripe-protocol \
  --check
python3 scripts/check_markdown.py
```

CI also recompiles the production Vyper ABIs and checks them against the
tracked artifacts before validating the generated reference blocks.

## Other resources

- [Ripe user documentation](https://docs.ripe.finance/) covers product concepts
  and user-facing guidance.
- [Ripe Protocol source](https://github.com/Ripe-Foundation/ripe-protocol)
  hosts the implementation.
- [Ripe Params](https://params.ripe.finance/) publishes current addresses and
  configuration.
