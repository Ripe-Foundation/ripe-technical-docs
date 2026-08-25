# TellerUtils

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/TellerUtils.vy)

## Purpose

`TellerUtils` centralizes validation and resolution helpers used by [Teller](./Teller.md). It is a policy helper, not a custody or accounting authority: Teller and the destination departments still enforce their own access controls and state transitions.

## Deposit validation

`validateOnDeposit` checks the current protocol, asset, vault, and user configuration. Depending on the caller and route, it validates:

- vault and asset registration and enablement;
- user/delegate deposit permission;
- available holder balance;
- per-user vault/asset-count limits;
- per-user and system deposit caps; and
- minimum resulting balances.

Registered Ripe depositors can bypass ordinary user limits for protocol
settlement flows. That helper branch returns the lesser of the request and the
selected holder's balance: Teller when `_areFundsHereAlready` is true, otherwise
the depositor. On the ordinary measured-deposit branch, already-held funds must
equal the requested amount instead of being silently clamped.
VaultMigrator establishes end-to-end migration exactness separately by checking
the resulting deposit and custody deltas.

## Withdrawal validation

Withdrawal helpers verify current vault resolution, caller authority, user configuration, balance, and CreditEngine's maximum safe withdrawal. A successful validation is local to the observed state; execution can still revert if a downstream balance or risk condition changes.

Vault resolution checks both the supplied address and ID. Callers should resolve current roles through MissionControl/VaultBook instead of assuming a permanent numeric ID.

## Underscore resolution

Underscore wallet, vault, Lego, and Earn-vault checks resolve the current MissionControl registry first and fail false when required topology is absent. In particular:

- `isUnderscoreAddr` resolves the current MissionControl address before testing membership;
- a current Underscore wallet owner satisfies `isUnderscoreOwnerOrLego`
  immediately; and
- otherwise, the delegated branch requires the caller to be either a current
  root Underscore-registry member or a current LegoBook member, plus the user's
  explicit `doesUndyLegoHaveAccess` grant.

Being an arbitrary Underscore-associated address is not sufficient to act for a user.

## Security and integration notes

- Helpers fail closed for missing or malformed current topology.
- Exact-held-funds validation protects the ordinary branch; protocol-depositor
  branches require the calling workflow's own post-custody invariants.
- Results are validation inputs, not durable permissions; mutation paths re-evaluate current state.

<!-- BEGIN GENERATED API REFERENCE: TellerUtils -->
## Exact API reference

> Generated from `contracts/core/TellerUtils.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `isUnderscoreAddr(address _addr, address _mc)` | `1–2` | `_mc` |
| `isUnderscoreOwnerOrLego(address _user, address _caller, address _mc)` | `2–3` | `_mc` |
| `isUnderscoreVault(address _user, address _mc)` | `1–2` | `_mc` |
| `isUnderscoreWallet(address _user, address _mc)` | `1–2` | `_mc` |
| `isUnderscoreWalletOrVault(address _addr, address _mc)` | `1–2` | `_mc` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `2–3` | `_mc` |
| `validateOnDeposit(address _asset, uint256 _amount, address _user, uint256 _vaultId, address _vaultAddr, address _depositor, bool _didAlreadyValidateSender, bool _areFundsHereAlready, tuple _d, Addys _a)` | `9–10` | `_a` |
| `validateOnWithdrawal(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId, address _caller, tuple _config, Addys _a)` | `7–8` | `_a` |

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `getVaultAddrAndId(address _asset, address _vaultAddr, uint256 _vaultId, address _vaultBook, address _missionControl)` | `view` | `(address, uint256)` |
| `isPaused()` | `view` | `bool` |
| `isUnderscoreAddr(address _addr)` | `view` | `bool` |
| `isUnderscoreAddr(address _addr, address _mc)` | `view` | `bool` |
| `isUnderscoreOwnerOrLego(address _user, address _caller)` | `view` | `bool` |
| `isUnderscoreOwnerOrLego(address _user, address _caller, address _mc)` | `view` | `bool` |
| `isUnderscoreVault(address _user)` | `view` | `bool` |
| `isUnderscoreVault(address _user, address _mc)` | `view` | `bool` |
| `isUnderscoreWallet(address _user)` | `view` | `bool` |
| `isUnderscoreWallet(address _user, address _mc)` | `view` | `bool` |
| `isUnderscoreWalletOrVault(address _addr)` | `view` | `bool` |
| `isUnderscoreWalletOrVault(address _addr, address _mc)` | `view` | `bool` |
| `isUnderscoreWalletOwner(address _user, address _caller)` | `view` | `bool` |
| `isUnderscoreWalletOwner(address _user, address _caller, address _mc)` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |
| `validateOnDeposit(address _asset, uint256 _amount, address _user, uint256 _vaultId, address _vaultAddr, address _depositor, bool _didAlreadyValidateSender, bool _areFundsHereAlready, (bool,uint256) _d)` | `view` | `uint256` |
| `validateOnDeposit(address _asset, uint256 _amount, address _user, uint256 _vaultId, address _vaultAddr, address _depositor, bool _didAlreadyValidateSender, bool _areFundsHereAlready, (bool,uint256) _d, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `uint256` |
| `validateOnWithdrawal(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId, address _caller, (bool,bool,bool,bool,uint256) _config)` | `view` | `uint256` |
| `validateOnWithdrawal(address _asset, uint256 _amount, address _user, address _vaultAddr, uint256 _vaultId, address _caller, (bool,bool,bool,bool,uint256) _config, (address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address) _a)` | `view` | `uint256` |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

### Structs declared by this source

- `DepositLedgerData(isParticipatingInVault: bool, numUserVaults: uint256)`
- `TellerDepositConfig(canDepositGeneral: bool, canDepositAsset: bool, doesVaultSupportAsset: bool, isUserAllowed: bool, perUserDepositLimit: uint256, globalDepositLimit: uint256, perUserMaxAssetsPerVault: uint256, perUserMaxVaults: uint256, canAnyoneDeposit: bool, minDepositBalance: uint256)`
- `TellerWithdrawConfig(canWithdrawGeneral: bool, canWithdrawAsset: bool, isUserAllowed: bool, canWithdrawForUser: bool, minDepositBalance: uint256)`

<!-- END GENERATED API REFERENCE: TellerUtils -->
