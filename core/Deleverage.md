# Deleverage

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/Deleverage.vy)

## Purpose

`Deleverage` repays debt by converting or withdrawing a user's eligible
collateral under route-specific rules. It supports a permissionless-but-capped
general batch, authorized explicit-asset deleveraging, volatile-collateral
reduction, collateral swaps, and withdrawal-time deleveraging.

General and specific-asset calls use Teller's batch routes; a one-item batch
handles one user. The direct volatile, swap, and withdrawal-time entries have
their own trusted integration boundaries.

## Entry points

- `deleverageManyUsers` and `deleverageWithSpecificAssets` are callable on the
  Deleverage contract only by Teller. Teller's general batch is open to any
  caller under the bounded untrusted rules below; the specific-asset route
  requires a trusted caller classification.
- `deleverageWithVolAssets` reduces eligible volatile collateral under current configuration and is restricted to registered Ripe callers or Switchboard.
- `swapCollateral` is a registered-Ripe-or-governance integration route; it does
  not perform the ordinary user delegation, quarantine, or liquidation-state
  checks.
- `deleverageForWithdrawal` admits any registered Ripe caller without user
  delegation. A non-Ripe caller must be a current Underscore earn vault or
  valid LegoBook address, and a cross-user Underscore call additionally
  requires `canBorrow` delegation.
- `getDeleverageInfo` and `getMaxDeleverageAmount` are screening/quote views, not execution guarantees.

The collateral/debt execution routes above are nonreentrant; configuration
setters are separately Switchboard-gated. Their trust models differ.
`swapCollateral` relies on registered-Ripe-or-governance authority rather than
ordinary user-state guards. Each route applies its own caps, prices, cooldowns,
and topology checks rather than one universal validation bundle.

### General batch: permissionless and trusted branches

`deleverageManyUsers` does not require the caller to be the user or to hold a
delegation. Each row first classifies the caller. A currently registered Ripe
address is trusted. Otherwise, a self-call is trusted only when that caller is
a registered Underscore address; an ordinary EOA self-call remains untrusted.
For a different target, current `canBorrow` delegation upgrades the caller to
trusted.

A caller who remains untrusted can still deleverage a target, but only while
the target is not in liquidation, has nonzero collateral value, is in the
configured near-redemption zone, and has no quarantined collateral. The
repayment is capped to the calculated amount needed to move toward the guarded
target LTV. This is an intentional permissionless risk-reduction route, not a
failed authorization check. Trusted general requests are not subject to the
near-redemption cap or liquidation rejection, though debt, quarantine, pricing,
custody, and settlement checks still apply.

`deleverageWithSpecificAssets` uses a different rule: a self-call is trusted
without requiring Underscore registration, and a registered Ripe caller or a
cross-user caller with `canBorrow` delegation is also accepted. There is no
permissionless untrusted specific-asset branch. An admitted specific-asset
request can operate during liquidation.

### Trusted volatile-asset route

`deleverageWithVolAssets` accepts any currently registered Ripe caller or
Switchboard, does not require user delegation, and has no `inLiquidation` guard.
It obtains current debt terms with strict pricing and returns zero when debt is
zero or that pass reports quarantine; an unavailable price required by the
strict pass can instead revert. The caller supplies the vault/asset order and
per-row repayment targets.

Here, "volatile" is a configuration exclusion, not a volatility or LTV test.
The route skips assets configured to burn as payment or transfer to Endaoment
through the normal deleverage cohort, and sends each remaining selected asset
to EndaomentFunds (or the configured PSM recipient for its yield-position
token). A zero-LTV asset can therefore still be repayment liquidity. The total
repayment is capped by current debt and debt is reread before department
settlement.

This route does not call Teller housekeeping. It neither writes Ledger
`lastTouch` nor updates `lastDeleverageBlock`; the latter mapping is used only by
`deleverageForWithdrawal`.

### Withdrawal-time route

`deleverageForWithdrawal` admits a currently registered Ripe address, a current
Underscore earn vault, or a valid address in the current Underscore LegoBook. A
cross-user Underscore caller must also hold `canBorrow` delegation. Every
admitted caller becomes trusted for the internal deleverage pass, so this route
can operate while the user is in liquidation. It still returns false for
quarantined/no-debt accounts and applies its withdrawal-value, lost-capacity,
cooldown, minimum-size, price, and settlement checks. A successful repayment records native
`block.number` in `lastDeleverageBlock`; it does not call Teller housekeeping or
write Ledger `lastTouch`.

### Trusted collateral swap

`swapCollateral` accepts a registered Ripe caller or the exact governance
address returned by RipeHq. It does not accept arbitrary Switchboards, ordinary
user delegation, or preflight debt, quarantine, or liquidation state. Both
vault IDs must resolve, and the replacement asset's current LTV must be at
least the withdrawn asset's LTV. AuctionHouse sends the user's withdrawn
collateral to the trusted caller, both sides are converted with strict prices,
and the caller must supply the USD-equivalent replacement asset for Teller to
deposit for the user. Any failed replacement or housekeeping step reverts the
whole swap.

After the replacement deposit, `swapCollateral` calls Teller's low-risk
housekeeping path. That path updates the Curve snapshot and debt, writes the
user's Ledger `lastTouch`, and still rejects a locked account, but it does not
enforce the one-action-per-action-block duplicate-touch check. It does not
write Deleverage's `lastDeleverageBlock`.

## Asset ordering and vault classification

The contract builds eligible collateral cohorts from current MissionControl classifications. Stability vaults are not treated as ordinary collateral priority, and historical/current RipeGov or preferred-vault relationships must be resolved dynamically. Disabled, missing, or malformed Underscore topology fails closed or causes an asset to be skipped rather than fabricating a route.

No current core, RipeGov, or preferred Stability vault ID is hardcoded by this documentation.

## Settlement integrity

External collateral actions can execute before final debt settlement. Immediately afterward, `_refreshSettlementDebt` rereads the user's debt and requires it to match the expected snapshot. This prevents a callback or integration from changing debt mid-route and then settling collateral against stale accounting.

Collateral custody, realized output, and debt repayment are reconciled exactly. A view result may shrink or become ineligible before execution as prices, balances, permissions, or debt change.

## Full payoff and debt clearing

Small residual debt is not automatically forgiven. The full-payoff path
requires both the configured absolute debt-clear threshold and the configured
basis-point threshold to authorize clearing. If either governing condition does
not permit it, the remainder stays as debt. Setting both controls to zero
disables dust forgiveness.

## Security properties

- Quarantine protects every debt-settlement route except `swapCollateral`,
  whose registered-Ripe-or-governance boundary and replacement-collateral
  invariant are different.
- The general batch intentionally permits arbitrary callers only for capped,
  non-liquidating near-redemption accounts. Trusted general, specific-asset,
  volatile-asset, and admitted withdrawal-time routes can operate during
  liquidation.
- Debt is re-read after external collateral actions and must equal the expected snapshot.
- Stability and Underscore integrations fail closed when their current topology is unusable.
- Sender checkpoints run after collateral movement so rewards and accounting follow the realized state.

<!-- BEGIN GENERATED API REFERENCE: Deleverage -->
## Exact API reference

> Generated from `contracts/core/Deleverage.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, uint256 _minDeleverageBps, uint256 _deleverageBuffer, uint256 _deleverageCooldown, uint256 _underscoreSafeSpreadBps, uint256 _deleverageFullPayoffBuffer, uint256 _deleverageOverageBps, uint256 _deleverageDustThreshold, uint256 _deleverageDustBps)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `deleverageManyUsers(tuple[] _users, address _caller, Addys _a)` | `2–3` | `_a` |
| `deleverageWithSpecificAssets(address _user, tuple[] _assets, address _caller, Addys _a)` | `3–4` | `_a` |
| `swapCollateral(address _user, uint256 _withdrawVaultId, address _withdrawAsset, uint256 _depositVaultId, address _depositAsset, uint256 _withdrawAmount)` | `5–6` | `_withdrawAmount` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `deleverageBuffer()` | `view` | `uint256` |
| `deleverageCooldown()` | `view` | `uint256` |
| `deleverageDustBps()` | `view` | `uint256` |
| `deleverageDustThreshold()` | `view` | `uint256` |
| `deleverageForWithdrawal(address _user, uint256 _vaultId, address _asset, uint256 _amount)` | `nonpayable` | `bool` |
| `deleverageFullPayoffBuffer()` | `view` | `uint256` |
| `deleverageManyUsers((address,uint256)[] _users, address _caller)` | `nonpayable` | `uint256` |
| `deleverageManyUsers((address,uint256)[] _users, address _caller, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `deleverageOverageBps()` | `view` | `uint256` |
| `deleverageWithSpecificAssets(address _user, (uint256,address,uint256)[] _assets, address _caller)` | `nonpayable` | `uint256` |
| `deleverageWithSpecificAssets(address _user, (uint256,address,uint256)[] _assets, address _caller, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `deleverageWithVolAssets(address _user, (uint256,address,uint256)[] _assets)` | `nonpayable` | `uint256` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getDeleverageInfo(address _user)` | `view` | `(uint256, uint256)` |
| `getMaxDeleverageAmount(address _user)` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `isPaused()` | `view` | `bool` |
| `lastDeleverageBlock(address arg0)` | `view` | `uint256` |
| `minDeleverageBps()` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `setDeleverageBuffer(uint256 _bps)` | `nonpayable` | — |
| `setDeleverageCooldown(uint256 _blocks)` | `nonpayable` | — |
| `setDeleverageFullPayoffParam(uint256 _param, uint256 _amount)` | `nonpayable` | — |
| `setMinDeleverageBps(uint256 _bps)` | `nonpayable` | — |
| `setUnderscoreSafeSpreadBps(uint256 _bps)` | `nonpayable` | — |
| `swapCollateral(address _user, uint256 _withdrawVaultId, address _withdrawAsset, uint256 _depositVaultId, address _depositAsset)` | `nonpayable` | `(uint256, uint256)` |
| `swapCollateral(address _user, uint256 _withdrawVaultId, address _withdrawAsset, uint256 _depositVaultId, address _depositAsset, uint256 _withdrawAmount)` | `nonpayable` | `(uint256, uint256)` |
| `underscoreSafeSpreadBps()` | `view` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `CollateralSwapped` | `address user indexed, address caller indexed, uint256 withdrawVaultId, address withdrawAsset indexed, uint256 withdrawAmount, uint256 depositVaultId, address depositAsset, uint256 depositAmount, uint256 usdValue` |
| `DeleverageBufferSet` | `uint256 bps` |
| `DeleverageCooldownSet` | `uint256 blocks` |
| `DeleverageFullPayoffParamSet` | `uint256 param, uint256 amount` |
| `DeleverageUser` | `address user indexed, address caller indexed, uint256 targetRepayAmount, uint256 targetRepayAmountWithBuffer, uint256 collateralValueRepaid, uint256 debtToClear, bool hasGoodDebtHealth` |
| `DeleverageUserWithVolatileAssets` | `address user indexed, uint256 repaidAmount, bool hasGoodDebtHealth` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `EndaomentTransferDuringDeleverage` | `address user indexed, uint256 vaultId, address asset indexed, uint256 amountSent, uint256 usdValue, bool isDepleted` |
| `MinDeleverageBpsSet` | `uint256 bps` |
| `StabAssetBurntDuringDeleverage` | `address user indexed, uint256 vaultId, address stabAsset indexed, uint256 amountBurned, uint256 usdValue, bool isDepleted` |
| `UnderscoreSafeSpreadBpsSet` | `uint256 bps` |

### Structs declared by this source

- `DeleverageUserRequest(user: address, targetRepayAmount: uint256)`
- `DeleverageAsset(vaultId: uint256, asset: address, targetRepayAmount: uint256)`
- `GenLiqConfig(canLiquidate: bool, keeperFeeRatio: uint256, minKeeperFee: uint256, maxKeeperFee: uint256, ltvPaybackBuffer: uint256, genAuctionParams: cs.AuctionParams, priorityLiqAssetVaults: DynArray[VaultData, PRIORITY_LIQ_VAULT_DATA], priorityStabVaults: DynArray[VaultData, MAX_STAB_VAULT_DATA])`
- `AssetLiqConfig(hasConfig: bool, shouldBurnAsPayment: bool, shouldTransferToEndaoment: bool, shouldSwapInStabPools: bool, shouldAuctionInstantly: bool, customAuctionParams: cs.AuctionParams, specialStabPool: VaultData)`
- `VaultData(vaultId: uint256, vaultAddr: address, asset: address)`
- `UserBorrowTerms(collateralVal: uint256, totalMaxDebt: uint256, debtTerms: cs.DebtTerms, lowestLtv: uint256, highestLtv: uint256, hasQuarantinedAsset: bool)`
- `UserDebt(amount: uint256, principal: uint256, debtTerms: cs.DebtTerms, lastTimestamp: uint256, inLiquidation: bool)`

<!-- END GENERATED API REFERENCE: Deleverage -->
