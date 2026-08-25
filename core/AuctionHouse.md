# AuctionHouse

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/AuctionHouse.vy)

## Purpose

`AuctionHouse` coordinates account liquidation, Stability Pool settlement, and block-priced fungible-collateral auctions. Users normally reach it through [Teller](./Teller.md); privileged lifecycle actions are controlled through the protocol address registry and Switchboard.

Liquidation is account-wide. Once an unhealthy account enters liquidation, its `inLiquidation` flag remains set while the protocol settles debt through direct Stability Pool swaps and, if necessary, auctions. An outstanding auction owns the next liquidation pass for that account.

## Liquidation flow

`liquidateUser` and `liquidateManyUsers` are callable only by Teller. A batch is bounded to 50 users. An entry is skipped when it cannot presently be liquidated—for example, when the user has no debt, is healthy, has quarantined collateral, is an Underscore Earn vault, or already has an outstanding auction.

For an eligible account, the implementation:

1. checkpoints debt and determines the executable liquidation amount;
2. marks the account as in liquidation;
3. calculates liquidation fees only when the account first enters the liquidation episode;
4. attempts target-value settlement against compatible Stability Pool
   liquidity, with exact collateral custody and a bounded payment tolerance;
5. starts auctions for remaining eligible collateral when debt health is not restored; and
6. updates Ledger state and emits settlement or auction events.

If the entry pass produces neither repayment nor an auction, the calculated
fees are reset to zero. Retry passes do not charge them later. Stability Pool
settlement is fail-closed: the pool must preflight the asset, collateral custody
must match exactly, and payment must be within the source's one-percent
tolerance of the requested amount. A transfer that produces zero debt credit
reverts rather than silently consuming collateral.

Quarantine prevents a new or retrying `liquidateUser` pass from proceeding. It
does not clear or pause a fungible auction that was already active. That
auction's purchase path does not recompute account-wide quarantine and may
continue when the auction record, debt, collateral transfer, price, buyer
permissions, and settlement remain executable. Repayment through CreditEngine
remains available for restoring debt health.

## Fungible auctions

Switchboard can call `startAuction`, `startManyAuctions`, `pauseAuction`, and `pauseManyAuctions`. An auction can start only for a registered vault balance belonging to an account already in liquidation. Asset-specific settings override the general liquidation configuration where configured.

The active purchase window is:

```text
startBlock <= block.number < endBlock
```

The discount increases over that interval and reaches its configured maximum on the last purchasable block. Purchases are capped by the account's current debt as well as the remaining auction collateral, so a previously observed quote is not an execution guarantee.

Public auction purchases use Teller's `buyManyFungibleAuctions` batch route,
which calls AuctionHouse's purchase entry point. A batch contains at most 20
purchases; a one-item batch handles a single purchase. Any unused GREEN is
returned to the actual payer, optionally as sGREEN according to the request.

Auction settlement preflights nonzero credit before moving collateral. If the post-transfer repayment would be zero, the transaction reverts atomically.

Switchboard's direct auction-start/restart surface is separate from the
ordinary `liquidateUser` pass: it requires an existing liquidation flag and a
nonzero registered-vault balance but does not itself recompute the account's
quarantine flag. Operators must not treat `canStartAuction` as a complete
account-health or price-readiness check.

## Expiry and restart

`removeExpiredFungibleAuction` is permissionless, but removes only an active
auction at or after its `endBlock`. It does not remove a paused, missing, or
unexpired auction. Removal also clears Ledger's auction membership. Switchboard
can then start a new auction when the account and collateral are still eligible.

## Other integration points

- `withdrawTokensFromVault` is callable only by Deleverage and supports exact collateral movement during deleveraging.
- `calcAmountOfDebtToRepayDuringLiq` is a hypothetical, fee-bearing risk calculation. It is not an executable quote and does not promise that a liquidation or auction will settle that amount.
- Vault classification and current protocol addresses are resolved through MissionControl/Addys. The source does not establish fixed current vault IDs.
- The constructor grants this department GREEN-minting capability for keeper
  rewards; ordinary auction refunds return GREEN already held by AuctionHouse.

## Main events

- `LiquidateUser`
- `CollateralSwappedWithStabPool`
- `FungibleAuctionUpdated`
- `FungibleAuctionPaused`
- `ExpiredFungibleAuctionRemoved`
- `FungAuctionPurchased`

Consumers should treat events as records of completed state transitions, not as substitutes for current Ledger debt, auction, or vault state.

## Security properties

- Department and Switchboard checks gate privileged entry points.
- Teller's public liquidation and purchase routes are nonreentrant, and AuctionHouse accepts those mutation entry points only from Teller.
- Exact collateral custody, bounded Stability payment tolerance, and nonzero-credit
  checks prevent partial or no-op accounting from silently consuming collateral.
- Debt is re-evaluated at settlement; stale front-end quotes cannot force
  overpayment.
- Account liquidation state and outstanding-auction membership prevent concurrent liquidation routes from independently owning the same debt.

<!-- BEGIN GENERATED API REFERENCE: AuctionHouse -->
## Exact API reference

> Generated from `contracts/core/AuctionHouse.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `buyFungibleAuction(address _liqUser, uint256 _vaultId, address _asset, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, Addys _a)` | `8–9` | `_a` |
| `buyManyFungibleAuctions(tuple[] _purchases, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, Addys _a)` | `6–7` | `_a` |
| `liquidateManyUsers(address[] _liqUsers, address _keeper, bool _wantsSavingsGreen, Addys _a)` | `3–4` | `_a` |
| `liquidateUser(address _liqUser, address _keeper, bool _wantsSavingsGreen, Addys _a)` | `3–4` | `_a` |
| `pauseAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset, Addys _a)` | `3–4` | `_a` |
| `pauseManyAuctions(tuple[] _auctions, Addys _a)` | `1–2` | `_a` |
| `startAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset, Addys _a)` | `3–4` | `_a` |
| `startManyAuctions(tuple[] _auctions, Addys _a)` | `1–2` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `buyFungibleAuction(address _liqUser, uint256 _vaultId, address _asset, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `buyFungibleAuction(address _liqUser, uint256 _vaultId, address _asset, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen)` | `nonpayable` | `uint256` |
| `buyManyFungibleAuctions((address,uint256,address,uint256)[] _purchases, uint256 _greenAmount, address _recipient, address _caller, bool _shouldTransferBalance, bool _shouldRefundSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `calcAmountOfDebtToRepayDuringLiq(address _user)` | `view` | `uint256` |
| `calcTargetRepayAmount(uint256 _debtAmount, uint256 _collateralValue, uint256 _targetLtv)` | `view` | `uint256` |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `canStartAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset)` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `isPaused()` | `view` | `bool` |
| `liquidateManyUsers(address[] _liqUsers, address _keeper, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `liquidateManyUsers(address[] _liqUsers, address _keeper, bool _wantsSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `liquidateUser(address _liqUser, address _keeper, bool _wantsSavingsGreen)` | `nonpayable` | `uint256` |
| `liquidateUser(address _liqUser, address _keeper, bool _wantsSavingsGreen, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `pauseAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset)` | `nonpayable` | `bool` |
| `pauseAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` |
| `pauseManyAuctions((address,uint256,address)[] _auctions)` | `nonpayable` | `uint256` |
| `pauseManyAuctions((address,uint256,address)[] _auctions, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `removeExpiredFungibleAuction(address _liqUser, uint256 _vaultId, address _asset)` | `nonpayable` | `bool` |
| `startAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset)` | `nonpayable` | `bool` |
| `startAuction(address _liqUser, uint256 _liqVaultId, address _liqAsset, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `bool` |
| `startManyAuctions((address,uint256,address)[] _auctions)` | `nonpayable` | `uint256` |
| `startManyAuctions((address,uint256,address)[] _auctions, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `uint256` |
| `withdrawTokensFromVault(address _user, address _asset, uint256 _amount, address _recipient, address _vaultAddr, bool _preflightSafeConversion, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `nonpayable` | `(uint256, bool)` |

### Events

| Event | Fields |
| --- | --- |
| `CollateralSwappedWithStabPool` | `address liqUser indexed, uint256 liqVaultId, address liqAsset indexed, uint256 collateralAmountOut, uint256 collateralValueOut, uint256 stabVaultId, address stabAsset indexed, address assetSwapped, uint256 amountSwapped, uint256 valueSwapped` |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |
| `ExpiredFungibleAuctionRemoved` | `address liqUser indexed, uint256 vaultId, address asset indexed` |
| `FungAuctionPurchased` | `address liqUser indexed, uint256 liqVaultId, address liqAsset indexed, uint256 greenSpent, address recipient indexed, address caller, uint256 collateralAmountSent, uint256 collateralUsdValueSent, bool isPositionDepleted, bool hasGoodDebtHealth` |
| `FungibleAuctionPaused` | `address liqUser indexed, uint256 vaultId, address asset indexed` |
| `FungibleAuctionUpdated` | `address liqUser indexed, uint256 vaultId, address asset indexed, uint256 startDiscount, uint256 maxDiscount, uint256 startBlock, uint256 endBlock, bool isNewAuction` |
| `LiquidateUser` | `address user indexed, uint256 totalLiqFees, uint256 targetRepayAmount, uint256 repayAmount, bool didRestoreDebtHealth, uint256 collateralValueOut, uint256 liqFeesUnpaid, uint256 numAuctionsStarted, uint256 keeperFee` |

### Structs declared by this source

- `AuctionBuyConfig(canBuyInAuctionGeneral: bool, canBuyInAuctionAsset: bool, isUserAllowed: bool, canAnyoneDeposit: bool)`
- `UserBorrowTerms(collateralVal: uint256, totalMaxDebt: uint256, debtTerms: cs.DebtTerms, lowestLtv: uint256, highestLtv: uint256, hasQuarantinedAsset: bool)`
- `UserDebt(amount: uint256, principal: uint256, debtTerms: cs.DebtTerms, lastTimestamp: uint256, inLiquidation: bool)`
- `VaultData(vaultId: uint256, vaultAddr: address, asset: address)`
- `GenLiqConfig(canLiquidate: bool, keeperFeeRatio: uint256, minKeeperFee: uint256, maxKeeperFee: uint256, ltvPaybackBuffer: uint256, genAuctionParams: cs.AuctionParams, priorityLiqAssetVaults: DynArray[VaultData, PRIORITY_LIQ_VAULT_DATA], priorityStabVaults: DynArray[VaultData, MAX_STAB_VAULT_DATA])`
- `AssetLiqConfig(hasConfig: bool, shouldBurnAsPayment: bool, shouldTransferToEndaoment: bool, shouldSwapInStabPools: bool, shouldAuctionInstantly: bool, customAuctionParams: cs.AuctionParams, specialStabPool: VaultData)`
- `FungibleAuction(liqUser: address, vaultId: uint256, asset: address, startDiscount: uint256, maxDiscount: uint256, startBlock: uint256, endBlock: uint256, isActive: bool)`
- `FungAuctionPurchase(liqUser: address, vaultId: uint256, asset: address, maxGreenAmount: uint256)`
- `FungAuctionConfig(liqUser: address, vaultId: uint256, asset: address)`

<!-- END GENERATED API REFERENCE: AuctionHouse -->
