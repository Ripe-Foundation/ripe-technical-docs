# StabVault module

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/vaults/modules/StabVault.vy)

## Overview

`StabVault` supplies StabilityPool's USD-valued share accounting, liquidation settlement, claim and redemption flows, and claim-asset lifecycle. A position is a cohort identified by its stabilization asset. The cohort owns unreserved principal plus the value of its **active** claim assets.

The composed [StabilityPool](../../core/StabilityPool.md) exports only a
selected part of this module and is the host-ABI authority.

## Constructor-bound addresses

At initialization the module resolves GREEN and Savings GREEN from RipeHq and stores both as immutables. PriceDesk and the other protocol addresses are resolved through Addys when used.

Changing a GREEN or Savings GREEN registry pointer does not rewrite these
immutables in an existing StabilityPool.

## Claim records and configuration

Claims and redemptions use these batch rows:

```text
StabPoolClaim:
  stabAsset
  claimAsset
  maxUsdValue

StabPoolRedemption:
  claimAsset
  maxGreenAmount
```

MissionControl returns:

```text
StabPoolClaimsConfig:
  canClaimInStabPoolGeneral
  canClaimInStabPoolAsset
  canClaimFromStabPoolForUser
  isUserAllowed
  rewardsLockDuration
  ripePerDollarClaimed

StabPoolRedemptionsConfig:
  canRedeemInStabPoolGeneral
  canRedeemInStabPoolAsset
  isUserAllowed
  canAnyoneDeposit
```

Both public batch limits are 15 rows. The module also limits one maintenance call to 15 claim assets.

## Principal, reservations, and custody

The two claim-balance ledgers have different scopes:

- `claimableBalances[stabAsset][claimAsset]` is one cohort's liability;
- `totalClaimableBalances[claimAsset]` is that token's liability across every cohort in the contract.

Physical token custody is not automatically principal. For any asset, the spendable balance is:

```text
unreserved = token.balanceOf(StabilityPool) - totalClaimableBalances[token]
```

The subtraction first asserts that custody covers the aggregate liability. This prevents one cohort, a withdrawal, or a liquidation swap from spending tokens reserved for another cohort.

A principal deposit is rejected when:

- the pool is paused;
- user or asset is zero;
- the asset is GREEN;
- the asset has any aggregate claim reservation; or
- the resulting share amount is zero.

The reported deposit is clipped to current custody. Teller is expected to move the tokens before calling the vault. A successful first deposit registers the asset in VaultData.

Outgoing principal and direct claim transfers require exact vault outflow and exact recipient delivery. Tokens that charge an outbound transfer fee are therefore incompatible with those routes. Auto-deposit instead verifies the StabilityPool's exact outflow around the Teller call.

## USD value and shares

GREEN claim balances are valued one-for-one in 18-decimal USD. Savings GREEN uses ERC-4626 conversion to or from GREEN. Other assets use strict PriceDesk conversions for accounting operations.

The cohort's strict USD value is:

```text
unreserved stabilization principal value
+ value of every active claim pair
```

Dormant claim pairs remain reserved liabilities but are deliberately excluded from NAV.

Share conversion uses a `1e8` virtual-share offset and a one-unit virtual USD value:

```text
shares = usdValue * (totalShares + 1e8) / (totalUsdValue + 1)
value  = shares   * (totalUsdValue + 1) / (totalShares + 1e8)
```

The caller-selected rounding direction is used internally. Deposits round share issuance down; partial withdrawal and claim calculations may round required shares up. Conversion uses checked `uint256` multiplication followed by division, not a 512-bit full-precision `mulDiv`; an overflowing intermediate product reverts even when the mathematical quotient would fit. A deposit that would mint zero shares also reverts.

Raw `userBalances` and `totalBalances` are shares, not token amounts. The module
declares the rounding-aware conversion views
`valueToShares(asset, usdValue, shouldRoundUp)` and
`sharesToValue(asset, shares, shouldRoundUp)`, but the composed StabilityPool
does not export either selector.

The host-facing USD views are `getTotalValue(asset)` and
`getTotalUserValue(user, asset)`. Its ordinary vault amount views are
`getTotalAmountForVault(asset)` and `getTotalAmountForUser(user, asset)`; these
convert the cohort's active NAV back into an equivalent amount of the
stabilization asset, so they need not equal raw principal custody.

Lootbox weight is `userShares / 1e8`.

## Withdrawals and internal transfers

A withdrawal values the user's shares against unreserved principal plus active claims, but pays only the stabilization asset. It computes the pro-rata principal amount, burns the corresponding shares, and transfers the principal exactly.

An internal vault transfer uses the same valuation but moves shares between users without moving tokens. AuctionHouse and CreditEngine use this route at the StabilityPool host level.

Both paths fail closed when required principal or active-claim custody is deficient or a required strict price is unavailable.

## Liquidation settlement

Only AuctionHouse may execute the two settlement routes, and the pool must be unpaused. The stabilization asset must already be registered, the received liquidation asset must be nonzero and must not itself be a registered pool asset, and GREEN cannot be the stabilization asset.

### Principal-funded settlement

`swapForLiquidatedCollateral` records the collateral as a cohort claim liability, then pays at most the cohort's unreserved principal.

- With a nonzero recipient, it transfers the stabilization asset exactly.
- With a zero recipient, the asset must be GREEN or Savings GREEN. Because the validation independently rejects GREEN as a stabilization asset, the current usable burn path is Savings GREEN: redeem it to GREEN and burn the GREEN.

### Claimable-GREEN settlement

`swapWithClaimableGreen` records the new collateral, consumes up to the cohort's reserved GREEN claim balance, reduces both pair and aggregate GREEN liabilities, and burns the GREEN. It does not spend stabilization principal.

### Receipt and admission checks

For a new or dormant claim pair, receipt requires:

- aggregate custody sufficient for every existing liability of that token;
- the reported receipt no greater than newly unreserved custody;
- a nonzero fail-soft USD quote; and
- room below the 20-active-asset cap.

At or above $0.10, the pair becomes active. A smaller positive-value receipt remains dormant. A later top-up can activate the dormant pair when its total reaches the floor.

`canAcceptLiquidationAsset` lets AuctionHouse skip an incompatible cohort before collateral moves. It returns false when:

- the stabilization asset is unsupported or the claim token is already a registered pool asset;
- any cohort has reserved the stabilization token as a claim asset;
- the pool is paused;
- a new or dormant pair would exceed the active cap; or
- a nonempty cohort has no fail-soft liquidation amount.

The fail-soft amount requires positive unreserved principal, a usable principal price, and adequate aggregate custody plus usable prices for every active claim. Dormant claims are not part of that calculation. A configured cohort with zero shares and zero active claims passes this preflight after the reservation checks; the state-changing settlement still enforces its stricter receipt assertions.

If a cohort is unhealthy during AuctionHouse enumeration, the vault preserves the stabilization asset address but reports amount zero. CreditEngine excludes StabilityPool vault IDs from collateral valuation; AuctionHouse can continue through its ordinary-auction path.

## Claiming cohort collateral

The module declares both `claimFromStabilityPool` and
`claimManyFromStabilityPool`, but the StabilityPool host exports only the batch
selector. Only Teller may call it, and the pool must be unpaused. Each row is
evaluated against MissionControl's general switch, claim-token switch,
whitelist, and third-party authority.

A third party may act through configured delegation. Without that delegation, the caller must be recognized as the claimer's Underscore wallet owner. Invalid or unavailable rows return zero; the whole batch reverts if the total claimed USD value is zero.

For a successful row the module:

1. reads the cohort pair balance directly, whether active or dormant;
2. limits the claim by the user's current share value, the row's USD cap, pair balance, and custody;
3. burns shares proportional to the claimed USD value;
4. reduces the pair liability and the token's aggregate liability;
5. transfers the asset exactly or attempts Teller auto-deposit; and
6. emits `AssetClaimedInStabilityPool`.

Dormant collateral is therefore not personal inventory: a funded shareholder can claim it and pays pro-rata cohort shares even though the dormant value is absent from NAV. A holder that fully exits first has no shares with which to claim the residual. The residual remains reserved and may later be activated, topped up, or consumed through redemption.

After all rows, each touched stabilization cohort is checkpointed in Lootbox once. The module then calculates RIPE rewards from total claimed USD value and the current global reward terms returned by MissionControl, caps issuance to Ledger's available reward budget, mints through VaultBook, and deposits into MissionControl's current core RipeGov vault with the configured lock. There is no permanent governance-vault ID in this flow. Any later failure reverts the entire claim transaction, including liability reductions and reward accounting.

## Redeeming GREEN for claim assets

The module likewise declares singular and batch redemption helpers, while the
host exports only `redeemManyFromStabilityPool`. Teller calls that route while
the pool is unpaused and transfers GREEN to the pool first, unwrapping payment
Savings GREEN when requested.

GREEN cannot be the requested claim asset. Each row applies MissionControl's general redemption switch, asset switch, recipient whitelist, and third-party deposit policy. When the recipient differs from the caller and public deposits for that recipient are disabled, the caller must be the recipient's Underscore wallet owner.

The module prices the requested token strictly, limits delivery to aggregate reserved liability and custody, then walks registered stabilization cohorts in vault order. Both active and dormant pair balances participate.

For each filled cohort:

- the claim token is delivered or auto-deposited for the recipient;
- pair and aggregate claim liabilities are reduced;
- a Savings GREEN cohort converts the corresponding GREEN into new Savings GREEN principal; and
- any other cohort receives the GREEN as a new claim liability for its shareholders.

The GREEN charge rounds up for each cohort and is capped by the row and
remaining payment. If no row fills, the transaction reverts. Unspent GREEN goes
back to the original caller. A Savings GREEN refund request wraps only when the
amount is strictly greater than `10**9` GREEN base units; smaller refunds remain
GREEN.

If GREEN is registered as a legacy stabilization asset, redemption is allowed only when it is the sole registered pool asset. New principal deposits and liquidation settlements still reject GREEN.

## Active, dormant, and absent claim assets

`getClaimAssetState` returns:

| Value | State | Meaning |
| --- | --- | --- |
| `0` | absent | pair balance is zero and it is not active |
| `1` | dormant | pair balance is nonzero but it is outside the active iterable set |
| `2` | active | pair is in the iterable set and contributes to NAV |

The active cap is 20 per stabilization cohort. `getNumActiveClaimAssets` removes the module's one-based sentinel from the stored iterable count.

Lifecycle event reason codes are:

| Event | Reason | Meaning |
| --- | --- | --- |
| `ClaimAssetLeftDormant` | `1` | receipt valued below the $0.10 activation floor |
| `ClaimAssetDeactivated` | `1` | pair balance reached zero |
| `ClaimAssetDeactivated` | `2` | priced residual was below the $0.05 retention floor |

Deactivation changes active-list membership; it does not sweep a nonzero balance or erase its liability.

## Permissionless maintenance

`pruneClaimableAssets` may run while paused or unpaused. It removes an active zero-balance entry. It may also make a nonzero active pair dormant when:

- the cohort has zero shares;
- aggregate custody is solvent; and
- a fail-soft quote is nonzero but below $0.05.

An unavailable or zero quote is not proof of dust and leaves the pair active.
An existing cohort's nonzero pair is not manually dust-pruned.

Claims and redemptions have an additional automatic cleanup rule. A priced
residual below $0.05 may be delisted for an empty cohort, or for a share-bearing
cohort only when its raw remainder is no more than one ten-billionth of the
prior pair balance. A zero remainder becomes absent; a nonzero remainder becomes
dormant.

`activateClaimAssets` is also permissionless but requires the pool paused. Each candidate is skipped unless the cohort has zero shares, the pair is dormant and nonzero, aggregate custody is solvent, its fail-soft value is at least $0.10, and active capacity remains. The module declares `canActivateClaimAsset`, but the StabilityPool host intentionally does not export that preflight view; integrations can use the exported claim-state/count views but must treat execution as authoritative.

The empty-cohort requirement prevents maintenance from adding previously
excluded dormant value to an existing shareholder cohort.

## Retirement and recovery

Only Switchboard may deregister a stabilization asset. Deregistration returns false while either principal shares or any nonzero claim pair remains. `doesVaultHaveAnyFunds` uses the same logical share/pair state; it is not a raw-token balance scan.

The StabilityPool host disables both recovery entry points unconditionally.
StabVault has no position export/import or claim-liability migration path, so
those positions and liabilities cannot be transferred through this module.

## Integration requirements

- Resolve the preferred StabilityPool and the core RipeGov vault from MissionControl at runtime.
- Treat `totalClaimableBalances` as a cross-cohort reservation, not informational accounting.
- Do not include dormant balances in cohort NAV, but do preserve their custody and claim/redemption rights.
- Use the host's batch-only claim and redemption routes through Teller.
- Keep AuctionHouse admission, raw-custody sizing, and settlement assertions aligned.
- Do not attempt to recover reserved tokens through the disabled recovery ABI.

<!-- BEGIN GENERATED API REFERENCE: StabVault -->
## Exact source-declared API reference

> Generated from declarations in `contracts/vaults/modules/StabVault.vy`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### Deployment/module initializer declared by this source

A `@deploy` initializer is constructor context when this source is deployed or module-initialization context when composed. It is not a runtime selector.

- `def __init__()`

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def activateClaimAssets(_stabAsset: address, _claimAssets: DynArray[address, MAX_CLAIM_ASSET_MAINTENANCE])` | `2` | `nonpayable` | — |
| `def canAcceptLiquidationAsset(_stabAsset: address, _claimAsset: address) -> bool` | `2` | `view` | `bool` |
| `def canActivateClaimAsset(_stabAsset: address, _claimAsset: address) -> (bool, uint256, uint256)` | `2` | `view` | `(bool, uint256, uint256)` |
| `def claimFromStabilityPool(_claimer: address, _stabAsset: address, _claimAsset: address, _maxUsdValue: uint256, _caller: address, _shouldAutoDeposit: bool, _a: addys.Addys = empty(addys.Addys)) -> uint256` | `6–7` | `nonpayable` | `uint256` |
| `def claimManyFromStabilityPool(_claimer: address, _claims: DynArray[StabPoolClaim, MAX_STAB_CLAIMS], _caller: address, _shouldAutoDeposit: bool, _a: addys.Addys = empty(addys.Addys)) -> uint256` | `4–5` | `nonpayable` | `uint256` |
| `def deregisterVaultAsset(_asset: address) -> bool` | `1` | `nonpayable` | `bool` |
| `def doesVaultHaveAnyFunds() -> bool` | `0` | `view` | `bool` |
| `def getClaimAssetState(_stabAsset: address, _claimAsset: address) -> uint256` | `2` | `view` | `uint256` |
| `def getNumActiveClaimAssets(_stabAsset: address) -> uint256` | `1` | `view` | `uint256` |
| `def getTotalUserValue(_user: address, _asset: address) -> uint256` | `2` | `view` | `uint256` |
| `def getTotalValue(_asset: address) -> uint256` | `1` | `view` | `uint256` |
| `def pruneClaimableAssets(_stabAsset: address, _claimAssets: DynArray[address, MAX_CLAIM_ASSET_MAINTENANCE])` | `2` | `nonpayable` | — |
| `def redeemFromStabilityPool(_asset: address, _greenAmount: uint256, _recipient: address, _caller: address, _shouldAutoDeposit: bool, _shouldRefundSavingsGreen: bool, _a: addys.Addys = empty(addys.Addys)) -> uint256` | `6–7` | `nonpayable` | `uint256` |
| `def redeemManyFromStabilityPool(_redemptions: DynArray[StabPoolRedemption, MAX_STAB_REDEMPTIONS], _greenAmount: uint256, _recipient: address, _caller: address, _shouldAutoDeposit: bool, _shouldRefundSavingsGreen: bool, _a: addys.Addys = empty(addys.Addys)) -> uint256` | `6–7` | `nonpayable` | `uint256` |
| `def sharesToValue(_asset: address, _shares: uint256, _shouldRoundUp: bool) -> uint256` | `3` | `view` | `uint256` |
| `def swapForLiquidatedCollateral(_stabAsset: address, _stabAssetAmount: uint256, _liqAsset: address, _liqAmountSent: uint256, _recipient: address, _greenToken: address, _savingsGreenToken: address) -> uint256` | `7` | `nonpayable` | `uint256` |
| `def swapWithClaimableGreen(_stabAsset: address, _greenAmount: uint256, _liqAsset: address, _liqAmountSent: uint256, _greenToken: address) -> uint256` | `5` | `nonpayable` | `uint256` |
| `def valueToShares(_asset: address, _usdValue: uint256, _shouldRoundUp: bool) -> uint256` | `3` | `view` | `uint256` |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `activateClaimAssets(address _stabAsset, DynArray[address, MAX_CLAIM_ASSET_MAINTENANCE] _claimAssets)` | `nonpayable` | — |
| `canAcceptLiquidationAsset(address _stabAsset, address _claimAsset)` | `view` | `bool` |
| `canActivateClaimAsset(address _stabAsset, address _claimAsset)` | `view` | `(bool, uint256, uint256)` |
| `claimFromStabilityPool(address _claimer, address _stabAsset, address _claimAsset, uint256 _maxUsdValue, address _caller, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` |
| `claimFromStabilityPool(address _claimer, address _stabAsset, address _claimAsset, uint256 _maxUsdValue, address _caller, bool _shouldAutoDeposit, addys.Addys _a)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(address _claimer, DynArray[StabPoolClaim, MAX_STAB_CLAIMS] _claims, address _caller, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(address _claimer, DynArray[StabPoolClaim, MAX_STAB_CLAIMS] _claims, address _caller, bool _shouldAutoDeposit, addys.Addys _a)` | `nonpayable` | `uint256` |
| `deregisterVaultAsset(address _asset)` | `nonpayable` | `bool` |
| `doesVaultHaveAnyFunds()` | `view` | `bool` |
| `getClaimAssetState(address _stabAsset, address _claimAsset)` | `view` | `uint256` |
| `getNumActiveClaimAssets(address _stabAsset)` | `view` | `uint256` |
| `getTotalUserValue(address _user, address _asset)` | `view` | `uint256` |
| `getTotalValue(address _asset)` | `view` | `uint256` |
| `pruneClaimableAssets(address _stabAsset, DynArray[address, MAX_CLAIM_ASSET_MAINTENANCE] _claimAssets)` | `nonpayable` | — |
| `redeemFromStabilityPool(address _asset, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemFromStabilityPool(address _asset, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen, addys.Addys _a)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(DynArray[StabPoolRedemption, MAX_STAB_REDEMPTIONS] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool(DynArray[StabPoolRedemption, MAX_STAB_REDEMPTIONS] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen, addys.Addys _a)` | `nonpayable` | `uint256` |
| `sharesToValue(address _asset, uint256 _shares, bool _shouldRoundUp)` | `view` | `uint256` |
| `swapForLiquidatedCollateral(address _stabAsset, uint256 _stabAssetAmount, address _liqAsset, uint256 _liqAmountSent, address _recipient, address _greenToken, address _savingsGreenToken)` | `nonpayable` | `uint256` |
| `swapWithClaimableGreen(address _stabAsset, uint256 _greenAmount, address _liqAsset, uint256 _liqAmountSent, address _greenToken)` | `nonpayable` | `uint256` |
| `valueToShares(address _asset, uint256 _usdValue, bool _shouldRoundUp)` | `view` | `uint256` |

### Compiler-generated public getters

| Getter | Mutability | Source return type |
| --- | --- | --- |
| `claimableAssets(address key1, uint256 key2)` | `view` | `address` |
| `claimableBalances(address key1, address key2)` | `view` | `uint256` |
| `indexOfClaimableAsset(address key1, address key2)` | `view` | `uint256` |
| `numClaimableAssets(address key1)` | `view` | `uint256` |
| `totalClaimableBalances(address key1)` | `view` | `uint256` |

### Events declared by this source

- `AssetClaimedInStabilityPool(user: indexed(address), stabAsset: indexed(address), claimAsset: indexed(address), claimAmount: uint256, claimUsdValue: uint256, claimShares: uint256, isDepleted: bool)`
- `ClaimAssetActivated(stabAsset: indexed(address), claimAsset: indexed(address), balance: uint256, activeCount: uint256)`
- `ClaimAssetDeactivated(stabAsset: indexed(address), claimAsset: indexed(address), balance: uint256, activeCount: uint256, reason: uint256)`
- `ClaimAssetLeftDormant(stabAsset: indexed(address), claimAsset: indexed(address), balance: uint256, activeCount: uint256, reason: uint256)`

### Constants declared by this source

- `MAX_STAB_CLAIMS: uint256 = 15`
- `MAX_STAB_REDEMPTIONS: uint256 = 15`
- `MAX_ACTIVE_CLAIM_ASSETS: uint256 = 20`
- `MAX_CLAIM_ASSET_MAINTENANCE: uint256 = 15`
- `DECIMAL_OFFSET: uint256 = 10 ** 8`
- `EIGHTEEN_DECIMALS: uint256 = 10 ** 18`
- `ACTIVATION_USD_THRESHOLD: uint256 = 10 * 10 ** 16`
- `RETENTION_USD_THRESHOLD: uint256 = 5 * 10 ** 16`
- `LIVE_RESIDUAL_DIVISOR: uint256 = 10 ** 10`
- `CLAIM_ASSET_ABSENT: uint256 = 0`
- `CLAIM_ASSET_DORMANT: uint256 = 1`
- `CLAIM_ASSET_ACTIVE: uint256 = 2`
- `DEACTIVATION_ZERO: uint256 = 1`
- `DEACTIVATION_DUST: uint256 = 2`
- `DORMANT_BELOW_FLOOR: uint256 = 1`

### Structs declared by this source

- `StabPoolClaim(stabAsset: address, claimAsset: address, maxUsdValue: uint256)`
- `StabPoolRedemption(claimAsset: address, maxGreenAmount: uint256)`
- `StabPoolClaimsConfig(canClaimInStabPoolGeneral: bool, canClaimInStabPoolAsset: bool, canClaimFromStabPoolForUser: bool, isUserAllowed: bool, rewardsLockDuration: uint256, ripePerDollarClaimed: uint256)`
- `StabPoolRedemptionsConfig(canRedeemInStabPoolGeneral: bool, canRedeemInStabPoolAsset: bool, isUserAllowed: bool, canAnyoneDeposit: bool)`
- `TellerDepositConfig(canDepositGeneral: bool, canDepositAsset: bool, doesVaultSupportAsset: bool, isUserAllowed: bool, perUserDepositLimit: uint256, globalDepositLimit: uint256, perUserMaxAssetsPerVault: uint256, perUserMaxVaults: uint256, canAnyoneDeposit: bool)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `asset reserved for claims`
- `burn failed`
- `cannot claim for user`
- `cannot mint 0 shares`
- `claim asset already active`
- `claim asset is stability asset`
- `claim custody deficit`
- `contract not paused`
- `contract paused`
- `failed to burn green`
- `green approval failed`
- `green cannot be stab asset`
- `green transfer failed`
- `invalid claim asset`
- `invalid deposit amount`
- `invalid liq asset`
- `invalid recipient delivery`
- `invalid stab asset`
- `invalid user or asset`
- `invalid user, asset, or recipient`
- `invalid users or asset`
- `invalid vault id`
- `invalid vault outflow`
- `liq asset cannot be vault asset`
- `max active claim assets`
- `max withdraw stab amount is 0`
- `mint failed`
- `must be green or savings green`
- `no claimable balance`
- `no green`
- `no green to redeem`
- `no perms`
- `no price for claim asset`
- `no price for stab asset`
- `no redemptions occurred`
- `no stab asset to withdraw`
- `no withdrawal amount`
- `not allowed to deposit for user`
- `nothing claimed`
- `nothing received`
- `nothing to transfer`
- `only AuctionHouse allowed`
- `only Teller allowed`
- `redemptions not allowed`
- `ripe approval failed`
- `savings green redeem failed`
- `short claim receipt`
- `stab asset not supported`
- `token approval failed`
- `transfer failed`
- `user has no shares`

<!-- END GENERATED API REFERENCE: StabVault -->
