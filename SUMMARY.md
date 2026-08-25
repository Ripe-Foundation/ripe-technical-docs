# Table of contents

- [Technical documentation](README.md)
- [Protocol architecture and contract behavior](CurrentImplementation.md)
- [Integration guide](guides/IntegratorOnRamp.md)

## Core

- [CreditEngine](core/CreditEngine.md)
- [Teller](core/Teller.md)
- [TellerUtils](core/TellerUtils.md)
- [Ledger](core/Ledger.md)
- [AuctionHouse](core/AuctionHouse.md)
- [AuctionHouseNFT](core/AuctionHouseNFT.md)
- [Boardroom](core/Boardroom.md)
- [StabilityPool](core/StabilityPool.md)
- [CreditRedeem](core/CreditRedeem.md)
- [Deleverage](core/Deleverage.md)
- [VaultMigrator](core/VaultMigrator.md)
- [RipeReserveEngine](core/RipeReserveEngine.md)
- [RipeReserveVesting](core/RipeReserveVesting.md)

## Core modules

- [Addys](core-modules/Addys.md)
- [AddressRegistry](core-modules/AddressRegistry.md)
- [DeptBasics](core-modules/DeptBasics.md)
- [VaultBook](core-modules/VaultBook.md)

## Governance

- [RipeHq](governance/RipeHq.md)
- [Switchboard](governance/Switchboard.md)
- [MissionControl](governance/MissionControl.md)
- [LocalGov](governance/LocalGov.md)
- [TimeLock](governance/TimeLock.md)
- [TrainingWheels](governance/TrainingWheels.md)

- Configuration switchboards
  - [SwitchboardAlpha](governance/configuration/SwitchboardAlpha.md)
  - [SwitchboardBravo](governance/configuration/SwitchboardBravo.md)
  - [SwitchboardCharlie](governance/configuration/SwitchboardCharlie.md)
  - [SwitchboardDelta](governance/configuration/SwitchboardDelta.md)
  - [SwitchboardEcho](governance/configuration/SwitchboardEcho.md)
  - [SwitchboardFoxtrot](governance/configuration/SwitchboardFoxtrot.md)
- Defaults seed profiles
  - [DefaultsBase](governance/configuration/DefaultsBase.md)
  - [DefaultsBaseLive](governance/configuration/DefaultsBaseLive.md)
  - [DefaultsRobinhood](governance/configuration/DefaultsRobinhood.md)
  - [DefaultsRobinhoodLive](governance/configuration/DefaultsRobinhoodLive.md)
  - [DefaultsLocal](governance/configuration/DefaultsLocal.md)

## Treasury

- [Endaoment](treasury/Endaoment.md)
- [EndaomentFunds](treasury/EndaomentFunds.md)
- [EndaomentPSM](treasury/EndaomentPSM.md)
- [BondRoom](treasury/BondRoom.md)
- [BondBooster](treasury/BondBooster.md)
- [Lootbox](treasury/Lootbox.md)
- [HumanResources](treasury/HumanResources.md)
- [Contributor](treasury/Contributor.md)

## Tokens

- [GreenToken](tokens/GreenToken.md)
- [RipeToken](tokens/RipeToken.md)
- [SavingsGreen](tokens/SavingsGreen.md)
- Token modules
  - [Erc20Token](tokens/modules/Erc20Token.md)
  - [Erc4626Token](tokens/modules/Erc4626Token.md)

## Vaults

- [SimpleErc20](vaults/SimpleErc20.md)
- [RebaseErc20](vaults/RebaseErc20.md)
- [RipeGov](vaults/RipeGov.md)
- Vault modules
  - [BasicVault](vaults/modules/BasicVault.md)
  - [SharesVault](vaults/modules/SharesVault.md)
  - [StabVault](vaults/modules/StabVault.md)
  - [VaultData](vaults/modules/VaultData.md)

## Pricing

- [PriceDesk](pricing/PriceDesk.md)
- [ChainlinkPrices](pricing/ChainlinkPrices.md)
- [PythPrices](pricing/PythPrices.md)
- [RedStone](pricing/RedStone.md)
- [StorkPrices](pricing/StorkPrices.md)
- [CurvePrices](pricing/CurvePrices.md)
- [BlueChipYieldPrices](pricing/BlueChipYieldPrices.md)
- [UndyVaultPrices](pricing/UndyVaultPrices.md)
- [wsuperOETHbPrices](pricing/wsuperOETHbPrices.md)
- [AeroRipePrices](pricing/AeroRipePrices.md)
- [UniswapV2Prices](pricing/UniswapV2Prices.md)
- Pricing modules
  - [PriceSourceData](pricing/modules/PriceSourceData.md)

## Interfaces

- [ConfigStructs](interfaces/ConfigStructs.md)
- [Defaults](interfaces/Defaults.md)
- [Department](interfaces/Department.md)
- [PriceSource](interfaces/PriceSource.md)
- [UndyLego](interfaces/UndyLego.md)
- [Vault](interfaces/Vault.md)

## Cross-chain

- [RIPE and GREEN CCIP burn/mint pools](cross-chain/RipeCcipBurnMintTokenPools.md)
- [Configurable-capability CCIP pool](cross-chain/RipeTokenPool.md)
- [BurnMintTokenPool 1.5.1 inherited API](cross-chain/BurnMintTokenPool151.md)

## External resources

- [Ripe Params](Deployments.md)
- [Current deployment addresses](https://params.ripe.finance/?tab=deployments)
- [Ripe Protocol source](https://github.com/Ripe-Foundation/ripe-protocol)
- [Ripe user documentation](https://docs.ripe.finance/)
