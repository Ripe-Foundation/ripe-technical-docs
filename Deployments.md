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
| [Credit Engine](core-lending/CreditEngine.md)   | [0xC4d54b999D333E8c8293f83DDcF3B9A19B76645F](https://basescan.org/address/0xC4d54b999D333E8c8293f83DDcF3B9A19B76645F) | Lending and borrowing engine |
| [Teller](core-lending/Teller.md)                | [0xad4a471C8D57715d3D8585a593305a43bc7389fa](https://basescan.org/address/0xad4a471C8D57715d3D8585a593305a43bc7389fa) | User interaction gateway     |
| [Ledger](core-lending/Ledger.md)                | [0x365256e322a47Aa2015F6724783F326e9B24fA47](https://basescan.org/address/0x365256e322a47Aa2015F6724783F326e9B24fA47) | Protocol data storage        |
| [Auction House](core-lending/AuctionHouse.md)   | [0x3228b04a4b4b498dA7235154131374077600989F](https://basescan.org/address/0x3228b04a4b4b498dA7235154131374077600989F) | Liquidation auctions         |
| [Stability Pool](core-lending/StabilityPool.md) | [0x2a157096af6337b2b4bd47de435520572ed5a439](https://basescan.org/address/0x2a157096af6337b2b4bd47de435520572ed5a439) | Liquidation backstop vault   |

## Treasury & Rewards

| Contract                                              | Address                                                                                                               | Description                  |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| [Endaoment](treasury-rewards/Endaoment.md)            | [0xd00A4A131b26920b6f407D177bCCa94454EAEF7d](https://basescan.org/address/0xd00A4A131b26920b6f407D177bCCa94454EAEF7d) | Treasury yield strategies    |
| [Bond Room](treasury-rewards/BondRoom.md)             | [0x7D0A292032c44e3e25871a1FB08288b85BdD816f](https://basescan.org/address/0x7D0A292032c44e3e25871a1FB08288b85BdD816f) | RIPE bond sales              |
| [Bond Booster](treasury-rewards/BondBooster.md)       | [0xF9E38714E01DA439E4211F8275F141d3A896bb74](https://basescan.org/address/0xF9E38714E01DA439E4211F8275F141d3A896bb74) | Bond purchase incentives     |
| [Lootbox](treasury-rewards/Lootbox.md)                | [0xE05605ba1Fb0551c6f4b0089FD46D42D63c795bA](https://basescan.org/address/0xE05605ba1Fb0551c6f4b0089FD46D42D63c795bA) | Rewards distribution         |
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
| [Switchboard Alpha](governance-control/configuration/SwitchboardAlpha.md)     | [0xAb5Cc2381b8F637D772fF927A0a7c2852d4B819b](https://basescan.org/address/0xAb5Cc2381b8F637D772fF927A0a7c2852d4B819b) | Config manager A |
| [Switchboard Bravo](governance-control/configuration/SwitchboardBravo.md)     | [0xD18AC028cBe1AbebDb118E9C7A60018d58C846e7](https://basescan.org/address/0xD18AC028cBe1AbebDb118E9C7A60018d58C846e7) | Config manager B |
| [Switchboard Charlie](governance-control/configuration/SwitchboardCharlie.md) | [0xB96D9862838f17Ca51603EEECd54E99f33D3461d](https://basescan.org/address/0xB96D9862838f17Ca51603EEECd54E99f33D3461d) | Config manager C |
| [Switchboard Delta](governance-control/configuration/SwitchboardDelta.md)     | [0x7c3a6D04DF0e066FDa6c2CBC570C25022EA31276](https://basescan.org/address/0x7c3a6D04DF0e066FDa6c2CBC570C25022EA31276) | Config manager D |

## Pricing

| Contract                                                | Address                                                                                                               | Description                  |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| [Price Desk](pricing/PriceDesk.md)                      | [0xDFe8D79bc05420a3fFa14824135016a738eE8299](https://basescan.org/address/0xDFe8D79bc05420a3fFa14824135016a738eE8299) | Price aggregation hub        |
| [Chainlink Prices](pricing/ChainlinkPrices.md)          | [0x253f55e455701fF0B835128f55668ed159aAB3D9](https://basescan.org/address/0x253f55e455701fF0B835128f55668ed159aAB3D9) | Chainlink oracle integration |
| [Curve Prices](pricing/CurvePrices.md)                  | [0x50C3eCC034436c7D962E7063Fc7cD8f05A97Bbc1](https://basescan.org/address/0x50C3eCC034436c7D962E7063Fc7cD8f05A97Bbc1) | Curve pool pricing           |
| [BlueChip Yield Prices](pricing/BlueChipYieldPrices.md) | [0x90C70ACfF302c8a7f00574EC3547B0221f39cD28](https://basescan.org/address/0x90C70ACfF302c8a7f00574EC3547B0221f39cD28) | Yield-bearing asset pricing  |
| [Pyth Prices](pricing/PythPrices.md)                    | [0x4dfbFaC4592699A84377C7E8d6Be8d0fEDb4b9c0](https://basescan.org/address/0x4dfbFaC4592699A84377C7E8d6Be8d0fEDb4b9c0) | Pyth oracle integration      |
| [Stork Prices](pricing/StorkPrices.md)                  | [0xd83187f7484FE9b92334d2a5bbCC6dDdA3E4e774](https://basescan.org/address/0xd83187f7484FE9b92334d2a5bbCC6dDdA3E4e774) | Stork oracle integration     |

## Vault Registry

| Contract                              | Address                                                                                                               | Description              |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| [Vault Book](registries/VaultBook.md) | [0xB758e30C14825519b895Fd9928d5d8748A71a944](https://basescan.org/address/0xB758e30C14825519b895Fd9928d5d8748A71a944) | Vault registry & rewards |

## Vaults

| Contract                              | Address                                                                                                               | Description               |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| [Ripe Gov](vaults/RipeGov.md)         | [0xe42b3dC546527EB70D741B185Dc57226cA01839D](https://basescan.org/address/0xe42b3dC546527EB70D741B185Dc57226cA01839D) | Governance staking vault  |
| [Simple Erc20](vaults/SimpleErc20.md) | [0xf75b566eF80Fde0dEfcC045A4d57b540eb43ddfD](https://basescan.org/address/0xf75b566eF80Fde0dEfcC045A4d57b540eb43ddfD) | Standard collateral vault |
| [Rebase Erc20](vaults/RebaseErc20.md) | [0xce2E96C9F6806731914A7b4c3E4aC1F296d98597](https://basescan.org/address/0xce2E96C9F6806731914A7b4c3E4aC1F296d98597) | Rebasing token vault      |

## Liquidity Pools

### Green Stablecoin Pool

| Pool      | Address                                                                                                               | Platform | Description                |
| --------- | --------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------- |
| GreenPool | [0xd6c283655B42FA0eb2685F7AB819784F071459dc](https://basescan.org/address/0xd6c283655B42FA0eb2685F7AB819784F071459dc) | Curve    | GREEN/USDC stablecoin pool |

### RIPE Token Pools

| Pool          | Address                                                                                                               | Platform  | Description    |
| ------------- | --------------------------------------------------------------------------------------------------------------------- | --------- | -------------- |
| RipePoolCurve | [0xF8D92a9531205AB2Dd0Bc623CDF4A6Ab4c3a2526](https://basescan.org/address/0xF8D92a9531205AB2Dd0Bc623CDF4A6Ab4c3a2526) | Curve     | RIPE/ETH pool  |
| RipePoolAero  | [0x765824aD2eD0ECB70ECc25B0Cf285832b335d6A9](https://basescan.org/address/0x765824aD2eD0ECB70ECc25B0Cf285832b335d6A9) | Aerodrome | RIPE/WETH pool |
