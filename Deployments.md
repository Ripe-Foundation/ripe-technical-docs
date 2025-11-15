# Deployed Contracts

This document contains all deployed contract addresses for the Ripe Protocol on Base Mainnet, organized by functional category.

## Tokens

### Core Tokens

| Contract                                | Address                                                                                                               | Description                 |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| [Green Token](tokens/GreenToken.md)     | [0xd1Eac76497D06Cf15475A5e3984D5bC03de7C707](https://basescan.org/address/0xd1Eac76497D06Cf15475A5e3984D5bC03de7C707) | USD-pegged stablecoin       |
| [Ripe Token](tokens/RipeToken.md)       | [0x2A0a59d6B975828e781EcaC125dBA40d7ee5dDC0](https://basescan.org/address/0x2A0a59d6B975828e781EcaC125dBA40d7ee5dDC0) | Governance token            |
| [Savings Green](tokens/SavingsGreen.md) | [0xaa0f13488CE069A7B5a099457c753A7CFBE04d36](https://basescan.org/address/0xaa0f13488CE069A7B5a099457c753A7CFBE04d36) | Interest-bearing stablecoin |

## Core Lending

| Contract                                        | Address                                                                                                               | Description                  |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| [Credit Engine](core-lending/CreditEngine.md)   | [0xf9111dFcAbf2538D6ED9057C07e18bc14AC8DA6a](https://basescan.org/address/0xf9111dFcAbf2538D6ED9057C07e18bc14AC8DA6a) | Lending and borrowing engine |
| Credit Redeem                                   | [0x3bfB0F72642aeFA2486da00Db855c5F0b787e3FB](https://basescan.org/address/0x3bfB0F72642aeFA2486da00Db855c5F0b787e3FB) | Redemptions engine           |
| Deleverage                                      | [0x9cE3f44E3796353825091317E09Cfc0d27C76F61](https://basescan.org/address/0x9cE3f44E3796353825091317E09Cfc0d27C76F61) | Deleverage engine            |
| [Teller](core-lending/Teller.md)                | [0xae87deB25Bc5030991Aa5E27Cbab38f37a112C13](https://basescan.org/address/0xae87deB25Bc5030991Aa5E27Cbab38f37a112C13) | User interaction gateway     |
| Teller Utils                                    | [0x57f071AB96D1798C6bB3e314D2D283502DEDDcdD](https://basescan.org/address/0x57f071AB96D1798C6bB3e314D2D283502DEDDcdD) | Helper                       |
| [Ledger](core-lending/Ledger.md)                | [0x365256e322a47Aa2015F6724783F326e9B24fA47](https://basescan.org/address/0x365256e322a47Aa2015F6724783F326e9B24fA47) | Protocol data storage        |
| [Auction House](core-lending/AuctionHouse.md)   | [0x38FB9baB5024CA717254b274D3D71CF1bfA07312](https://basescan.org/address/0x38FB9baB5024CA717254b274D3D71CF1bfA07312) | Liquidation auctions         |
| [Stability Pool](core-lending/StabilityPool.md) | [0x2a157096af6337b2b4bd47de435520572ed5a439](https://basescan.org/address/0x2a157096af6337b2b4bd47de435520572ed5a439) | Liquidation backstop vault   |

## Treasury & Rewards

| Contract                                              | Address                                                                                                               | Description                  |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| [Endaoment](treasury-rewards/Endaoment.md)            | [0x14F4f1CD5F4197DB7cB536B282fe6c59eACfE40d](https://basescan.org/address/0x14F4f1CD5F4197DB7cB536B282fe6c59eACfE40d) | Treasury yield strategies    |
| [Bond Room](treasury-rewards/BondRoom.md)             | [0xe2E1a03b95B8E8EFEB6eFbAD52172488FF8C84A6](https://basescan.org/address/0xe2E1a03b95B8E8EFEB6eFbAD52172488FF8C84A6) | RIPE bond sales              |
| [Bond Booster](treasury-rewards/BondBooster.md)       | [0xA1872467AC4fb442aeA341163A65263915ce178a](https://basescan.org/address/0xA1872467AC4fb442aeA341163A65263915ce178a) | Bond purchase incentives     |
| [Lootbox](treasury-rewards/Lootbox.md)                | [0xef52d8a4732b96b98A0Bd47a69beFb40CdCF2515](https://basescan.org/address/0xef52d8a4732b96b98A0Bd47a69beFb40CdCF2515) | Rewards distribution         |
| [Human Resources](treasury-rewards/HumanResources.md) | [0xF9aCDFd0d167b741f9144Ca01E52FcdE16BE108b](https://basescan.org/address/0xF9aCDFd0d167b741f9144Ca01E52FcdE16BE108b) | Contributor management       |
| [Contributor](treasury-rewards/Contributor.md)        | [0x4965578D80E54b5EbE3BB5D7b1B3E0425559C1D1](https://basescan.org/address/0x4965578D80E54b5EbE3BB5D7b1B3E0425559C1D1) | Contributor vesting template |

## Governance & Control

| Contract                                                | Address                                                                                                               | Description             |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| [Ripe Hq](governance-control/RipeHq.md)                 | [0x6162df1b329E157479F8f1407E888260E0EC3d2b](https://basescan.org/address/0x6162df1b329E157479F8f1407E888260E0EC3d2b) | Central governance hub  |
| [Mission Control](governance-control/MissionControl.md) | [0xB59b84B526547b6dcb86CCF4004d48E619156CF3](https://basescan.org/address/0xB59b84B526547b6dcb86CCF4004d48E619156CF3) | Protocol configuration  |
| [Switchboard](governance-control/Switchboard.md)        | [0xc68A90A40B87ae1dABA93Da9c02642F8B74030F9](https://basescan.org/address/0xc68A90A40B87ae1dABA93Da9c02642F8B74030F9) | Configuration authority |

### Switchboard Managers

| Contract                                                                      | Address                                                                                                               | Description      |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------- |
| [Switchboard Alpha](governance-control/configuration/SwitchboardAlpha.md)     | [0x4EEc14F2905ec6bCfE9f399b90c1b92128B0AF8B](https://basescan.org/address/0x4EEc14F2905ec6bCfE9f399b90c1b92128B0AF8B) | Config manager A |
| [Switchboard Bravo](governance-control/configuration/SwitchboardBravo.md)     | [0xD18AC028cBe1AbebDb118E9C7A60018d58C846e7](https://basescan.org/address/0xD18AC028cBe1AbebDb118E9C7A60018d58C846e7) | Config manager B |
| [Switchboard Charlie](governance-control/configuration/SwitchboardCharlie.md) | [0xaEb344EAE3be9D1e8164E7fE3AcE3e496125403b](https://basescan.org/address/0xaEb344EAE3be9D1e8164E7fE3AcE3e496125403b) | Config manager C |
| [Switchboard Delta](governance-control/configuration/SwitchboardDelta.md)     | [0x50e815AC356798E42EB35De538a0376459ce11cb](https://basescan.org/address/0x50e815AC356798E42EB35De538a0376459ce11cb) | Config manager D |

## Pricing

| Contract                                                | Address                                                                                                               | Description                                 |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| [Price Desk](pricing/PriceDesk.md)                      | [0xDFe8D79bc05420a3fFa14824135016a738eE8299](https://basescan.org/address/0xDFe8D79bc05420a3fFa14824135016a738eE8299) | Price aggregation hub                       |
| [Chainlink Prices](pricing/ChainlinkPrices.md)          | [0x253f55e455701fF0B835128f55668ed159aAB3D9](https://basescan.org/address/0x253f55e455701fF0B835128f55668ed159aAB3D9) | Chainlink oracle integration                |
| [Curve Prices](pricing/CurvePrices.md)                  | [0x7B2aeE8B6A4bdF0885dEF48CCda8453Fdc1Bba5d](https://basescan.org/address/0x7B2aeE8B6A4bdF0885dEF48CCda8453Fdc1Bba5d) | Curve pool pricing                          |
| [BlueChip Yield Prices](pricing/BlueChipYieldPrices.md) | [0x90C70ACfF302c8a7f00574EC3547B0221f39cD28](https://basescan.org/address/0x90C70ACfF302c8a7f00574EC3547B0221f39cD28) | Yield-bearing asset pricing                 |
| [Pyth Prices](pricing/PythPrices.md)                    | [0x4dfbFaC4592699A84377C7E8d6Be8d0fEDb4b9c0](https://basescan.org/address/0x4dfbFaC4592699A84377C7E8d6Be8d0fEDb4b9c0) | Pyth oracle integration                     |
| [Stork Prices](pricing/StorkPrices.md)                  | [0xd83187f7484FE9b92334d2a5bbCC6dDdA3E4e774](https://basescan.org/address/0xd83187f7484FE9b92334d2a5bbCC6dDdA3E4e774) | Stork oracle integration                    |
| Aero Ripe Prices                                        | [0x5ce2BbD5eBe9f7d9322a8F56740F95b9576eE0A2](https://basescan.org/address/0x5ce2BbD5eBe9f7d9322a8F56740F95b9576eE0A2) | Aerodrome Ripe Price oracle integration     |
| wsuperOETHbPrices                                       | [0x2606Ce36b62a77562DF664E7a0009805BB254F3f](https://basescan.org/address/0x2606Ce36b62a77562DF664E7a0009805BB254F3f) | Wrapped Super OETH Price oracle integration |
| Redstone                                                | [0x4Ef9450f11058fad3456f4461db24b461420A8C8](https://basescan.org/address/0x4Ef9450f11058fad3456f4461db24b461420A8C8) | Redstone oracle integration                 |
| UndyVaultPrices                                         | [0x2210a9b994CC0F13689043A34F2E11d17DB2099C](https://basescan.org/address/0x2210a9b994CC0F13689043A34F2E11d17DB2099C) | Underscore Vaults oracle integration        |

## Vault Registry

| Contract                              | Address                                                                                                               | Description              |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| [Vault Book](registries/VaultBook.md) | [0xB758e30C14825519b895Fd9928d5d8748A71a944](https://basescan.org/address/0xB758e30C14825519b895Fd9928d5d8748A71a944) | Vault registry & rewards |

## Vaults

| Contract                                  | Address                                                                                                               | Description               |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| [Ripe Gov](vaults/RipeGov.md)             | [0xe42b3dC546527EB70D741B185Dc57226cA01839D](https://basescan.org/address/0xe42b3dC546527EB70D741B185Dc57226cA01839D) | Governance staking vault  |
| [Simple Erc20](vaults/SimpleErc20.md)     | [0xf75b566eF80Fde0dEfcC045A4d57b540eb43ddfD](https://basescan.org/address/0xf75b566eF80Fde0dEfcC045A4d57b540eb43ddfD) | Standard collateral vault |
| [Rebase Erc20](vaults/RebaseErc20.md)     | [0xce2E96C9F6806731914A7b4c3E4aC1F296d98597](https://basescan.org/address/0xce2E96C9F6806731914A7b4c3E4aC1F296d98597) | Rebasing token vault      |
| [Underscore Vault](vaults/SimpleErc20.md) | [0x4549A368c00f803862d457C4C0c659a293F26C66](https://basescan.org/address/0x4549A368c00f803862d457C4C0c659a293F26C66) | Standard collateral vault |

## Liquidity Pools

### Green Stablecoin Pool

| Pool      | Address                                                                                                               | Platform | Description                |
| --------- | --------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------- |
| GreenPool | [0xd6c283655B42FA0eb2685F7AB819784F071459dc](https://basescan.org/address/0xd6c283655B42FA0eb2685F7AB819784F071459dc) | Curve    | GREEN/USDC stablecoin pool |

### RIPE Token Pools

| Pool         | Address                                                                                                               | Platform  | Description    |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | --------- | -------------- |
| RipePoolAero | [0x765824aD2eD0ECB70ECc25B0Cf285832b335d6A9](https://basescan.org/address/0x765824aD2eD0ECB70ECc25B0Cf285832b335d6A9) | Aerodrome | RIPE/WETH pool |
