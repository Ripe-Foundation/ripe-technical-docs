# CreditRedeem

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/CreditRedeem.vy)

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

Before mutating the vault, it verifies that the collateral delivery would
produce nonzero GREEN debt credit. Delivery has two modes:

- With `_shouldTransferBalance == true`, the vault transfers the balance
  internally, checkpoints the borrower, adds the recipient's vault membership
  in Ledger, and checkpoints the recipient.
- With `_shouldTransferBalance == false`, the vault withdraws tokens externally
  to the recipient and checkpoints only the borrower. This is Teller's default.

GREEN is then burned and CreditEngine updates the borrower's debt. If the
post-delivery repayment would be zero, the transaction reverts atomically
rather than consuming collateral without reducing debt.

A batch is bounded to 20 redemption requests. Unused GREEN is returned to the
actual caller. An sGREEN preference wraps only amounts above `10**9` base
units; smaller refunds remain raw GREEN. A preview or
previously observed balance is not an execution guarantee because debt, prices,
balances, and account health are re-read during execution.

Individual rows may be skipped, but the whole batch reverts if every row is
skipped and aggregate GREEN spent remains zero.

## Views

`getMaxRedeemValue` returns the current upper bound for a target account. It returns zero when the target has no debt, is in liquidation or quarantine, has no usable collateral value, or has not crossed the configured redemption threshold.

The view is a screening result, not a reservation. Execution repeats the checks and may settle less or skip the entry.

## Security properties

- Only Teller may invoke the batch mutation entry point.
- Authorized but ineligible entries can fail soft; failed third-party authority
  and accounting inconsistencies revert the transaction.
- GREEN is burned only against debt actually credited through CreditEngine.
- The selected delivery mode determines whether collateral remains in protocol
  custody and whether recipient membership and checkpoints are written.
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
| `redeemCollateralFromMany(tuple[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, Addys _a)` | `6–7` | `_a = empty(addys.Addys)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getMaxRedeemValue(address _user)` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `isPaused()` | `view` | `bool` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` | `uint256` |
| `redeemCollateralFromMany((address,uint256,address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |

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

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `contract paused`
- `could not burn green`
- `green approval failed`
- `green transfer failed`
- `invalid vault id`
- `no green to redeem`
- `no redemptions occurred`
- `not allowed to deposit for user`
- `only Teller allowed`
- `sgreen approval failed`
- `vault outflow exceeds request`
- `zero repayment value (vault under-send)`

<!-- END GENERATED API REFERENCE: CreditRedeem -->
