# CreditEngine

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/core/CreditEngine.vy)

## Purpose

`CreditEngine` is the protocol's debt and collateral-risk coordinator. It computes account borrow terms, accrues interest, mints and burns GREEN, enforces borrow and withdrawal limits, and supplies health checks to liquidation, redemption, and deleveraging modules.

Users do not call its state-changing borrowing and repayment methods directly. [Teller](./Teller.md) is the normal gateway; AuctionHouse, CreditRedeem, Deleverage, and other registered departments have narrowly scoped settlement routes.

## Borrowing

`borrowForUser` is Teller-only. Before increasing debt, CreditEngine verifies, among other constraints:

- user authority or an allowed Underscore owner route;
- account, protocol, interval, borrower, and minimum-debt limits;
- the account's weighted loan-to-value terms;
- that the account is not already in liquidation; and
- that no collateral condition has placed the account in quarantine.

It accrues existing interest before applying the new principal and origination fee, updates reward points, and sends the borrowed GREEN according to the user's current configuration. GREEN may be delivered directly, converted to sGREEN, and optionally deposited into the dynamically configured preferred Stability Pool vault. An sGREEN preference falls back to raw GREEN when the handled amount is at or below `10**9` base units. Neither the core nor preferred vault is assumed to have a hardcoded ID.

## Repayment

`repayForUser` is Teller-only. AuctionHouse uses `repayDuringAuctionPurchase`; AuctionHouse, CreditRedeem, and Deleverage can use the department settlement route exposed by `repayFromDept`.

Repayment remains available for a quarantined account so the user can recover its debt health. Interest is checkpointed before principal accounting. Excess input is refunded to the actual payer, and an sGREEN-preferred refund at or below the `10**9`-base-unit dust guard is delivered as raw GREEN. A successful repayment can clear liquidation state when the account is healthy again.

`NewBorrow.didReceiveSavingsGreen` and `RepayDebt.refundWasSavingsGreen` record
the requested preference Boolean. They are not proof of the actual token form
when the dust fallback applies (and the repayment field may be `true` even when
the refund amount is zero).

The price behavior depends on both the remaining debt and the settlement route:

- A full standard payoff reduces debt to zero before collateral terms are recomputed. It therefore skips collateral pricing and quarantine recomputation, writes zero debt, and clears liquidation state.
- A partial standard repayment recomputes borrow terms with non-raising prices. An unavailable price on positive-LTV collateral conservatively removes that collateral's capacity and records quarantine, but does not prevent the repayment from being written; the account may remain in liquidation.
- A partial auction, redemption, or Deleverage department settlement recomputes the required collateral terms with strict pricing. A missing required price reverts that settlement atomically rather than accepting a partial nonstandard repayment against incomplete terms.

## Borrow terms and quarantine

`getUserBorrowTerms` aggregates eligible collateral across the user's registered vaults. It returns collateral value, debt limits, weighted terms, lowest/highest LTV information, and `hasQuarantinedAsset`.

Stability vaults are classified dynamically through MissionControl and are excluded from ordinary borrow collateral. CreditEngine also reads each asset's debt terms and skips the asset entirely when its current LTV is zero. A zero-LTV position therefore does not cause debt quarantine merely because its price or vault backing is unavailable.

Quarantine applies to positive-LTV collateral. A positive amount with no usable USD value is quarantined. A nominal balance whose converted amount is zero is quarantined only when the vault-wide amount for that asset is also zero; share-rounding dust in an otherwise nonempty vault is not. Risk-increasing operations then fail closed rather than treating unsafe positive-LTV collateral as worthless and continuing. Views such as `getMaxBorrowAmount` return zero when safe terms cannot be established.

This is distinct from ordinary price movement: quarantine represents incomplete or unsafe collateral valuation/topology, not merely an unhealthy LTV.

## Health and liquidation state

- `hasGoodDebtHealth` reports whether the account satisfies current debt-health terms.
- `canLiquidateUser` reports current liquidation eligibility.
- `canRedeemUserCollateral` reports whether collateral redemption may target the account.
- `getMaxWithdrawableForAsset` computes the maximum safe withdrawal for a specific vault and asset.

An account with no debt may withdraw its available balance. An account in
liquidation has no ordinary withdrawal capacity. When the requested asset's
current LTV is zero, `getMaxWithdrawableForAsset` returns `max_value(uint256)`
without running collateral pricing or account-quarantine calculations; Teller
and the vault still cap execution by the real position and other route checks.
For positive-LTV collateral, the reserve calculation fails closed on unusable
pricing or quarantined collateral, rounds conservatively, and includes the debt
buffer.

`inLiquidation` is an account-wide freeze. A liquidation retry is allowed only when no outstanding auction already owns the account's next settlement pass.

## Interest rate source

The constructor binds an immutable Curve price-source ID.
`getDynamicBorrowRate` returns the supplied base rate when that ID resolves to
the zero address, or when Curve's current status reports a zero weighted ratio
or a ratio below its danger trigger. Those are the explicit fallback cases.
Typed failures from PriceDesk's registry, CurvePrices, or MissionControl
propagate; a paused CurvePrices contract does not by itself select the base-rate
fallback because `getCurrentGreenPoolStatus` does not consult its pause flag.

## Department integrations

- `updateDebtForUser` permits registered Ripe departments to apply authorized debt changes.
- The CreditRedeem-only wrapper either transfers collateral in-vault or
  withdraws it externally. Both modes checkpoint the borrower after mutation;
  only in-vault delivery adds the recipient's Ledger vault membership and
  checkpoints the recipient.
- Switchboard controls sensitive parameters such as the Underscore vault discount and buyback configuration.

## Security properties

- State-changing debt routes are restricted to Teller or named protocol departments.
- Quarantine fails closed for borrowing, collateral-dependent withdrawal,
  liquidation, and redemption while leaving repayment and the zero-LTV
  withdrawal branch available.
- Exact accounting and post-operation health checks prevent stale front-end calculations from becoming execution authority.
- Dynamic vault classification replaces assumptions about fixed core, RipeGov, or preferred Stability vault IDs.

<!-- BEGIN GENERATED API REFERENCE: CreditEngine -->
## Exact API reference

> Generated from `contracts/core/CreditEngine.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _curvePricesId)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `borrowForUser(address _user, uint256 _greenAmount, bool _wantsSavingsGreen, bool _shouldEnterStabPool, address _caller, Addys _a)` | `5–6` | `_a = empty(addys.Addys)` |
| `canLiquidateUser(address _user, Addys _a)` | `1–2` | `_a = empty(addys.Addys)` |
| `canRedeemUserCollateral(address _user, Addys _a)` | `1–2` | `_a = empty(addys.Addys)` |
| `getLatestUserDebtAndTerms(address _user, bool _shouldRaise, Addys _a)` | `2–3` | `_a = empty(addys.Addys)` |
| `getMaxWithdrawableForAsset(address _user, uint256 _vaultId, address _asset, address _vaultAddr, Addys _a)` | `3–5` | `_vaultAddr = empty(address)`, `_a = empty(addys.Addys)` |
| `getUserBorrowTerms(address _user, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset, Addys _a)` | `2–5` | `_skipVaultId = 0`, `_skipAsset = empty(address)`, `_a = empty(addys.Addys)` |
| `getUserBorrowTermsWithNumVaults(address _user, uint256 _numUserVaults, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset, Addys _a)` | `3–6` | `_skipVaultId = 0`, `_skipAsset = empty(address)`, `_a = empty(addys.Addys)` |
| `hasGoodDebtHealth(address _user, Addys _a)` | `1–2` | `_a = empty(addys.Addys)` |
| `repayDuringAuctionPurchase(address _liqUser, uint256 _repayValue, Addys _a)` | `2–3` | `_a = empty(addys.Addys)` |
| `repayForUser(address _user, uint256 _greenAmount, bool _shouldRefundSavingsGreen, address _caller, Addys _a)` | `4–5` | `_a = empty(addys.Addys)` |
| `repayFromDept(address _user, tuple _userDebt, uint256 _repayValue, uint256 _newInterest, uint256 _numUserVaults, Addys _a)` | `5–6` | `_a = empty(addys.Addys)` |
| `updateDebtForUser(address _user, Addys _a)` | `1–2` | `_a = empty(addys.Addys)` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `borrowForUser(address _user, uint256 _greenAmount, bool _wantsSavingsGreen, bool _shouldEnterStabPool, address _caller)` | `nonpayable` | `uint256` | `uint256` |
| `borrowForUser(address _user, uint256 _greenAmount, bool _wantsSavingsGreen, bool _shouldEnterStabPool, address _caller, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `buybackRatio()` | `view` | `uint256` | — |
| `canLiquidateUser(address _user)` | `view` | `bool` | `bool` |
| `canLiquidateUser(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `bool` | `bool` |
| `canMintGreen()` | `view` | `bool` | — |
| `canMintRipe()` | `view` | `bool` | — |
| `canRedeemUserCollateral(address _user)` | `view` | `bool` | `bool` |
| `canRedeemUserCollateral(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `bool` | `bool` |
| `getAddys()` | `view` | `(address hq, address greenToken, address savingsGreen, address ripeToken, address ledger, address missionControl, address switchboard, address priceDesk, address vaultBook, address auctionHouse, address auctionHouseNft, address boardroom, address bondRoom, address creditEngine, address endaoment, address humanResources, address lootbox, address teller)` | — |
| `getBorrowRate(address _user)` | `view` | `uint256` | `uint256` |
| `getCollateralValue(address _user)` | `view` | `uint256` | `uint256` |
| `getDynamicBorrowRate(uint256 _baseRate)` | `view` | `uint256` | `uint256` |
| `getLatestUserDebtAndTerms(address _user, bool _shouldRaise)` | `view` | `((uint256 amount, uint256 principal, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lastTimestamp, bool inLiquidation), (uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset), uint256)` | `(UserDebt, UserBorrowTerms, uint256)` |
| `getLatestUserDebtAndTerms(address _user, bool _shouldRaise, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `((uint256 amount, uint256 principal, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lastTimestamp, bool inLiquidation), (uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset), uint256)` | `(UserDebt, UserBorrowTerms, uint256)` |
| `getLatestUserDebtWithInterest((uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool) _userDebt)` | `view` | `((uint256 amount, uint256 principal, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lastTimestamp, bool inLiquidation), uint256)` | `(UserDebt, uint256)` |
| `getLiquidationThreshold(address _user)` | `view` | `uint256` | `uint256` |
| `getMaxBorrowAmount(address _user)` | `view` | `uint256` | `uint256` |
| `getMaxWithdrawableForAsset(address _user, uint256 _vaultId, address _asset)` | `view` | `uint256` | `uint256` |
| `getMaxWithdrawableForAsset(address _user, uint256 _vaultId, address _asset, address _vaultAddr)` | `view` | `uint256` | `uint256` |
| `getMaxWithdrawableForAsset(address _user, uint256 _vaultId, address _asset, address _vaultAddr, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `uint256` | `uint256` |
| `getRedemptionThreshold(address _user)` | `view` | `uint256` | `uint256` |
| `getRipeHq()` | `view` | `address` | — |
| `getUserBorrowTerms(address _user, bool _shouldRaise)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTerms(address _user, bool _shouldRaise, uint256 _skipVaultId)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTerms(address _user, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTerms(address _user, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTermsWithNumVaults(address _user, uint256 _numUserVaults, bool _shouldRaise)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTermsWithNumVaults(address _user, uint256 _numUserVaults, bool _shouldRaise, uint256 _skipVaultId)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTermsWithNumVaults(address _user, uint256 _numUserVaults, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserBorrowTermsWithNumVaults(address _user, uint256 _numUserVaults, bool _shouldRaise, uint256 _skipVaultId, address _skipAsset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `(uint256 collateralVal, uint256 totalMaxDebt, (uint256 ltv, uint256 redemptionThreshold, uint256 liqThreshold, uint256 liqFee, uint256 borrowRate, uint256 daowry) debtTerms, uint256 lowestLtv, uint256 highestLtv, bool hasQuarantinedAsset)` | `UserBorrowTerms` |
| `getUserCollateralValueAndDebtAmount(address _user)` | `view` | `(uint256, uint256)` | `(uint256, uint256)` |
| `getUserDebtAmount(address _user)` | `view` | `uint256` | `uint256` |
| `hasGoodDebtHealth(address _user)` | `view` | `bool` | `bool` |
| `hasGoodDebtHealth(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `bool` | `bool` |
| `isPaused()` | `view` | `bool` | — |
| `pause(bool _shouldPause)` | `nonpayable` | — | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — | — |
| `repayDuringAuctionPurchase(address _liqUser, uint256 _repayValue)` | `nonpayable` | `bool` | `bool` |
| `repayDuringAuctionPurchase(address _liqUser, uint256 _repayValue, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` | `bool` |
| `repayForUser(address _user, uint256 _greenAmount, bool _shouldRefundSavingsGreen, address _caller)` | `nonpayable` | `bool` | `bool` |
| `repayForUser(address _user, uint256 _greenAmount, bool _shouldRefundSavingsGreen, address _caller, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` | `bool` |
| `repayFromDept(address _user, (uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool) _userDebt, uint256 _repayValue, uint256 _newInterest, uint256 _numUserVaults)` | `nonpayable` | `bool` | `bool` |
| `repayFromDept(address _user, (uint256,uint256,(uint256,uint256,uint256,uint256,uint256,uint256),uint256,bool) _userDebt, uint256 _repayValue, uint256 _newInterest, uint256 _numUserVaults, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` | `bool` |
| `setBuybackRatio(uint256 _ratio)` | `nonpayable` | — | — |
| `setUnderscoreVaultDiscount(uint256 _discount)` | `nonpayable` | — | — |
| `transferOrWithdrawViaRedemption(bool _shouldTransferBalance, address _asset, address _user, address _recipient, uint256 _amount, uint256 _vaultId, address _vaultAddr, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` | `uint256` |
| `undyVaulDiscount()` | `view` | `uint256` | — |
| `updateDebtForUser(address _user)` | `nonpayable` | `bool` | `bool` |
| `updateDebtForUser(address _user, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` | `bool` |

### Events

| Event | Fields |
| --- | --- |
| `BuybackRatioSet` | `uint256 ratio` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `NewBorrow` | `address user indexed, uint256 newLoan, uint256 daowry, bool didReceiveSavingsGreen, uint256 outstandingUserDebt, uint256 userCollateralVal, uint256 maxUserDebt, uint256 globalYieldRealized` |
| `RepayDebt` | `address user indexed, uint256 repayValue, uint256 repayType, uint256 refundAmount, bool refundWasSavingsGreen, uint256 outstandingUserDebt, uint256 userCollateralVal, uint256 maxUserDebt, bool hasGoodDebtHealth` |
| `UnderscoreVaultDiscountSet` | `uint256 discount` |

### Structs declared by this source

- `BorrowDataBundle(userDebt: UserDebt, userBorrowInterval: IntervalBorrow, isUserBorrower: bool, numUserVaults: uint256, totalDebt: uint256, numBorrowers: uint256)`
- `UserBorrowTerms(collateralVal: uint256, totalMaxDebt: uint256, debtTerms: cs.DebtTerms, lowestLtv: uint256, highestLtv: uint256, hasQuarantinedAsset: bool)`
- `UserDebt(amount: uint256, principal: uint256, debtTerms: cs.DebtTerms, lastTimestamp: uint256, inLiquidation: bool)`
- `IntervalBorrow(start: uint256, amount: uint256)`
- `RepayDataBundle(userDebt: UserDebt, numUserVaults: uint256)`
- `BorrowConfig(canBorrow: bool, canBorrowForUser: bool, numAllowedBorrowers: uint256, maxBorrowPerInterval: uint256, numBlocksPerInterval: uint256, perUserDebtLimit: uint256, globalDebtLimit: uint256, minDebtAmount: uint256, isDaowryEnabled: bool)`
- `RepayConfig(canRepay: bool, canAnyoneRepayDebt: bool)`
- `CurrentGreenPoolStatus(weightedRatio: uint256, dangerTrigger: uint256, numBlocksInDanger: uint256)`
- `DynamicBorrowRateConfig(minDynamicRateBoost: uint256, maxDynamicRateBoost: uint256, increasePerDangerBlock: uint256, maxBorrowRate: uint256)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `bad debt health`
- `borrow not enabled`
- `cannot borrow`
- `cannot borrow 0 amount`
- `cannot borrow for 0x0`
- `cannot borrow in liquidation`
- `cannot repay with 0 green`
- `contract paused`
- `could not burn green`
- `could not transfer`
- `could not transfer to gov`
- `debt too small`
- `global debt limit reached`
- `green approval failed`
- `green transfer failed`
- `interval borrow limit reached`
- `invalid discount`
- `invalid ratio`
- `invalid vault id`
- `max num borrowers reached`
- `no debt available`
- `no debt outstanding`
- `no perms`
- `not allowed`
- `not allowed to borrow for user`
- `not allowed to repay for user`
- `only auction house allowed`
- `only credit redeem allowed`
- `only switchboard allowed`
- `only teller allowed`
- `per user debt limit reached`
- `quarantined asset`
- `repay paused`
- `sgreen approval failed`

<!-- END GENERATED API REFERENCE: CreditEngine -->
