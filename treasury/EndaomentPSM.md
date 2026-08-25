# EndaomentPSM

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/EndaomentPSM.vy)

## Purpose

`EndaomentPSM` is a gated USDC/GREEN conversion module. It can mint GREEN (or deposit it into sGREEN) against USDC and redeem GREEN or sGREEN for USDC. The configured payment token must have exactly six decimals.

The constructor always starts both directions disabled: `canMint = false` and
`canRedeem = false`. A separate Switchboard action enables either direction.

## Minting USDC to GREEN

`mintGreen` requires the contract to be unpaused and minting enabled. For ordinary users, it applies the mint allowlist when configured, caps input by the active interval, applies the fee, and values output conservatively as the lesser of oracle value and 1:1 USDC value. It can deliver GREEN directly or sGREEN through SavingsGreen.

A recipient recognized as a current Underscore vault receives the special vault treatment: no ordinary mint fee or interval cap. Registry detection is dynamic; an arbitrary address cannot self-declare this status.

## Redeeming GREEN to USDC

`redeemGreen` accepts GREEN or sGREEN, requires redemption to be enabled, and is bounded by idle plus safely discoverable yield-position USDC. Ordinary users receive the lesser of oracle and 1:1 USDC value, then pay the configured fee and consume interval capacity.

A current Underscore vault receives the more favorable of oracle and 1:1 value and bypasses ordinary interval/fee treatment, but remains limited by real USDC liquidity.

When available USDC represents less than one USDC base unit in GREEN value, `getMaxRedeemableGreenAmount` returns zero rather than presenting an unusable dust quote. Mint and redeem are nonreentrant and burn/mint only after their corresponding custody checks.

## Block intervals

Mint and redemption have independent `PsmInterval` accounting. A future stored interval start is treated as active without subtracting it from the current block, avoiding an underflow. Switchboard may update the nonzero, non-maximum interval length and validated caps while the contract is unpaused.

These intervals use native `block.number`, not Ledger's configurable
action-block source.

## USDC yield

Available redemption liquidity includes idle USDC plus the underlying value of the configured yield position. A yield position is usable only when both its Lego ID and vault token are valid through the current Underscore topology. Switchboard can change the configured position and control auto-deposit. Registered Ripe addresses invoke the operational yield deposit, withdrawal, and USDC-to-EndaomentFunds routes. Missing topology fails closed instead of inventing liquidity.

## Administration

Switchboard controls enable flags, fees, caps, allowlists, interval length, yield position, and auto-deposit while respecting the contract's validation and pause rules. Relevant events distinguish conversions, yield movements, and every configuration update.

<!-- BEGIN GENERATED API REFERENCE: EndaomentPSM -->
## Exact API reference

> Generated from `contracts/core/EndaomentPSM.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _numBlocksPerInterval, uint256 _mintFee, uint256 _maxIntervalMint, uint256 _redeemFee, uint256 _maxIntervalRedeem, address _usdc, uint256 _usdcYieldLegoId, address _usdcYieldVaultToken)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `getMaxRedeemableGreenAmount(address _user, bool _isUnderscoreVault)` | `0–2` | `_user`, `_isUnderscoreVault` |
| `getMaxUsdcAmountForMint(address _user, bool _isUnderscoreVault)` | `0–2` | `_user`, `_isUnderscoreVault` |
| `mintGreen(uint256 _usdcAmount, address _recipient, bool _wantsSavingsGreen)` | `0–3` | `_usdcAmount`, `_recipient`, `_wantsSavingsGreen` |
| `redeemGreen(uint256 _paymentAmount, address _recipient, bool _isPaymentSavingsGreen)` | `0–3` | `_paymentAmount`, `_recipient`, `_isPaymentSavingsGreen` |
| `withdrawFromYield(uint256 _amount, bool _shouldTransferToEndaoFunds, bool _shouldFullSweep)` | `0–3` | `_amount`, `_shouldTransferToEndaoFunds`, `_shouldFullSweep` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `USDC()` | `view` | `address` |
| `canMint()` | `view` | `bool` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `canRedeem()` | `view` | `bool` |
| `depositToYield()` | `nonpayable` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getAvailIntervalMint()` | `view` | `uint256` |
| `getAvailIntervalRedemptions()` | `view` | `uint256` |
| `getAvailableUsdc()` | `view` | `uint256` |
| `getMaxRedeemableGreenAmount()` | `view` | `uint256` |
| `getMaxRedeemableGreenAmount(address _user)` | `view` | `uint256` |
| `getMaxRedeemableGreenAmount(address _user, bool _isUnderscoreVault)` | `view` | `uint256` |
| `getMaxUsdcAmountForMint()` | `view` | `uint256` |
| `getMaxUsdcAmountForMint(address _user)` | `view` | `uint256` |
| `getMaxUsdcAmountForMint(address _user, bool _isUnderscoreVault)` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `getUnderlyingYieldAmount()` | `view` | `uint256` |
| `getUsdcYieldPositionVaultToken()` | `view` | `address` |
| `globalMintInterval()` | `view` | `(uint256,uint256)` |
| `globalRedeemInterval()` | `view` | `(uint256,uint256)` |
| `isPaused()` | `view` | `bool` |
| `maxIntervalMint()` | `view` | `uint256` |
| `maxIntervalRedeem()` | `view` | `uint256` |
| `mintAllowlist(address arg0)` | `view` | `bool` |
| `mintFee()` | `view` | `uint256` |
| `mintGreen()` | `nonpayable` | `uint256` |
| `mintGreen(uint256 _usdcAmount)` | `nonpayable` | `uint256` |
| `mintGreen(uint256 _usdcAmount, address _recipient)` | `nonpayable` | `uint256` |
| `mintGreen(uint256 _usdcAmount, address _recipient, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `numBlocksPerInterval()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `redeemAllowlist(address arg0)` | `view` | `bool` |
| `redeemFee()` | `view` | `uint256` |
| `redeemGreen()` | `nonpayable` | `uint256` |
| `redeemGreen(uint256 _paymentAmount)` | `nonpayable` | `uint256` |
| `redeemGreen(uint256 _paymentAmount, address _recipient)` | `nonpayable` | `uint256` |
| `redeemGreen(uint256 _paymentAmount, address _recipient, bool _isPaymentSavingsGreen)` | `nonpayable` | `uint256` |
| `setCanMint(bool _canMint)` | `nonpayable` | — |
| `setCanRedeem(bool _canRedeem)` | `nonpayable` | — |
| `setMaxIntervalMint(uint256 _maxGreenAmount)` | `nonpayable` | — |
| `setMaxIntervalRedeem(uint256 _maxGreenAmount)` | `nonpayable` | — |
| `setMintFee(uint256 _fee)` | `nonpayable` | — |
| `setNumBlocksPerInterval(uint256 _blocks)` | `nonpayable` | — |
| `setRedeemFee(uint256 _fee)` | `nonpayable` | — |
| `setShouldAutoDeposit(bool _shouldAutoDeposit)` | `nonpayable` | — |
| `setShouldEnforceMintAllowlist(bool _shouldEnforce)` | `nonpayable` | — |
| `setShouldEnforceRedeemAllowlist(bool _shouldEnforce)` | `nonpayable` | — |
| `setUsdcYieldPosition(uint256 _legoId, address _vaultToken)` | `nonpayable` | — |
| `shouldAutoDeposit()` | `view` | `bool` |
| `shouldEnforceMintAllowlist()` | `view` | `bool` |
| `shouldEnforceRedeemAllowlist()` | `view` | `bool` |
| `transferUsdcToEndaomentFunds(uint256 _amount)` | `nonpayable` | `uint256` |
| `updateMintAllowlist(address _user, bool _isAllowed)` | `nonpayable` | — |
| `updateRedeemAllowlist(address _user, bool _isAllowed)` | `nonpayable` | — |
| `usdcYieldPosition()` | `view` | `(uint256,address)` |
| `withdrawFromYield()` | `nonpayable` | `(uint256, uint256)` |
| `withdrawFromYield(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` |
| `withdrawFromYield(uint256 _amount, bool _shouldTransferToEndaoFunds)` | `nonpayable` | `(uint256, uint256)` |
| `withdrawFromYield(uint256 _amount, bool _shouldTransferToEndaoFunds, bool _shouldFullSweep)` | `nonpayable` | `(uint256, uint256)` |

### Events

| Event | Fields |
| --- | --- |
| `CanMintUpdated` | `bool canMint` |
| `CanRedeemUpdated` | `bool canRedeem` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `EndaomentPSMYieldDeposit` | `uint256 amount, address vaultToken indexed, uint256 vaultTokenReceived, uint256 usdValue` |
| `EndaomentPSMYieldWithdrawal` | `address vaultToken indexed, uint256 vaultTokenBurned, uint256 usdcReceived, uint256 usdValue` |
| `MaxIntervalMintUpdated` | `uint256 maxAmount` |
| `MaxIntervalRedeemUpdated` | `uint256 maxAmount` |
| `MintAllowlistUpdated` | `address user indexed, bool isAllowed` |
| `MintFeeUpdated` | `uint256 fee` |
| `MintGreen` | `address user indexed, address sender indexed, uint256 usdcIn, uint256 greenOut, uint256 usdcFee, bool receivedSavingsGreen` |
| `NumBlocksPerIntervalUpdated` | `uint256 blocks` |
| `RedeemAllowlistUpdated` | `address user indexed, bool isAllowed` |
| `RedeemFeeUpdated` | `uint256 fee` |
| `RedeemGreen` | `address user indexed, address sender indexed, uint256 greenIn, uint256 usdcOut, uint256 usdcFee, bool paidWithSavingsGreen` |
| `ShouldAutoDepositUpdated` | `bool shouldAutoDeposit` |
| `ShouldEnforceMintAllowlistUpdated` | `bool shouldEnforce` |
| `ShouldEnforceRedeemAllowlistUpdated` | `bool shouldEnforce` |
| `UsdcYieldPositionUpdated` | `uint256 legoId, address vaultToken indexed` |

### Structs declared by this source

- `PsmInterval(start: uint256, amount: uint256)`
- `UsdcYieldPosition(legoId: uint256, vaultToken: address)`

<!-- END GENERATED API REFERENCE: EndaomentPSM -->
