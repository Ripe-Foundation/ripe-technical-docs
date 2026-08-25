# UndyLego interface

`UndyLego.vyi` is the integration boundary used when Ripe calls Underscore Lego
adapters for swaps, yield, mint/redeem, rewards, and liquidity operations.

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/interfaces/UndyLego.vyi)

## Shared data

`MiniAddys` carries the Underscore Ledger, MissionControl, LegoBook, and
Appraiser addresses. Callers may pass an empty struct and let the implementation
resolve addresses according to its own rules.

`SwapInstruction` contains a Lego ID, exact input amount, minimum output, token
path, and pool path. Token paths are bounded to five tokens and pool paths to
one fewer entry. Reward proofs are bounded to 25.

## Action categories

The `ActionType` flag covers transfer, yield deposit/withdraw/rebalance, swap,
mint/redeem and confirmation, collateral add/remove, borrow/repay, rewards,
ETH/WETH conversion, ordinary and concentrated liquidity add/remove, and cheque
payment.

## Adapter surface

The interface exposes:

- ordinary and concentrated liquidity add/remove;
- asset mint/redeem and confirmation;
- token swaps;
- yield deposit and withdrawal;
- incentive claims;
- Lego access discovery; and
- safe underlying/vault-token conversion views.

Most state-changing methods accept a recipient plus optional `MiniAddys` and
return measured amounts, identifiers, or success flags. The exact tuple meanings
and custody guarantees belong to the selected Lego implementation; integrations
must use the exact API inventory rather than infer them from a similarly named
adapter.

## Trust boundary

MissionControl's `doesUndyLegoHaveAccess` checks Ripe user/delegate policy, while
the Underscore Lego and registries enforce their own permissions and accounting.
An address satisfying this interface is not by itself approved or current.

<!-- BEGIN GENERATED API REFERENCE: UndyLego -->
## Exact API reference

> Generated from declarations in `interfaces/UndyLego.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

- `def addLiquidity(_pool: address, _tokenA: address, _tokenB: address, _amountA: uint256, _amountB: uint256, _minAmountA: uint256, _minAmountB: uint256, _minLpAmount: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (address, uint256, uint256, uint256, uint256)`
- `def addLiquidityConcentrated(_nftTokenId: uint256, _pool: address, _tokenA: address, _tokenB: address, _tickLower: int24, _tickUpper: int24, _amountA: uint256, _amountB: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, uint256, uint256)`
- `def claimIncentives(_user: address, _rewardToken: address, _rewardAmount: uint256, _proofs: DynArray[bytes32, MAX_PROOFS], _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256)`
- `def confirmMintOrRedeemAsset(_tokenIn: address, _tokenOut: address, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256)`
- `def depositForYield(_asset: address, _amount: uint256, _vaultAddr: address, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, address, uint256, uint256)`
- `def getAccessForLego(_user: address, _action: ActionType) -> (address, String[64], uint256)`
- `def getUnderlyingAmountSafe(_vaultToken: address, _vaultTokenBalance: uint256) -> uint256`
- `def getVaultTokenAmount(_asset: address, _assetAmount: uint256, _vaultToken: address) -> uint256`
- `def mintOrRedeemAsset(_tokenIn: address, _tokenOut: address, _tokenInAmount: uint256, _minAmountOut: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, bool, uint256)`
- `def removeLiquidity(_pool: address, _tokenA: address, _tokenB: address, _lpToken: address, _lpAmount: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, uint256)`
- `def removeLiquidityConcentrated(_nftTokenId: uint256, _pool: address, _tokenA: address, _tokenB: address, _liqToRemove: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, bool, uint256)`
- `def swapTokens(_amountIn: uint256, _minAmountOut: uint256, _tokenPath: DynArray[address, MAX_TOKEN_PATH], _poolPath: DynArray[address, MAX_TOKEN_PATH - 1], _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256)`
- `def withdrawFromYield(_vaultToken: address, _amount: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, address, uint256, uint256)`

### Structs declared by this source

- `MiniAddys(ledger: address, missionControl: address, legoBook: address, appraiser: address)`
- `SwapInstruction(legoId: uint256, amountIn: uint256, minAmountOut: uint256, tokenPath: DynArray[address, MAX_TOKEN_PATH], poolPath: DynArray[address, MAX_TOKEN_PATH - 1])`

<!-- END GENERATED API REFERENCE: UndyLego -->
