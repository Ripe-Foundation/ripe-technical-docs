# StabilityPool

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/vaults/StabilityPool.vy)

## Overview

`StabilityPool` is the vault host through which configured stabilization assets absorb liquidations and receive collateral claims. It stores user positions as USD-valued shares, not raw token balances. Neither the accepted principal assets nor the liquidation spread is hardcoded in this contract.

The detailed accounting and claim lifecycle live in [StabVault](../vaults/modules/StabVault.md).

## Composition and constructor

The host combines:

- Addys for RipeHQ-backed protocol addresses;
- VaultData for pause state, user/vault asset indexes, and share storage; and
- StabVault for valuation, reservations, liquidation swaps, claims, redemptions, and maintenance.

The constructor takes only `ripeHq`. The vault starts unpaused. During
initialization StabVault captures the GREEN and Savings GREEN addresses as
immutables.

MissionControl selects the current preferred StabilityPool. Consumers must not assume that selection has a permanent numeric vault ID.

## Access boundaries

| Operation | Authorized caller | Pause condition |
| --- | --- | --- |
| principal deposit | Teller | pool must be unpaused |
| principal withdrawal | Teller, AuctionHouse, or CreditEngine | pool must be unpaused |
| internal balance transfer | AuctionHouse or CreditEngine | pool must be unpaused |
| batch collateral claim | Teller | pool must be unpaused |
| batch GREEN redemption | Teller | pool must be unpaused |
| liquidation settlement | AuctionHouse | pool must be unpaused |
| pause change | a valid Switchboard | no host-level pause prerequisite |
| claim pruning | anyone | paused or unpaused |
| dormant-claim activation | anyone | pool must be paused |
| stabilization-asset deregistration | a valid Switchboard | no host-level pause prerequisite |

All three core balance-changing vault entry points are nonreentrant.

## Principal positions

### Deposit

Teller transfers the configured stabilization asset to the vault and calls `depositTokensInVault(user, asset, amount, addys)`. StabVault clips the reported amount to custody, values it in USD, includes active claim value in the pre-deposit cohort NAV, and mints shares. GREEN itself is rejected as a principal asset; the standard GREEN convenience route in Teller first converts GREEN to Savings GREEN and deposits that into MissionControl's current preferred pool.

The host returns the accepted token amount and emits:

```text
StabilityPoolDeposit(user, asset, amount, shares)
```

### Withdrawal

`withdrawTokensFromVault` burns the USD-value shares required for the requested principal amount, transfers the stabilization asset exactly, and returns `(withdrawalAmount, isDepleted)`.

```text
StabilityPoolWithdrawal(user, asset, amount, isDepleted, shares)
```

Liquidated collateral is not implicitly delivered with a principal withdrawal. It is obtained through the explicit claim flow.

### Internal transfer

`transferBalanceWithinVault` moves shares between users without moving tokens. The amount returned is the stabilization-asset equivalent used to size the share transfer.

```text
StabilityPoolTransfer(
  fromUser,
  toUser,
  asset,
  transferAmount,
  isFromUserDepleted,
  transferShares
)
```

## Batch-only claim and redemption routes

The composed `StabilityPool` host ABI exports only the batch claim and
redemption entry points. `StabVault.vy` declares singular module helpers named
`claimFromStabilityPool` and `redeemFromStabilityPool`, but the host does not
export them, so callers cannot use those selectors on the host. A
single-item action must use a one-row batch through
[Teller](./Teller.md). The host variants are protocol integration surfaces and
may include the resolved Addys struct; end users should not call them directly.

### Claims

Teller forwards up to 15 `(stabAsset, claimAsset, maxUsdValue)` rows for a claimer. Each successful row burns the claimer's cohort shares, reduces the pair and aggregate claim liabilities, and transfers or auto-deposits the claim asset. Active and dormant pairs can both be claimed.

The batch returns total claimed 18-decimal USD value. MissionControl controls general/asset/whitelist/delegation authority. RIPE claim incentives, when configured and funded, are deposited into MissionControl's current core RipeGov vault rather than a hardcoded vault ID.

Successful rows emit:

```text
AssetClaimedInStabilityPool(
  user,
  stabAsset,
  claimAsset,
  claimAmount,
  claimUsdValue,
  claimShares,
  isDepleted
)
```

### Redemptions

Teller transfers GREEN to the selected StabilityPool, optionally by redeeming the caller's Savings GREEN first. It forwards up to 15 `(claimAsset, maxGreenAmount)` rows. The pool exchanges GREEN at current strict USD value for aggregate reserved claim assets across registered stabilization cohorts.

The requested claim assets go to the recipient or an eligible auto-deposit vault. GREEN spent against a Savings GREEN cohort becomes additional Savings GREEN principal; GREEN spent against other cohorts becomes a reserved GREEN claim for those shareholders. Unspent payment is refunded to the original caller as GREEN or, when requested and above the dust guard, Savings GREEN.

The return value is GREEN spent. A batch with no successful redemption reverts.

## Liquidation integration

[AuctionHouse](./AuctionHouse.md) first checks
`canAcceptLiquidationAsset(stabAsset, claimAsset)`. The view rejects an
unsupported stabilization asset, a claim token that is itself a registered
pool asset, a reserved stabilization token, a paused pool, unavailable active
capacity for a new/dormant pair, or an unhealthy nonempty cohort. The cohort
health calculation prices unreserved principal and existing active claims; an
empty cohort can pass without pricing the incoming claim token.

That preflight is not a guarantee that the incoming claim will be admitted.
After AuctionHouse transfers collateral, settlement separately rechecks
aggregate claim custody, the newly unreserved receipt, active capacity, and a
nonzero fail-soft price for a new or dormant claim pair. Failure reverts the
whole swap rather than recording unpriced liability.

For a principal-funded swap, AuctionHouse transfers the liquidated collateral into the pool, records it as a reserved cohort claim, and removes unreserved stabilization principal. A non-GREEN principal is transferred to AuctionHouse's chosen recipient. Savings GREEN can instead be redeemed and burned as GREEN.

If the cohort already owns reserved GREEN, AuctionHouse may consume and burn that claim liability in exchange for new collateral without removing principal.

The liquidation-facing position iterator preserves the registered asset address but returns amount zero when the cohort's fail-soft liquidation value is unavailable. This lets AuctionHouse skip the pool and continue through ordinary auction handling. CreditEngine excludes StabilityPool vault IDs from collateral valuation.

## Claim reservation and lifecycle views

The host exports:

- pair balances by stabilization asset and claim token;
- aggregate reserved balance by claim token across all cohorts;
- active-list slots, indexes, and the stored sentinel count;
- logical active count;
- numeric claim state: absent `0`, dormant `1`, or active `2`;
- total cohort USD value and user USD value; and
- permissionless prune and paused activation maintenance.

Only active claims contribute to NAV. Dormant balances remain physically reserved and remain available to explicit claims and redemptions. The activation floor is $0.10 and the retention floor is $0.05, both in 18-decimal USD. Deactivation changes list membership without sweeping a nonzero liability.

See [StabVault](../vaults/modules/StabVault.md) for aggregate-custody checks, capacity, automatic microscopic-residual handling, and exact lifecycle event reason codes.

## Vault and integration views

The host exports VaultData's share ledgers and one-based asset indexes along with:

- deposit data used by Teller;
- Lootbox share weight;
- user asset/amount enumeration for liquidation handling;
- user asset/balance enumeration for Lootbox and AuctionHouse;
- `getTotalAmountForVault(asset)` and
  `getTotalAmountForUser(user, asset)`, expressed in the stabilization asset;
- `getTotalValue(asset)` and `getTotalUserValue(user, asset)`, expressed as
  18-decimal USD value; and
- logical fund/asset retirement checks.

`userBalances` and `totalBalances` are shares. Use the four named aggregate
getters above when an amount or USD value is required. The `StabVault` module's
generic `valueToShares` and `sharesToValue` helpers are not exported by the
composed host and are absent from its ABI.

`doesVaultHaveAnyFunds` returns true when a registered stabilization asset has either nonzero shares or any nonzero claim pair, including dormant pairs. It does not scan arbitrary donated token custody.

## Pause, retirement, and recovery

Pausing blocks deposits, withdrawals, internal transfers, claims, redemptions,
and liquidation swaps. Pruning remains available, while activation
intentionally requires the paused state so an empty cohort can be repaired
without changing an existing cohort's NAV.

Switchboard can deregister an asset only after its shares and every active or dormant pair are gone. Both public recovery entry points remain in the ABI for interface compatibility but unconditionally revert with `recovery disabled`; there is no privileged sweep route.

The host has no position-migration or claim-liability-migration interface. Changing the preferred MissionControl pointer does not move shares, principal, reservations, or claim custody out of an old pool.

## Integration invariants

- Onboard token pricing and PriceDesk token scale before the asset enters strict NAV.
- Treat aggregate claim balances as custody reservations across cohorts.
- Use Teller's batch APIs, even for one claim or redemption.
- Drain or explicitly account for shares and every dormant/active claim pair before pool retirement.

<!-- BEGIN GENERATED API REFERENCE: StabilityPool -->
## Exact API reference

> Generated from `contracts/vaults/StabilityPool.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `claimManyFromStabilityPool(address _claimer, tuple[] _claims, address _caller, bool _shouldAutoDeposit, Addys _a)` | `4–5` | `_a` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, Addys _a)` | `3–4` | `_a` |
| `redeemManyFromStabilityPool(tuple[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen, Addys _a)` | `6–7` | `_a` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, Addys _a)` | `4–5` | `_a` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, Addys _a)` | `4–5` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `activateClaimAssets(address _stabAsset, address[] _claimAssets)` | `nonpayable` | — |
| `canAcceptLiquidationAsset(address _stabAsset, address _claimAsset)` | `view` | `bool` |
| `claimManyFromStabilityPool(address _claimer, (address,address,uint256)[] _claims, address _caller, bool _shouldAutoDeposit)` | `nonpayable` | `uint256` |
| `claimManyFromStabilityPool(address _claimer, (address,address,uint256)[] _claims, address _caller, bool _shouldAutoDeposit, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `claimableAssets(address arg0, uint256 arg1)` | `view` | `address` |
| `claimableBalances(address arg0, address arg1)` | `view` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount)` | `nonpayable` | `uint256` |
| `depositTokensInVault(address _user, address _asset, uint256 _amount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `deregisterUserAsset(address _user, address _asset)` | `nonpayable` | `bool` |
| `deregisterVaultAsset(address _asset)` | `nonpayable` | `bool` |
| `doesUserHaveBalance(address _user, address _asset)` | `view` | `bool` |
| `doesVaultHaveAnyFunds()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getClaimAssetState(address _stabAsset, address _claimAsset)` | `view` | `uint256` |
| `getNumActiveClaimAssets(address _stabAsset)` | `view` | `uint256` |
| `getNumUserAssets(address _user)` | `view` | `uint256` |
| `getNumVaultAssets()` | `view` | `uint256` |
| `getRipeHq()` | `view` | `address` |
| `getTotalAmountForUser(address _user, address _asset)` | `view` | `uint256` |
| `getTotalAmountForVault(address _asset)` | `view` | `uint256` |
| `getTotalUserValue(address _user, address _asset)` | `view` | `uint256` |
| `getTotalValue(address _asset)` | `view` | `uint256` |
| `getUserAssetAndAmountAtIndex(address _user, uint256 _index)` | `view` | `(address, uint256)` |
| `getUserAssetAtIndexAndHasBalance(address _user, uint256 _index)` | `view` | `(address, bool)` |
| `getUserLootBoxShare(address _user, address _asset)` | `view` | `uint256` |
| `getVaultDataOnDeposit(address _user, address _asset)` | `view` | `(bool,uint256,uint256,uint256)` |
| `indexOfAsset(address arg0)` | `view` | `uint256` |
| `indexOfClaimableAsset(address arg0, address arg1)` | `view` | `uint256` |
| `indexOfUserAsset(address arg0, address arg1)` | `view` | `uint256` |
| `isPaused()` | `view` | `bool` |
| `isSupportedVaultAsset(address _asset)` | `view` | `bool` |
| `isUserInVaultAsset(address _user, address _asset)` | `view` | `bool` |
| `numAssets()` | `view` | `uint256` |
| `numClaimableAssets(address arg0)` | `view` | `uint256` |
| `numUserAssets(address arg0)` | `view` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pruneClaimableAssets(address _stabAsset, address[] _claimAssets)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `redeemManyFromStabilityPool((address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `redeemManyFromStabilityPool((address,uint256)[] _redemptions, uint256 _greenAmount, address _recipient, address _caller, bool _shouldAutoDeposit, bool _shouldRefundSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `swapForLiquidatedCollateral(address _stabAsset, uint256 _stabAssetAmount, address _liqAsset, uint256 _liqAmountSent, address _recipient, address _greenToken, address _savingsGreenToken)` | `nonpayable` | `uint256` |
| `swapWithClaimableGreen(address _stabAsset, uint256 _greenAmount, address _liqAsset, uint256 _liqAmountSent, address _greenToken)` | `nonpayable` | `uint256` |
| `totalBalances(address arg0)` | `view` | `uint256` |
| `totalClaimableBalances(address arg0)` | `view` | `uint256` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount)` | `nonpayable` | `(uint256, bool)` |
| `transferBalanceWithinVault(address _asset, address _fromUser, address _toUser, uint256 _transferAmount, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |
| `userAssets(address arg0, uint256 arg1)` | `view` | `address` |
| `userBalances(address arg0, address arg1)` | `view` | `uint256` |
| `vaultAssets(uint256 arg0)` | `view` | `address` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient)` | `nonpayable` | `(uint256, bool)` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |

### Events

| Event | Fields |
| --- | --- |
| `AssetClaimedInStabilityPool` | `address user indexed, address stabAsset indexed, address claimAsset indexed, uint256 claimAmount, uint256 claimUsdValue, uint256 claimShares, bool isDepleted` |
| `ClaimAssetActivated` | `address stabAsset indexed, address claimAsset indexed, uint256 balance, uint256 activeCount` |
| `ClaimAssetDeactivated` | `address stabAsset indexed, address claimAsset indexed, uint256 balance, uint256 activeCount, uint256 reason` |
| `ClaimAssetLeftDormant` | `address stabAsset indexed, address claimAsset indexed, uint256 balance, uint256 activeCount, uint256 reason` |
| `StabilityPoolDeposit` | `address user indexed, address asset indexed, uint256 amount, uint256 shares` |
| `StabilityPoolTransfer` | `address fromUser indexed, address toUser indexed, address asset indexed, uint256 transferAmount, bool isFromUserDepleted, uint256 transferShares` |
| `StabilityPoolWithdrawal` | `address user indexed, address asset indexed, uint256 amount, bool isDepleted, uint256 shares` |
| `VaultPauseModified` | `bool isPaused` |

<!-- END GENERATED API REFERENCE: StabilityPool -->
