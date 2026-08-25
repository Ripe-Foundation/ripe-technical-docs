# SwitchboardEcho

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/contracts/config/SwitchboardEcho.vy)

`SwitchboardEcho` is the governance and lite-action facade for Endaoment,
EndaomentPSM, vault migrations, and irreversible RipeGov point-accrual
disables.

## Vault migration facade

Governance can invoke the VaultMigrator through bounded routes:

- migrate RipeGov positions for up to 25 users from a source vault;
- migrate selected assets for one RipeGov user;
- migrate ordinary vault positions between source and target IDs for up to 25
  users;
- migrate selected assets for one ordinary-vault user; and
- migrate legacy Base RipeGov positions.

Selected-asset batches are capped at 20. Echo validates nonempty user/asset
inputs and nonzero vault IDs, while VaultMigrator enforces route, custody, and
position invariants. These migration calls are governance-only and immediate;
they are not `TimeLock` action types.

## Irreversible RipeGov point-accrual disable

Governance can propose either a global disable for a RipeGov vault or a
user-specific disable. These actions are timelocked because the underlying
vault operation is irreversible.

Proposal validation requires a registered VaultBook ID and a RipeGov-compatible
contract whose corresponding disable block is still zero. The proposal stores
both vault ID and resolved vault address. Execution revalidates eligibility and
requires the ID to resolve to the same address, preventing a registry
replacement from redirecting the queued action.

## Endaoment operations

Governance and lite signers can perform routine yield deposits/withdrawals,
ETH/WETH conversion, incentive claims, GREEN reference-pool stabilization,
transfers to EndaomentPSM or vaults, and PSM yield/funds maintenance.

Lite signers cannot call Endaoment directly. For the treasury-to-PSM route they
call `transferFundsToEndaomentPsmInEndaoment(amount)`. Echo checks governance or
MissionControl lite-action authority, then forwards to Endaoment as the
registered Switchboard.

Material treasury changes are governance-only and timelocked: arbitrary asset
transfer, swaps, liquidity add/remove, partner mint/pool operations, and pool
debt repayment. Partner-pool proposals include an explicit expected LP token,
which is forwarded and checked by Endaoment.

## EndaomentPSM configuration

PSM mint/redeem enablement, fees, interval caps, allowlist enforcement and
membership, yield position, interval length, and auto-deposit policy are routed
through Echo. Policy-changing operations create TimeLock actions; risk-reducing
disable directions may use lite access where the source explicitly permits it,
while enabling functionality requires governance.

## TimeLock behavior

Each queued action stores a typed payload. Governance executes or cancels it;
expired actions are cleared. State-sensitive point-disable and target binding
checks run again after the delay. Payloads and action-type tags are cleared on
execution or cancellation.

## Security boundaries

- Point-accrual disables are one-way and address-bound.
- Lite signers do not gain arbitrary transfer, swap, liquidity, migration, or
  irreversible-disable authority.
- The generated API reference defines the exact selector and event surface.

<!-- BEGIN GENERATED API REFERENCE: SwitchboardEcho -->
## Exact API reference

> Generated from `contracts/config/SwitchboardEcho.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq, address _tempGov, uint256 _minConfigTimeLock, uint256 _maxConfigTimeLock)`

### Optional-argument call guide

Vyper exposes one ABI selector for each accepted prefix of a default-argument call. Use the canonical full call below for readability; the exact selector table that follows retains every callable arity.

| Canonical full call | Accepted argument counts | Optional trailing arguments |
| --- | --- | --- |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData)` | `4–10` | `_amountA = max_value(uint256)`, `_amountB = max_value(uint256)`, `_minAmountA = 0`, `_minAmountB = 0`, `_minLpAmount = 0`, `_extraData = empty(bytes32)` |
| `claimIncentivesInEndaoment(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount, bytes32[] _proofs)` | `2–5` | `_rewardToken = empty(address)`, `_rewardAmount = max_value(uint256)`, `_proofs = []` |
| `convertEthToWethInEndaoment(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `convertWethToEthInEndaoment(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `depositForYieldInEndaoment(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount, bytes32 _extraData)` | `2–5` | `_vaultAddr = empty(address)`, `_amount = max_value(uint256)`, `_extraData = empty(bytes32)` |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `1–2` | `_timeLock = 0` |
| `mintPartnerLiquidityInEndaoment(address _partner, address _asset, uint256 _amount)` | `2–3` | `_amount = max_value(uint256)` |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData)` | `5–9` | `_lpAmount = max_value(uint256)`, `_minAmountA = 0`, `_minAmountB = 0`, `_extraData = empty(bytes32)` |
| `repayPoolDebtInEndaoment(address _pool, uint256 _amount)` | `1–2` | `_amount = max_value(uint256)` |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `0–1` | `_newTimeLock = 0` |
| `transferFundsToEndaomentPsmInEndaoment(uint256 _amount)` | `0–1` | `_amount = max_value(uint256)` |
| `withdrawFromYieldInEndaoment(uint256 _legoId, address _vaultToken, uint256 _amount, bytes32 _extraData)` | `2–4` | `_amount = max_value(uint256)`, `_extraData = empty(bytes32)` |
| `withdrawFromYieldInPsm(uint256 _amount, bool _shouldTransferToEndaoFunds, bool _shouldFullSweep)` | `0–3` | `_amount = max_value(uint256)`, `_shouldTransferToEndaoFunds = False`, `_shouldFullSweep = False` |

### Functions

| Signature | Mutability | ABI returns | Source return type |
| --- | --- | --- | --- |
| `actionId()` | `view` | `uint256` | — |
| `actionTimeLock()` | `view` | `uint256` | — |
| `actionType(uint256 arg0)` | `view` | `uint256` | — |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount)` | `nonpayable` | `uint256` | `uint256` |
| `addLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData)` | `nonpayable` | `uint256` | `uint256` |
| `addPartnerLiquidityInEndaoment(uint256 _legoId, address _pool, address _partner, address _asset, uint256 _amount, uint256 _minLpAmount, address _expectedLpToken)` | `nonpayable` | `uint256` | `uint256` |
| `canConfirmAction(uint256 _actionId)` | `view` | `bool` | — |
| `canGovern(address _addr)` | `view` | `bool` | — |
| `cancelGovernanceChange()` | `nonpayable` | — | — |
| `cancelPendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `claimIncentivesInEndaoment(address _user, uint256 _legoId)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentivesInEndaoment(address _user, uint256 _legoId, address _rewardToken)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentivesInEndaoment(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `claimIncentivesInEndaoment(address _user, uint256 _legoId, address _rewardToken, uint256 _rewardAmount, bytes32[] _proofs)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `confirmGovernanceChange()` | `nonpayable` | — | — |
| `convertEthToWethInEndaoment()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertEthToWethInEndaoment(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertWethToEthInEndaoment()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `convertWethToEthInEndaoment(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `depositForYieldInEndaoment(uint256 _legoId, address _asset)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYieldInEndaoment(uint256 _legoId, address _asset, address _vaultAddr)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYieldInEndaoment(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositForYieldInEndaoment(uint256 _legoId, address _asset, address _vaultAddr, uint256 _amount, bytes32 _extraData)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `depositToYieldInPsm()` | `nonpayable` | `uint256` | `uint256` |
| `disableRipeGovPointAccrualForUser(uint256 _vaultId, address _user)` | `nonpayable` | `uint256` | `uint256` |
| `disableRipeGovPointAccrualGlobally(uint256 _vaultId)` | `nonpayable` | `uint256` | `uint256` |
| `executePendingAction(uint256 _aid)` | `nonpayable` | `bool` | `bool` |
| `expiration()` | `view` | `uint256` | — |
| `finishRipeHqSetup(address _newGov)` | `nonpayable` | `bool` | — |
| `finishRipeHqSetup(address _newGov, uint256 _timeLock)` | `nonpayable` | `bool` | — |
| `getActionConfirmationBlock(uint256 _actionId)` | `view` | `uint256` | — |
| `getGovernors()` | `view` | `address[]` | — |
| `getRipeHqFromGov()` | `view` | `address` | — |
| `govChangeTimeLock()` | `view` | `uint256` | — |
| `governance()` | `view` | `address` | — |
| `hasPendingAction(uint256 _actionId)` | `view` | `bool` | — |
| `hasPendingGovChange()` | `view` | `bool` | — |
| `isExpired(uint256 _actionId)` | `view` | `bool` | — |
| `isValidActionTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidGovTimeLock(uint256 _newTimeLock)` | `view` | `bool` | — |
| `isValidRipeGovPointAccrualDisable(uint256 _vaultId, address _user)` | `view` | `bool` | `bool` |
| `maxActionTimeLock()` | `view` | `uint256` | — |
| `maxGovChangeTimeLock()` | `view` | `uint256` | — |
| `migrateLegacyRipeGovPositions(address[] _users)` | `nonpayable` | `uint256` | `uint256` |
| `migrateRipeGovPositions(address[] _users, uint256 _sourceVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateRipeGovPositionsForUserByAssets(address _user, address[] _assets, uint256 _sourceVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateVaultPositions(address[] _users, uint256 _sourceVaultId, uint256 _targetVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `migrateVaultPositionsForUserByAssets(address _user, address[] _assets, uint256 _sourceVaultId, uint256 _targetVaultId)` | `nonpayable` | `uint256` | `uint256` |
| `minActionTimeLock()` | `view` | `uint256` | — |
| `minGovChangeTimeLock()` | `view` | `uint256` | — |
| `mintPartnerLiquidityInEndaoment(address _partner, address _asset)` | `nonpayable` | `uint256` | `uint256` |
| `mintPartnerLiquidityInEndaoment(address _partner, address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `numGovChanges()` | `view` | `uint256` | — |
| `pendingActions(uint256 arg0)` | `view` | `(uint256 initiatedBlock, uint256 confirmBlock, uint256 expiration)` | — |
| `pendingEndaoAddLiquidityActions(uint256 arg0)` | `view` | `(uint256 legoId, address pool, address tokenA, address tokenB, uint256 amountA, uint256 amountB, uint256 minAmountA, uint256 minAmountB, uint256 minLpAmount, bytes32 extraData, address lpToken, uint256 lpAmount)` | — |
| `pendingEndaoPartnerMintActions(uint256 arg0)` | `view` | `(address partner, address asset, uint256 amount)` | — |
| `pendingEndaoPartnerPoolActions(uint256 arg0)` | `view` | `(uint256 legoId, address pool, address partner, address asset, uint256 amount, uint256 minLpAmount, address expectedLpToken)` | — |
| `pendingEndaoRemoveLiquidityActions(uint256 arg0)` | `view` | `(uint256 legoId, address pool, address tokenA, address tokenB, uint256 amountA, uint256 amountB, uint256 minAmountA, uint256 minAmountB, uint256 minLpAmount, bytes32 extraData, address lpToken, uint256 lpAmount)` | — |
| `pendingEndaoRepayActions(uint256 arg0)` | `view` | `(address pool, uint256 amount)` | — |
| `pendingEndaoSwapActions(uint256 arg0, uint256 arg1)` | `view` | `(uint256 legoId, uint256 amountIn, uint256 minAmountOut, address[] tokenPath, address[] poolPath)` | — |
| `pendingEndaoTransfer(uint256 arg0)` | `view` | `(address asset, uint256 amount)` | — |
| `pendingGov()` | `view` | `(address newGov, uint256 initiatedBlock, uint256 confirmBlock)` | — |
| `pendingPsmSetCanMintActions(uint256 arg0)` | `view` | `(bool canMint)` | — |
| `pendingPsmSetCanRedeemActions(uint256 arg0)` | `view` | `(bool canRedeem)` | — |
| `pendingPsmSetMaxIntervalMintActions(uint256 arg0)` | `view` | `(uint256 maxGreenAmount)` | — |
| `pendingPsmSetMaxIntervalRedeemActions(uint256 arg0)` | `view` | `(uint256 maxGreenAmount)` | — |
| `pendingPsmSetMintFeeActions(uint256 arg0)` | `view` | `(uint256 fee)` | — |
| `pendingPsmSetNumBlocksPerIntervalActions(uint256 arg0)` | `view` | `(uint256 blocks)` | — |
| `pendingPsmSetRedeemFeeActions(uint256 arg0)` | `view` | `(uint256 fee)` | — |
| `pendingPsmSetShouldAutoDepositActions(uint256 arg0)` | `view` | `(bool shouldAutoDeposit)` | — |
| `pendingPsmSetShouldEnforceMintAllowlistActions(uint256 arg0)` | `view` | `(bool shouldEnforce)` | — |
| `pendingPsmSetShouldEnforceRedeemAllowlistActions(uint256 arg0)` | `view` | `(bool shouldEnforce)` | — |
| `pendingPsmSetUsdcYieldPositionActions(uint256 arg0)` | `view` | `(uint256 legoId, address vaultToken)` | — |
| `pendingPsmUpdateMintAllowlistActions(uint256 arg0)` | `view` | `(address user, bool isAllowed)` | — |
| `pendingPsmUpdateRedeemAllowlistActions(uint256 arg0)` | `view` | `(address user, bool isAllowed)` | — |
| `pendingRipeGovPointAccrualDisableActions(uint256 arg0)` | `view` | `(uint256 vaultId, address vaultAddr, address user)` | — |
| `performEndaomentSwap((uint256,uint256,uint256,address[],address[])[] _instructions)` | `nonpayable` | `uint256` | `uint256` |
| `performEndaomentTransfer(address _asset, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `relinquishGov()` | `nonpayable` | — | — |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken)` | `nonpayable` | `uint256` | `uint256` |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount)` | `nonpayable` | `uint256` | `uint256` |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA)` | `nonpayable` | `uint256` | `uint256` |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB)` | `nonpayable` | `uint256` | `uint256` |
| `removeLiquidityInEndaoment(uint256 _legoId, address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData)` | `nonpayable` | `uint256` | `uint256` |
| `repayPoolDebtInEndaoment(address _pool)` | `nonpayable` | `uint256` | `uint256` |
| `repayPoolDebtInEndaoment(address _pool, uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `setActionTimeLock(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup()` | `nonpayable` | `bool` | — |
| `setActionTimeLockAfterSetup(uint256 _newTimeLock)` | `nonpayable` | `bool` | — |
| `setExpiration(uint256 _expiration)` | `nonpayable` | `bool` | — |
| `setGovTimeLock(uint256 _numBlocks)` | `nonpayable` | `bool` | — |
| `setPsmCanMint(bool _canMint)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmCanRedeem(bool _canRedeem)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmMaxIntervalMint(uint256 _maxGreenAmount)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmMaxIntervalRedeem(uint256 _maxGreenAmount)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmMintFee(uint256 _fee)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmNumBlocksPerInterval(uint256 _blocks)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmRedeemFee(uint256 _fee)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmShouldAutoDeposit(bool _shouldAutoDeposit)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmShouldEnforceMintAllowlist(bool _shouldEnforce)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmShouldEnforceRedeemAllowlist(bool _shouldEnforce)` | `nonpayable` | `uint256` | `uint256` |
| `setPsmUsdcYieldPosition(uint256 _legoId, address _vaultToken)` | `nonpayable` | `uint256` | `uint256` |
| `stabilizeGreenRefPoolInEndaoment()` | `nonpayable` | `bool` | `bool` |
| `startGovernanceChange(address _newGov)` | `nonpayable` | — | — |
| `transferFundsToEndaomentPsmInEndaoment()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToEndaomentPsmInEndaoment(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `transferFundsToVaultInEndaoment(address[] _assets)` | `nonpayable` | — | — |
| `transferUsdcToEndaomentFundsInPsm(uint256 _amount)` | `nonpayable` | `uint256` | `uint256` |
| `updatePsmMintAllowlist(address _user, bool _isAllowed)` | `nonpayable` | `uint256` | `uint256` |
| `updatePsmRedeemAllowlist(address _user, bool _isAllowed)` | `nonpayable` | `uint256` | `uint256` |
| `withdrawFromYieldInEndaoment(uint256 _legoId, address _vaultToken)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYieldInEndaoment(uint256 _legoId, address _vaultToken, uint256 _amount)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYieldInEndaoment(uint256 _legoId, address _vaultToken, uint256 _amount, bytes32 _extraData)` | `nonpayable` | `(uint256, address, uint256, uint256)` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYieldInPsm()` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `withdrawFromYieldInPsm(uint256 _amount)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `withdrawFromYieldInPsm(uint256 _amount, bool _shouldTransferToEndaoFunds)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |
| `withdrawFromYieldInPsm(uint256 _amount, bool _shouldTransferToEndaoFunds, bool _shouldFullSweep)` | `nonpayable` | `(uint256, uint256)` | `(uint256, uint256)` |

### Events

| Event | Fields |
| --- | --- |
| `ActionTimeLockSet` | `uint256 newTimeLock, uint256 prevTimeLock` |
| `EndaoAddLiquidityExecuted` | `uint256 legoId, address pool indexed, address tokenA indexed, address tokenB indexed` |
| `EndaoPartnerMintExecuted` | `address partner indexed, address asset indexed, uint256 greenMinted` |
| `EndaoPartnerPoolExecuted` | `uint256 legoId, address pool indexed, address partner indexed, address asset indexed` |
| `EndaoRemoveLiquidityExecuted` | `uint256 legoId, address pool indexed, address tokenA indexed, address tokenB indexed` |
| `EndaoRepayExecuted` | `address pool indexed, bool success` |
| `EndaoSwapExecuted` | `uint256 numSwapInstructions` |
| `EndaoTransferExecuted` | `address asset indexed, uint256 amount` |
| `EndaomentClaimPerformed` | `uint256 legoId, address rewardToken indexed, uint256 rewardAmount, uint256 usdValue, address caller indexed` |
| `EndaomentDepositPerformed` | `uint256 legoId, address asset indexed, address vault indexed, uint256 amount, address caller indexed` |
| `EndaomentEthToWethPerformed` | `uint256 amount, address caller indexed` |
| `EndaomentPsmDepositPerformed` | `uint256 amountDeposited, address caller indexed` |
| `EndaomentPsmTransferPerformed` | `uint256 amount, uint256 usdValue, address caller indexed` |
| `EndaomentPsmTransferToFundsPerformed` | `uint256 amount, address caller indexed` |
| `EndaomentPsmWithdrawPerformed` | `uint256 amountWithdrawn, uint256 amountTransferred, address caller indexed` |
| `EndaomentStabilizerPerformed` | `bool success, address caller indexed` |
| `EndaomentVaultTransferPerformed` | `uint256 numAssets, address caller indexed` |
| `EndaomentWethToEthPerformed` | `uint256 amount, address caller indexed` |
| `EndaomentWithdrawalPerformed` | `uint256 legoId, address asset indexed, address vaultAddr indexed, uint256 withdrawAmount, address caller indexed` |
| `ExpirationSet` | `uint256 expiration` |
| `GovChangeCancelled` | `address cancelledGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeConfirmed` | `address prevGov indexed, address newGov indexed, uint256 initiatedBlock, uint256 confirmBlock` |
| `GovChangeStarted` | `address prevGov indexed, address newGov indexed, uint256 confirmBlock` |
| `GovChangeTimeLockModified` | `uint256 prevTimeLock, uint256 newTimeLock` |
| `GovRelinquished` | `address prevGov indexed` |
| `PendingEndaoAddLiquidityAction` | `uint256 legoId, address pool indexed, address tokenA indexed, address tokenB indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoPartnerMintAction` | `address partner indexed, address asset indexed, uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoPartnerPoolAction` | `uint256 legoId, address pool indexed, address partner indexed, address asset indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoRemoveLiquidityAction` | `uint256 legoId, address pool indexed, address tokenA indexed, address tokenB indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoRepayAction` | `address pool indexed, uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoSwapAction` | `uint256 numSwapInstructions, uint256 confirmationBlock, uint256 actionId` |
| `PendingEndaoTransferAction` | `address asset indexed, uint256 amount, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetCanMintAction` | `bool canMint, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetCanRedeemAction` | `bool canRedeem, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetMaxIntervalMintAction` | `uint256 maxGreenAmount, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetMaxIntervalRedeemAction` | `uint256 maxGreenAmount, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetMintFeeAction` | `uint256 fee, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetNumBlocksPerIntervalAction` | `uint256 blocks, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetRedeemFeeAction` | `uint256 fee, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetShouldAutoDepositAction` | `bool shouldAutoDeposit, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetShouldEnforceMintAllowlistAction` | `bool shouldEnforce, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetShouldEnforceRedeemAllowlistAction` | `bool shouldEnforce, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmSetUsdcYieldPositionAction` | `uint256 legoId, address vaultToken indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmUpdateMintAllowlistAction` | `address user indexed, bool isAllowed, uint256 confirmationBlock, uint256 actionId` |
| `PendingPsmUpdateRedeemAllowlistAction` | `address user indexed, bool isAllowed, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeGovPointAccrualGlobalDisable` | `uint256 vaultId indexed, address vaultAddr indexed, uint256 confirmationBlock, uint256 actionId` |
| `PendingRipeGovPointAccrualUserDisable` | `uint256 vaultId indexed, address vaultAddr indexed, address user indexed, uint256 confirmationBlock, uint256 actionId` |
| `PsmSetCanMintExecuted` | `bool canMint` |
| `PsmSetCanRedeemExecuted` | `bool canRedeem` |
| `PsmSetMaxIntervalMintExecuted` | `uint256 maxGreenAmount` |
| `PsmSetMaxIntervalRedeemExecuted` | `uint256 maxGreenAmount` |
| `PsmSetMintFeeExecuted` | `uint256 fee` |
| `PsmSetNumBlocksPerIntervalExecuted` | `uint256 blocks` |
| `PsmSetRedeemFeeExecuted` | `uint256 fee` |
| `PsmSetShouldAutoDepositExecuted` | `bool shouldAutoDeposit` |
| `PsmSetShouldEnforceMintAllowlistExecuted` | `bool shouldEnforce` |
| `PsmSetShouldEnforceRedeemAllowlistExecuted` | `bool shouldEnforce` |
| `PsmSetUsdcYieldPositionExecuted` | `uint256 legoId, address vaultToken indexed` |
| `PsmUpdateMintAllowlistExecuted` | `address user indexed, bool isAllowed` |
| `PsmUpdateRedeemAllowlistExecuted` | `address user indexed, bool isAllowed` |
| `RipeGovPointAccrualGlobalDisableExecuted` | `uint256 vaultId indexed, address vaultAddr indexed` |
| `RipeGovPointAccrualUserDisableExecuted` | `uint256 vaultId indexed, address vaultAddr indexed, address user indexed` |
| `RipeHqSetupFinished` | `address prevGov indexed, address newGov indexed, uint256 timeLock` |

### Structs declared by this source

- `EndaoLiquidityAction(legoId: uint256, pool: address, tokenA: address, tokenB: address, amountA: uint256, amountB: uint256, minAmountA: uint256, minAmountB: uint256, minLpAmount: uint256, extraData: bytes32, lpToken: address, lpAmount: uint256)`
- `EndaoPartnerMintAction(partner: address, asset: address, amount: uint256)`
- `EndaoPartnerPoolAction(legoId: uint256, pool: address, partner: address, asset: address, amount: uint256, minLpAmount: uint256, expectedLpToken: address)`
- `EndaoRepayAction(pool: address, amount: uint256)`
- `EndaoTransfer(asset: address, amount: uint256)`
- `PsmSetCanMintAction(canMint: bool)`
- `PsmSetMintFeeAction(fee: uint256)`
- `PsmSetMaxIntervalMintAction(maxGreenAmount: uint256)`
- `PsmSetShouldEnforceMintAllowlistAction(shouldEnforce: bool)`
- `PsmUpdateMintAllowlistAction(user: address, isAllowed: bool)`
- `PsmSetCanRedeemAction(canRedeem: bool)`
- `PsmSetRedeemFeeAction(fee: uint256)`
- `PsmSetMaxIntervalRedeemAction(maxGreenAmount: uint256)`
- `PsmSetShouldEnforceRedeemAllowlistAction(shouldEnforce: bool)`
- `PsmUpdateRedeemAllowlistAction(user: address, isAllowed: bool)`
- `PsmSetUsdcYieldPositionAction(legoId: uint256, vaultToken: address)`
- `PsmSetNumBlocksPerIntervalAction(blocks: uint256)`
- `PsmSetShouldAutoDepositAction(shouldAutoDeposit: bool)`
- `RipeGovPointAccrualDisableAction(vaultId: uint256, vaultAddr: address, user: address)`

### Source-declared revert reasons

These are explicit source annotations or string reasons, not an exhaustive list of typed-call failures, arithmetic panics, or inherited-module reverts.

- `cannot cancel action`
- `invalid amount`
- `invalid asset`
- `invalid disable`
- `invalid global action`
- `invalid lego id`
- `invalid lp token`
- `invalid partner`
- `invalid pool`
- `invalid source vault id`
- `invalid user`
- `invalid user action`
- `invalid vault id`
- `no assets provided`
- `no migrations`
- `no perms`
- `no swap instructions provided`
- `vault binding changed`

<!-- END GENERATED API REFERENCE: SwitchboardEcho -->
