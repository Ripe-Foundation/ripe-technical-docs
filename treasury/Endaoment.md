# Endaoment

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/Endaoment.vy)

## Purpose and custody model

`Endaoment` is the governed executor for protocol-owned treasury assets. Long-lived assets are normally held by [EndaomentFunds](./EndaomentFunds.md); Endaoment pulls only the amount needed for a current action, executes it, and returns resulting assets to EndaomentFunds.

Switchboard controls the treasury operations, pause state, and recovery routes.
The direct USDC transfer to EndaomentPSM accepts either a registered Switchboard
or RipeHq governance. A lite signer cannot call Endaoment directly; it uses
[`SwitchboardEcho.transferFundsToEndaomentPsmInEndaoment`](../governance/configuration/SwitchboardEcho.md),
which forwards as the registered Switchboard. Every governed external mutation
route is nonreentrant; the payable default function separately accepts native
funds. The constructor binds WETH, a native-token sentinel, and a Curve
price-source ID.

## Supported operations

The contract can:

- transfer assets to governance or EndaomentPSM, and return transient balances to EndaomentFunds;
- deposit to and withdraw from approved yield positions;
- execute bounded multi-step swaps;
- claim incentives;
- wrap and unwrap the configured native asset/WETH pair;
- add and remove pool liquidity;
- stabilize the configured GREEN reference pool;
- mint and add partner liquidity; and
- repay GREEN debt associated with a pool.

Yield, swap, reward, and liquidity routes resolve a nonzero adapter from the
current Underscore Lego registry. `claimIncentives` additionally checks that the
Lego is approved for the reward action type; the other route families do not
run one universal action-type authorization check. Token approvals are scoped
to the action and reset afterward. Missing registry topology fails closed.

## GREEN reference-pool stabilization

`stabilizeGreenRefPool` reads the current stabilizer configuration and
normalizes GREEN and alternate-asset pool balances through the configured Curve
price source. It can operate when one normalized side is zero; an absent pool
or two zero/equal sides returns false.

When GREEN is underweight, the contract may mint/add GREEN liquidity and record the actual new GREEN used as pool debt. When GREEN is overweight, it removes liquidity and repays debt from the recovered GREEN. Both directions must preserve or improve the pool's calculated net position. The removal path searches for an executable amount rather than assuming the initial quote can be used, and applies conservative rounding around the LP quote.

`getGreenAmountToAddInStabilizer`, `getGreenAmountToRemoveInStabilizer`, and
`calcProfitForStabilizer` calculate from state at call time and do not reserve
an execution outcome.

## Partner liquidity

`mintPartnerLiquidity(partner, asset, amount)` prepares matched GREEN against an
approved partner asset. The combined route is the seven-argument
`addPartnerLiquidity(legoId, pool, partner, asset, amount, minLpAmount,
expectedLpToken)`.

For the combined route:

- LP is minted to Endaoment so only that call's balance delta is split;
- the returned LP token must equal `expectedLpToken`, and the measured LP delta must equal the venue report;
- reported partner/GREEN contributions must equal the combined Endaoment plus EndaomentFunds custody decrease;
- partial fills are accepted, but unused provisional GREEN mint is burned;
- pool debt increases only by newly minted GREEN actually contributed; and
- unless the partner is Endaoment itself, the partner receives half the LP and EndaomentFunds receives the remainder.

The explicit amount, minimum LP output, and expected token are security-relevant
and must be supplied by integrations.

## Pool debt

Ledger records GREEN minted into supported liquidity pools. `repayPoolDebt` burns no more than both available GREEN and the pool's recorded debt. Stabilizer and partner paths reconcile debt to realized token movement, not a requested or quoted amount.

## Events and operational evidence

`WalletAction`, `WalletActionExt`, `StabilizerPoolLiqAdded`,
`StabilizerPoolLiqRemoved`, `PoolDebtRepaid`, `PartnerLiquidityMinted`, and
`PartnerLiquidityAdded` record completed calls and their documented values.

<!-- BEGIN GENERATED API REFERENCE: Endaoment -->
## Exact API reference

> Generated from `contracts/core/Endaoment.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _weth, address _eth, uint256 _curvePricesId)`

### Fallback and receive

- `fallback()` — `payable`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData)` | `4–10` | `_amountA = max_value(uint256)`, `_amountB = max_value(uint256)`, `_minAmountA = 0`, `_minAmountB = 0`, `_minLpAmount = 0`, `_extraData = empty(bytes32)` |
| `claimIncentives(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount, bytes32[] _proofs)` | `2–5` | `_rewardToken = empty(address)`, `_rewardAmount = max_value(uint256)`, `_proofs = []` |
| `convertEthToWeth(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `convertWethToEth(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `depositForYield(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount, bytes32 _extraData)` | `2–5` | `_vaultAddr = empty(address)`, `_amount = max_value(uint256)`, `_extraData = empty(bytes32)` |
| `mintPartnerLiquidity(address _partner, address _asset, uint256 _amount)` | `2–3` | `_amount = max_value(uint256)` |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData)` | `5–9` | `_lpAmount = max_value(uint256)`, `_minAmountA = 0`, `_minAmountB = 0`, `_extraData = empty(bytes32)` |
| `repayPoolDebt(address _pool, uint256 _amount)` | `1–2` | `_amount = max_value(uint256)` |
| `transferFundsToEndaomentPSM(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `transferFundsToGov(address _asset, uint256 _amount)` | `1–2` | `_amount = max_value(uint256)` |
| `withdrawFromYield(uint256 _legoId, address _vaultToken, uint256 _amount, bytes32 _extraData)` | `2–4` | `_amount = max_value(uint256)`, `_extraData = empty(bytes32)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `ETH()` | `view` | `address` | — |
| `WETH()` | `view` | `address` | — |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `addPartnerLiquidity(uint256 _legoId, address _pool, address _partner, address _asset, uint256 _amount, uint256 _minLpAmount, address _expectedLpToken)` | `nonpayable` | `(uint256, uint256, uint256)` | `(uint256, uint256, uint256)` |
| `calcProfitForStabilizer()` | `view` | `uint256` | `uint256` |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `claimIncentives(address _user, uint256 _legoId)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentives(address _user, uint256 _legoId, address _rewardToken)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentives(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentives(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount, bytes32[] _proofs)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertEthToWeth()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertEthToWeth(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertWethToEth()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertWethToEth(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `depositForYield(uint256 _legoId, address _asset)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYield(uint256 _legoId, address _asset, address _vaultAddr)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYield(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYield(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount, bytes32 _extraData)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getGreenAmountToAddInStabilizer()` | `view` | `uint256` | `uint256` |
| `getGreenAmountToRemoveInStabilizer()` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | `bool` |
| `mintPartnerLiquidity(address _partner, address _asset)` | `nonpayable` | `uint256` | `uint256` |
| `mintPartnerLiquidity(address _partner, address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidity(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` | `(uint256, uint256, uint256, uint256)` |
| `repayPoolDebt(address _pool)` | `nonpayable` | `bool` | `bool` |
| `repayPoolDebt(address _pool, uint256 _amount)` | `nonpayable` | `bool` | `bool` |
| `stabilizeGreenRefPool()` | `nonpayable` | `bool` | `bool` |
| `swapTokens((uint256,uint256,uint256,address[],address[])[] _instructions)` | `nonpayable` | `(address, uint256, address, uint256, uint256)` | `(address, uint256, address, uint256, uint256)` |
| `transferFundsToEndaomentPSM()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToEndaomentPSM(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToGov(address _asset)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToGov(address _asset, uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToVault(address[] _assets)` | `nonpayable` | — | — |
| `withdrawFromYield(uint256 _legoId, address _vaultToken)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYield(uint256 _legoId, address _vaultToken, uint256 _amount)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYield(uint256 _legoId, address _vaultToken, uint256 _amount, bytes32 _extraData)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `PartnerLiquidityAdded` | `address partner indexed, address asset indexed, uint256 partnerAmount, uint256 greenAmount, uint256 lpBalance` |
| `PartnerLiquidityMinted` | `address partner indexed, address asset indexed, uint256 partnerAmount, uint256 usdValue, uint256 greenMinted` |
| `PoolDebtRepaid` | `address pool indexed, uint256 amount` |
| `StabilizerPoolLiqAdded` | `address pool indexed, uint256 greenAmountAdded, uint256 lpReceived, uint256 poolDebtAdded` |
| `StabilizerPoolLiqRemoved` | `address pool indexed, uint256 lpBurned, uint256 greenAmountRemoved, uint256 debtRepaid` |
| `WalletAction` | `uint8 op, address asset1 indexed, address asset2 indexed, uint256 amount1, uint256 amount2, uint256 usdValue, uint256 legoId` |
| `WalletActionExt` | `uint8 op, address asset1 indexed, address asset2 indexed, uint256 tokenId, uint256 amount1, uint256 amount2, uint256 usdValue, uint256 extra` |

### Structs declared by this source

- `StabilizerConfig(pool: address, lpToken: address, greenBalance: uint256, greenRatio: uint256, greenIndex: uint256, stabilizerAdjustWeight: uint256, stabilizerMaxPoolDebt: uint256, altBalance: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `appr`
- `approval failed`
- `contract paused`
- `could not burn green`
- `could not transfer`
- `failed to set operator`
- `green accounting`
- `green refund accounting`
- `invalid addys`
- `invalid asset`
- `invalid gov recipient`
- `invalid lego`
- `invalid lp token`
- `invalid partner asset`
- `invalid underscore registry`
- `lego`
- `lp amount mismatch`
- `no amt`
- `no asset received`
- `no asset to add`
- `no balance for _token`
- `no change`
- `no debt to repay`
- `no endaoment funds`
- `no endaoment psm`
- `no liquidity added`
- `no output amount`
- `no perms`
- `no usdc`
- `partner asset accounting`
- `path`
- `stabilizer was not profitable`
- `swaps`
- `transfer failed`
- `unexpected lp token`
- `xfer`

<!-- END GENERATED API REFERENCE: Endaoment -->
