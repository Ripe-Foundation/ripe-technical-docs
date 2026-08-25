# Protocol architecture and contract behavior

This guide summarizes how the protocol's contracts compose. Each component
page remains the reference for its exact constructors, functions, arguments,
returns, events, and errors.

## System map

1. Users enter through `Teller`, which resolves departments and vaults through
   protocol registries and applies access, delegation, pause, and account-state
   checks.
2. Vaults custody or account for assets. `VaultBook` registers vaults, while
   `MissionControl` preserves historical Stability and RipeGov vault-role
   classifications used by positions, rewards, and migration.
3. `CreditEngine` derives account credit, debt terms, and liquidation state.
   `Ledger` stores shared positions, debt data, and action-block identities.
4. `PriceDesk` selects qualified sources, scales tokens through cached decimal
   data, and isolates external source calls. Specialized sources implement
   oracle, Curve, yield-token, or monitoring behavior.
5. `StabilityPool`, `AuctionHouse`, `CreditRedeem`, and `Deleverage` implement
   distinct paths for unhealthy positions and protocol debt.
6. `RipeHq`, `MissionControl`, `Switchboard`, and the specialized switchboards
   establish authority and configuration. Treasury, token, and vault contracts
   use the same registry and pause model.

## Account safety and liquidation

`CreditEngine` applies account-wide collateral quarantine. Positive-LTV
collateral is quarantined when a nominal position has no usable vault-wide
backing, or when a positive usable amount has no USD value because its price is
unavailable. Quarantined accounts cannot borrow, perform collateral-dependent
withdrawals, enter or retry the ordinary liquidation pass, redeem collateral,
or use deleverage routes that invoke quarantine checks until the backing or
price condition is restored.

Quarantine does not cancel an auction that is already active. Its purchase path
can continue while the auctioned asset and the rest of the transaction remain
executable. A zero-LTV asset follows the separate unrestricted CreditEngine
withdrawal branch, still bounded by the real vault balance and Teller/vault
checks. Repayment remains possible, and full repayment does not require a fresh
collateral-price read.

Liquidation state is account-wide. The retry path is available only when no
auction still owns the episode. Fungible-auction fees are charged once per
liquidation episode; retrying after auction expiry does not charge the fee
again. Expired fungible auctions can be removed permissionlessly at or after
`endBlock`. Auction, Stability Pool, and vault transfers enforce exact or
bounded custody and delivery before mutating credit.

`Deleverage` exposes batch, specific-asset, volatile-asset, swap, and withdrawal
flows. It re-reads debt before settlement and applies route-specific authority,
liquidation, quarantine, and cooldown checks. The general batch includes a
bounded permissionless branch: any caller may deleverage a non-liquidating,
non-quarantined account in the near-redemption zone, but repayment is capped at
the amount calculated to restore the configured target.

A registered Ripe caller, a registered Underscore self-call, or a cross-user
caller with `canBorrow` delegation uses the trusted general branch; an ordinary
EOA self-call alone does not. The specific-asset route requires self,
registered-Ripe, or `canBorrow` authority. Trusted general, specific-asset,
volatile-asset, and admitted withdrawal-time flows can operate during
liquidation. `swapCollateral` instead relies on its registered-Ripe-or-governance
caller boundary and does not run ordinary user delegation, quarantine, or
liquidation checks.

The batch and specific-asset Teller routes and the direct volatile and
withdrawal routes do not perform Teller housekeeping or write `lastTouch`.
`swapCollateral` is the exception: it performs low-risk housekeeping, which
writes the user's `lastTouch` without a same-action-block rejection. When both
configured debt-clear controls are zero, dust write-off is disabled.

## Stability Pool claim lifecycle

Claim assets have three states:

| State | Meaning |
| --- | --- |
| Absent (`0`) | No claim-asset record participates in the pool |
| Dormant (`1`) | Existing claims remain claimable and the asset is excluded from active NAV; a qualifying liquidation top-up can reactivate it after the activation condition is met |
| Active (`2`) | The asset participates in active NAV and can accept liquidation inventory, subject to the pool's guards |

The active set is capped at 20 assets and maintenance batches are capped at 15.
Activation uses a $0.10 value threshold; active retention uses $0.05. Dormant
activation is permissionless only while the pool is paused. Reservations use
unreserved custody and cannot reserve the Stability Pool asset itself. Claims
checkpoint rewards atomically.

The singular `claimFromStabilityPool` and `redeemFromStabilityPool` module
helpers and the generic `valueToShares` and `sharesToValue` helpers are not
exported by the composed `StabilityPool` host. The host exports
`getTotalAmountForUser`, `getTotalAmountForVault`, `getTotalUserValue`, and
`getTotalValue`. Standard Department `recoverFunds` selectors remain
ABI-visible but intentionally revert.

## Migration and historical roles

`MissionControl` stores mutable pointers for the preferred Stability Pool vault
and core RipeGov vault. Separate monotonic maps retain whether an ID has ever
held either role. Callers must not assume an initial ID remains current or
treat a rotated-out ID as an ordinary vault.

`VaultMigrator` is Switchboard-controlled. It validates registered and distinct
source and target vaults, compatible vault types, pauses, exact custody and
receipt, position depletion, reward and Lootbox state, and migration
housekeeping. User batches are capped at 25 and explicit asset lists at 20. The
automatic non-legacy RipeGov batch permits at most 20 registered asset slots per
user and 20 aggregate slots across the batch, including slots whose balance is
not moved or whose target route is unsupported. Historical RipeGov vaults are
excluded from the ordinary path.

RipeGov migration also carries lock terms, point state, and the irreversible
point-disable tombstone. `SwitchboardEcho` supplies immediate migration routes;
timelocked governance routes rotate mutable protocol pointers and revalidate
their candidates at execution.

## Teller interface and sentinel behavior

User-facing auction, Stability Pool claim and redeem, collateral redemption,
and deleverage actions use batch-capable selectors, including for a single
item. Teller also exposes five migrator-only routes for exact deposit,
withdrawal, position, and governance-state movement. Vault-ID-aware lock routes
support positions in both current and historical RipeGov vaults.

When a caller omits `setUserConfig` booleans, omitted values are written as
`false`; every call replaces all three fields instead of preserving omitted
prior values. Generic deposit and withdrawal calls interpret `_vaultId == 0`
as a request to select or resolve a configured vault. `adjustLock` and
`releaseLock` interpret zero as the current core RipeGov vault.

`lastTouch` behavior is route-specific: higher-risk housekeeping can reject a
prior touch in the same action block and then writes, low-risk housekeeping
writes without that duplicate-touch gate, and several third-party, batch, and
deleverage routes do not write for the target. Bond purchase includes
`minRipePayout`; its default is zero, so payout slippage protection is opt-in.
Omitted bond lock duration is zero and an omitted recipient is the caller.

Use [Teller](core/Teller.md) for the exact selector families, tuple shapes, and
sentinel semantics.

## Price routing and freshness

`PriceDesk` caches `tokenScale` values and supports token decimals from 0
through 77. A missing scale fails strictly or produces a fail-soft zero result,
depending on the route. A nonzero USD result that would otherwise round to zero
floors to one base unit. Price-source calls use bounded isolation so a broken
source cannot consume the entire routing attempt.

`ChainlinkPrices`, `PythPrices`, `RedStone`, and `StorkPrices` support local
freshness overrides with a global fallback. A feed-local zero inherits the
global window; a nonzero local value is an absolute override. Local values must
be between five minutes and seven days, and the effective or global window
cannot exceed seven days. Only `PriceDesk` may forward the global nonzero
value. Confirmation revalidates candidates, and future or stale observations
fail closed.

Pyth batch payloads use bounded `bytes[]`. Stork batch updates use typed
`TemporalNumericValueInput[]`. `BlueChipYieldPrices` and `UndyVaultPrices`
weight snapshots by elapsed time rather than token supply. Blue-chip validation
includes Morpho V2 ERC-4626 factory checks. `CurvePrices` validates pool
topology, rejects dependency cycles, and tracks both GREEN and alternate
balances in its stabilizer configuration.

`AeroRipePrices` and `UniswapV2Prices` are monitoring-only spot views. They
return no generic PriceDesk feed, expose no priced-asset set, and cannot be
configured as ordinary price sources. Their values are manipulable and must not
be used for lending, liquidation, minting, accounting, or other
security-sensitive decisions.

## Treasury, tokens, and vault accounting

`Endaoment.addPartnerLiquidity` has one seven-argument form with explicit
amount, minimum LP, and expected LP token. Normalized stabilizer balances and
delta accounting protect custody. `EndaomentPSM` begins with mint and redeem
directions disabled; Switchboard controls whether either direction is enabled
after construction.

Token approvals can be cleared or revoked while paused or blacklisted, while a
new nonzero allowance remains gated. Permit uses the 65-byte signature form.
ERC-4626 maximum-operation views return zero under blocking conditions and when
backing is zero. After RipeHq setup, token contracts expose their CCIP
administrator, and the first-party CCIP pools implement burn/mint movement
between chain-local token representations.

Protocol tokenomics define RIPE's total supply as one billion across chains.
Each `RipeToken` instance maintains only its chain-local ERC-20
`totalSupply`; the contracts do not maintain a cross-chain aggregate or enforce
the one-billion policy as a local token cap. See [RipeToken](tokens/RipeToken.md)
for the mint, burn, and cross-chain mechanics.

Basic and share vaults enforce real custody. Share accounting rejects
zero-share deposits, uses full-precision math, bounds tolerated transfer
deltas, and credits the lesser delivered amount. RipeGov lock and point
behavior is vault-ID-aware; voluntary actions honor locks while forced
liquidation can bypass them under the liquidation path's authority.
