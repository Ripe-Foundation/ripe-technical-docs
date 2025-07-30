# Ripe Protocol Technical Documentation

For deployed contract addresses on Base Mainnet, see [Deployments](Deployments.md). To see our full source code, check out our [GitHub](https://github.com/Ripe-Foundation/ripe-protocol).


## Overview  

Ripe Protocol is an onchain credit layer that turns **any tokenized asset—crypto‑native *or* real‑world**—into both a yield source *and* instant liquidity.  

Users deposit assets that keep earning through external strategies **plus** Ripe’s Endaoment, then draw a **single GREEN loan** against their diversified portfolio—no order books, no counterparties, predictable rates. Governance, driven by RIPE tokens and dynamic committee voting, steers risk, monetary policy and treasury allocations, giving the community full ownership of the protocol’s economics.

### Key Features  

| Feature | Why it matters |
|---------|----------------|
| **Earn Yield on Anything** | The Endaoment reinvests all protocol revenues and Bonding proceeds, distributing sustainable yield (and RIPE incentives) even to idle NFTs or tokenized RWAs. |
| **One‑Loan‑for‑All Collateral** | Aggregate every deposit—stablecoins, LP tokens, NFTs, houses—to back a *single* GREEN debt position, slashing liquidation risk and UX friction. |
| **GREEN Stablecoin & Multi‑Layer Peg Defense** | Dynamic interest, Stability Pool absorption, Endaoment redemptions and protocol‑owned liquidity keep GREEN fully‑backed and on‑peg. |
| **Compliance‑Ready RWA Support** | Whitelists and transfer‑restricted liquidation paths let regulated or permissioned assets participate safely. |
| **Counterparty‑Free, Predictable Borrowing** | Smart contracts mint GREEN directly—no lenders, no funding gaps, transparent terms. |
| **Resilient Liquidations** | Cascade of Stability Pool swaps + fungible/NFT auctions minimizes bad debt while rewarding backstops. |
| **Dynamic, Onchain Governance** | Continuous “Dynamic Voting,” elected committees and **Juice Score** incentives align risk, rewards and protocol evolution with token‑holder skin‑in‑the‑game. |

### Protocol Components

The protocol consists of several interconnected systems:
- **Core Lending**: Lending engine, user interface, liquidations, and stability pool
- **Treasury & Rewards**: Treasury management, bonding, rewards distribution, and contributor compensation
- **Governance & Control**: Access control, configuration management, and time-locked operations
- **Tokens**: GREEN (stablecoin), RIPE (governance), and sGREEN (yield-bearing GREEN)
- **Vaults**: Asset management strategies from simple storage to yield optimization
- **Pricing**: Multi-oracle integration for accurate and resilient asset valuations
- **Registries**: Central coordination points for vaults and addresses
- **Shared Modules**: Reusable components for address resolution and department operations

## Core Lending

Essential contracts for lending operations, liquidations, and user interactions.

| Contract | Description |
|----------|-------------|
| [CreditEngine.vy](core-lending/CreditEngine.md) | Lending powerhouse managing collateralized borrowing, interest accrual, and debt repayment |
| [Teller.vy](core-lending/Teller.md) | Primary user interface for deposits, withdrawals, borrowing, and account management |
| [Ledger.vy](core-lending/Ledger.md) | Comprehensive data storage for user positions, debt, and protocol metrics |
| [AuctionHouse.vy](core-lending/AuctionHouse.md) | Liquidation engine executing multi-phase strategies to recover value from under-collateralized positions |
| [StabilityPool.vy](core-lending/StabilityPool.md) | Insurance fund where stablecoin deposits earn discounted liquidated collateral |

## Treasury & Rewards

Treasury management, bonding mechanisms, and reward distribution systems.

| Contract | Description |
|----------|-------------|
| [Endaoment.vy](treasury-rewards/Endaoment.md) | Treasury and liquidity hub deploying funds across DeFi strategies while maintaining GREEN stability |
| [BondRoom.vy](treasury-rewards/BondRoom.md) | Decentralized bond marketplace for GREEN/RIPE exchanges with dynamic pricing based on treasury needs |
| [Lootbox.vy](treasury-rewards/Lootbox.md) | Rewards distribution engine calculating time-weighted points for RIPE token allocation |
| [HumanResources.vy](treasury-rewards/HumanResources.md) | On-chain payroll system managing contributor vesting schedules and token compensation |
| [Contributor.vy](treasury-rewards/Contributor.md) | Individual vesting contracts for contributor token compensation |
| [BondBooster.vy](treasury-rewards/BondBooster.md) | Dynamic discount mechanism for GREEN-to-RIPE bond conversions |

## Governance & Control

Access control, configuration management, and protocol governance systems.

| Contract | Description |
|----------|-------------|
| [RipeHq.vy](governance-control/RipeHq.md) | Master registry and governance hub controlling token minting permissions |
| [Switchboard.vy](governance-control/Switchboard.md) | Authorization gateway for all protocol configuration changes |
| [MissionControl.vy](governance-control/MissionControl.md) | Central configuration hub storing all operational parameters |
| [LocalGov.vy](governance-control/LocalGov.md) | Two-tier governance system for contract-specific operations |
| [TimeLock.vy](governance-control/TimeLock.md) | Time-delay mechanism for critical configuration changes |

### Configuration Contracts

| Contract | Description |
|----------|-------------|
| [SwitchboardAlpha.vy](governance-control/configuration/SwitchboardAlpha.md) | Asset and vault configuration including collateral parameters |
| [SwitchboardBravo.vy](governance-control/configuration/SwitchboardBravo.md) | Reward distribution and points system configuration |
| [SwitchboardCharlie.vy](governance-control/configuration/SwitchboardCharlie.md) | Protocol operations including deposits, withdrawals, and liquidations |
| [SwitchboardDelta.vy](governance-control/configuration/SwitchboardDelta.md) | HR, contributor management, and auxiliary feature configuration |

## Tokens

Protocol tokens for value transfer and governance.

| Contract | Description |
|----------|-------------|
| [GreenToken.vy](tokens/GreenToken.md) | USD-pegged stablecoin minted through overcollateralized positions |
| [RipeToken.vy](tokens/RipeToken.md) | Governance token for voting on protocol parameters and treasury |
| [SavingsGreen.vy](tokens/SavingsGreen.md) | Yield-bearing GREEN vault implementing ERC4626 standard |

### Token Modules

| Module | Description |
|--------|-------------|
| [Erc20Token.vy](tokens/modules/Erc20Token.md) | Enhanced ERC20 with blacklisting, pausability, and governance integration |
| [Erc4626Token.vy](tokens/modules/Erc4626Token.md) | Tokenized vault standard for yield-bearing tokens |

## Vaults

Modular vault implementations for different asset management strategies.

| Contract | Description |
|----------|-------------|
| [SimpleErc20.vy](vaults/SimpleErc20.md) | Basic vault with direct 1:1 balance tracking for standard ERC20 collateral |
| [RebaseErc20.vy](vaults/RebaseErc20.md) | Yield-optimized vault for rebase tokens like stETH with automatic compounding |
| [RipeGov.vy](vaults/RipeGov.md) | Governance vault where users lock RIPE tokens for voting power with time-based bonuses |

### Vault Modules

Reusable components that power vault functionality.

| Module | Description |
|--------|-------------|
| [BasicVault.vy](vaults/modules/BasicVault.md) | Foundational vault operations for deposits, withdrawals, and transfers |
| [SharesVault.vy](vaults/modules/SharesVault.md) | Share-based accounting for yield distribution and proportional ownership |
| [StabVault.vy](vaults/modules/StabVault.md) | Stability pool mechanics for liquidation absorption and reward distribution |
| [VaultData.vy](vaults/modules/VaultData.md) | Universal database layer for balance tracking and state management |

## Pricing

Oracle integrations and price aggregation for reliable asset valuations.

| Contract | Description |
|----------|-------------|
| [PriceDesk.vy](pricing/PriceDesk.md) | Oracle aggregator routing price requests through prioritized sources |
| [ChainlinkPrices.vy](pricing/ChainlinkPrices.md) | Integration with Chainlink's decentralized oracle network |
| [PythPrices.vy](pricing/PythPrices.md) | High-frequency pricing with Pyth Network's pull-based oracles |
| [StorkPrices.vy](pricing/StorkPrices.md) | Stork Network integration with nanosecond-precision timestamps |
| [CurvePrices.vy](pricing/CurvePrices.md) | Curve LP token pricing and GREEN stabilizer monitoring |
| [BlueChipYieldPrices.vy](pricing/BlueChipYieldPrices.md) | Specialized pricing for yield-bearing vault tokens with snapshot system |

### Pricing Modules

| Module | Description |
|--------|-------------|
| [PriceSourceData.vy](pricing/modules/PriceSourceData.md) | Base module defining standard interface for all price sources |

## Registries

Central coordination points for protocol components.

| Contract | Description |
|----------|-------------|
| [VaultBook.vy](registries/VaultBook.md) | Central registry of approved vaults with safety checks and RIPE reward distribution |
| [AddressRegistry.vy](registries/AddressRegistry.md) | Flexible registry for managing protocol addresses with time-locks |

## Shared Modules

Reusable components providing common functionality across the protocol.

| Module | Description |
|--------|-------------|
| [Addys.vy](shared-modules/Addys.md) | Centralized address resolution providing validated protocol addresses |
| [DeptBasics.vy](shared-modules/DeptBasics.md) | Base functionality for protocol departments including pause controls |

---

## Getting Started

1. **New Users**: Start with [Teller.vy](core-lending/Teller.md) to understand user interactions
2. **Developers**: Review [RipeHq.vy](governance-control/RipeHq.md) for protocol architecture
3. **Governance**: Explore [RipeToken.vy](tokens/RipeToken.md) and [RipeGov.vy](vaults/RipeGov.md)
4. **Integrators**: Check [PriceDesk.vy](pricing/PriceDesk.md) and vault interfaces

## Architecture Principles

- **Modular Design**: Reusable modules reduce code duplication and audit surface
- **Registry Pattern**: Central registries coordinate decentralized components
- **Time-Locked Changes**: Critical updates require delays to prevent rushed decisions
- **Multi-Oracle Support**: No single point of failure for price feeds
- **Layered Security**: Multiple validation layers from modules to registries to core contracts