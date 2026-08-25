# CreditRedeem

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/CreditRedeem.vy)

## Purpose

`CreditRedeem` lets GREEN holders repay eligible borrowers' debt in exchange for those borrowers' collateral. It is a debt-health mechanism, not an unconditional token swap: the target account, vault, asset, valuation, and requested amount are revalidated during execution.

User calls use Teller's `redeemCollateralFromMany` batch route, which calls the
method of the same name on CreditRedeem. A one-item batch handles a single
redemption.

## Eligibility

Each batch item is evaluated independently and may be skipped when it cannot safely execute. Examples include:

- an invalid or self recipient;
- an unregistered vault, unsupported asset, or zero usable balance;
- an Underscore Earn vault;
- disabled redemption configuration or asset/user disallowance;
- no target debt, an account in liquidation, or a quarantined account;
- no usable collateral value or a target that has not reached the redemption threshold.

Third-party recipient authority is fail-closed rather than a skippable
eligibility condition. If the recipient differs from the caller and the caller
lacks the required public-deposit or current Underscore-owner authority, the
assertion reverts the whole batch. Borrower eligibility and vault
classifications are resolved from current protocol state rather than fixed
vault IDs.

## Settlement

For an eligible item, CreditRedeem targets collateral at the account's lowest relevant LTV, applies the configured buffer and cap, obtains a fail-soft price, and computes no more than the caller requested or the target can safely provide.

Before mutating the vault, it verifies that the collateral transfer would produce nonzero GREEN debt credit. The collateral is then moved in-vault to the recipient, GREEN is burned, and CreditEngine updates the borrower's debt. If the post-transfer repayment would be zero, the transaction reverts atomically rather than consuming collateral without reducing debt.

A batch is bounded to 20 redemption requests. Unused GREEN is returned to the
actual caller, optionally as sGREEN according to the request. A preview or
previously observed balance is not an execution guarantee because debt, prices,
balances, and account health are re-read during execution.

## Views

`getMaxRedeemValue` returns the current upper bound for a target account. It returns zero when the target has no debt, is in liquidation or quarantine, has no usable collateral value, or has not crossed the configured redemption threshold.

The view is a screening result, not a reservation. Execution repeats the checks and may settle less or skip the entry.

## Security properties

- Only Teller may invoke the batch mutation entry point.
- Authorized but ineligible entries can fail soft; failed third-party authority
  and accounting inconsistencies revert the transaction.
- GREEN is burned only against debt actually credited through CreditEngine.
- In-vault collateral transfer preserves protocol custody and invokes the appropriate checkpoints.
- Quarantine and liquidation state prevent redemption from competing with account recovery or liquidation ownership.

<!-- BEGIN GENERATED API REFERENCE: CreditRedeem -->
## Exact API reference

> Generated from `contracts/core/CreditRedeem.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `redeemCollateralFromMany(tuple[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, Addys _a)` | `6–7` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getMaxRedeemValue(address _user)` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `CollateralRedeemed` | `address user indexed, uint256 vaultId, address asset indexed, uint256 amount, address recipient indexed, address caller, uint256 repayValue, bool hasGoodDebtHealth` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

### Structs declared by this source

- `UserBorrowTerms(collateralVal: uint256, totalMaxDebt: uint256, debtTerms: cs.DebtTerms, lowestLtv: uint256, highestLtv: uint256, hasQuarantinedAsset: bool)`
- `UserDebt(amount: uint256, principal: uint256, debtTerms: cs.DebtTerms, lastTimestamp: uint256, inLiquidation: bool)`
- `RepayDataBundle(userDebt: UserDebt, numUserVaults: uint256)`
- `RedeemCollateralConfig(canRedeemCollateralGeneral: bool, canRedeemCollateralAsset: bool, isUserAllowed: bool, ltvPaybackBuffer: uint256, canAnyoneDeposit: bool)`
- `CollateralRedemption(user: address, vaultId: uint256, asset: address, maxGreenAmount: uint256)`

<!-- END GENERATED API REFERENCE: CreditRedeem -->
