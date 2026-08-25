# UndyLego interface

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/5c30234e855cd8cbb54d199aef48e5ee07538244/interfaces/UndyLego.vyi)

`UndyLego.vyi` is the integration boundary used when Ripe calls Underscore Lego
adapters for swaps, yield, mint/redeem, rewards, and liquidity operations.

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
## Exact source-declared API reference

> Generated from declarations in `interfaces/UndyLego.vyi`. This source has no tracked ABI under `scripts/abis`; the inventory therefore covers the functions, events, and structs declared by this source rather than claiming a composed host ABI.

### External functions declared by this source

| Source declaration | Accepted arities | Mutability | Returns |
| --- | --- | --- | --- |
| `def addLiquidity(_pool: address, _tokenA: address, _tokenB: address, _amountA: uint256, _amountB: uint256, _minAmountA: uint256, _minAmountB: uint256, _minLpAmount: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (address, uint256, uint256, uint256, uint256)` | `10–11` | `nonpayable` | `(address, uint256, uint256, uint256, uint256)` |
| `def addLiquidityConcentrated(_nftTokenId: uint256, _pool: address, _tokenA: address, _tokenB: address, _tickLower: int24, _tickUpper: int24, _amountA: uint256, _amountB: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, uint256, uint256)` | `12–13` | `nonpayable` | `(uint256, uint256, uint256, uint256, uint256)` |
| `def claimIncentives(_user: address, _rewardToken: address, _rewardAmount: uint256, _proofs: DynArray[bytes32, MAX_PROOFS], _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256)` | `4–5` | `nonpayable` | `(uint256, uint256)` |
| `def confirmMintOrRedeemAsset(_tokenIn: address, _tokenOut: address, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256)` | `4–5` | `nonpayable` | `(uint256, uint256)` |
| `def depositForYield(_asset: address, _amount: uint256, _vaultAddr: address, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, address, uint256, uint256)` | `5–6` | `nonpayable` | `(uint256, address, uint256, uint256)` |
| `def getAccessForLego(_user: address, _action: ActionType) -> (address, String[64], uint256)` | `2` | `view` | `(address, String[64], uint256)` |
| `def getUnderlyingAmountSafe(_vaultToken: address, _vaultTokenBalance: uint256) -> uint256` | `2` | `view` | `uint256` |
| `def getVaultTokenAmount(_asset: address, _assetAmount: uint256, _vaultToken: address) -> uint256` | `3` | `view` | `uint256` |
| `def mintOrRedeemAsset(_tokenIn: address, _tokenOut: address, _tokenInAmount: uint256, _minAmountOut: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, bool, uint256)` | `6–7` | `nonpayable` | `(uint256, uint256, bool, uint256)` |
| `def removeLiquidity(_pool: address, _tokenA: address, _tokenB: address, _lpToken: address, _lpAmount: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, uint256)` | `9–10` | `nonpayable` | `(uint256, uint256, uint256, uint256)` |
| `def removeLiquidityConcentrated(_nftTokenId: uint256, _pool: address, _tokenA: address, _tokenB: address, _liqToRemove: uint256, _minAmountA: uint256, _minAmountB: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256, bool, uint256)` | `9–10` | `nonpayable` | `(uint256, uint256, uint256, bool, uint256)` |
| `def swapTokens(_amountIn: uint256, _minAmountOut: uint256, _tokenPath: DynArray[address, MAX_TOKEN_PATH], _poolPath: DynArray[address, MAX_TOKEN_PATH - 1], _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, uint256, uint256)` | `5–6` | `nonpayable` | `(uint256, uint256, uint256)` |
| `def withdrawFromYield(_vaultToken: address, _amount: uint256, _extraData: bytes32, _recipient: address, _miniAddys: MiniAddys = empty(MiniAddys)) -> (uint256, address, uint256, uint256)` | `4–5` | `nonpayable` | `(uint256, address, uint256, uint256)` |

### Source-declared selector arities

Each row is one callable selector prefix created by the source declaration's trailing defaults.

| Selector declaration | Mutability | Returns |
| --- | --- | --- |
| `addLiquidity(address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData, address _recipient)` | `nonpayable` | `(address, uint256, uint256, uint256, uint256)` |
| `addLiquidity(address _pool, address _tokenA, address _tokenB, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, uint256 _minLpAmount, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(address, uint256, uint256, uint256, uint256)` |
| `addLiquidityConcentrated(uint256 _nftTokenId, address _pool, address _tokenA, address _tokenB, int24 _tickLower, int24 _tickUpper, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, uint256, uint256, uint256, uint256)` |
| `addLiquidityConcentrated(uint256 _nftTokenId, address _pool, address _tokenA, address _tokenB, int24 _tickLower, int24 _tickUpper, uint256 _amountA, uint256 _amountB, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256, uint256, uint256, uint256)` |
| `claimIncentives(address _user, address _rewardToken, uint256 _rewardAmount, DynArray[bytes32, MAX_PROOFS] _proofs)` | `nonpayable` | `(uint256, uint256)` |
| `claimIncentives(address _user, address _rewardToken, uint256 _rewardAmount, DynArray[bytes32, MAX_PROOFS] _proofs, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256)` |
| `confirmMintOrRedeemAsset(address _tokenIn, address _tokenOut, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, uint256)` |
| `confirmMintOrRedeemAsset(address _tokenIn, address _tokenOut, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256)` |
| `depositForYield(address _asset, uint256 _amount, address _vaultAddr, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, address, uint256, uint256)` |
| `depositForYield(address _asset, uint256 _amount, address _vaultAddr, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, address, uint256, uint256)` |
| `getAccessForLego(address _user, ActionType _action)` | `view` | `(address, String[64], uint256)` |
| `getUnderlyingAmountSafe(address _vaultToken, uint256 _vaultTokenBalance)` | `view` | `uint256` |
| `getVaultTokenAmount(address _asset, uint256 _assetAmount, address _vaultToken)` | `view` | `uint256` |
| `mintOrRedeemAsset(address _tokenIn, address _tokenOut, uint256 _tokenInAmount, uint256 _minAmountOut, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, uint256, bool, uint256)` |
| `mintOrRedeemAsset(address _tokenIn, address _tokenOut, uint256 _tokenInAmount, uint256 _minAmountOut, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256, bool, uint256)` |
| `removeLiquidity(address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidity(address _pool, address _tokenA, address _tokenB, address _lpToken, uint256 _lpAmount, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256, uint256, uint256)` |
| `removeLiquidityConcentrated(uint256 _nftTokenId, address _pool, address _tokenA, address _tokenB, uint256 _liqToRemove, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, uint256, uint256, bool, uint256)` |
| `removeLiquidityConcentrated(uint256 _nftTokenId, address _pool, address _tokenA, address _tokenB, uint256 _liqToRemove, uint256 _minAmountA, uint256 _minAmountB, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256, uint256, bool, uint256)` |
| `swapTokens(uint256 _amountIn, uint256 _minAmountOut, DynArray[address, MAX_TOKEN_PATH] _tokenPath, DynArray[address, MAX_TOKEN_PATH - 1] _poolPath, address _recipient)` | `nonpayable` | `(uint256, uint256, uint256)` |
| `swapTokens(uint256 _amountIn, uint256 _minAmountOut, DynArray[address, MAX_TOKEN_PATH] _tokenPath, DynArray[address, MAX_TOKEN_PATH - 1] _poolPath, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, uint256, uint256)` |
| `withdrawFromYield(address _vaultToken, uint256 _amount, bytes32 _extraData, address _recipient)` | `nonpayable` | `(uint256, address, uint256, uint256)` |
| `withdrawFromYield(address _vaultToken, uint256 _amount, bytes32 _extraData, address _recipient, MiniAddys _miniAddys)` | `nonpayable` | `(uint256, address, uint256, uint256)` |

### Flags declared by this source

Flag members are powers of two in declaration order; zero is the empty flag, and members may be combined with bitwise OR.

- `ActionType`
  - `TRANSFER = 1` (`1 << 0`)
  - `EARN_DEPOSIT = 2` (`1 << 1`)
  - `EARN_WITHDRAW = 4` (`1 << 2`)
  - `EARN_REBALANCE = 8` (`1 << 3`)
  - `SWAP = 16` (`1 << 4`)
  - `MINT_REDEEM = 32` (`1 << 5`)
  - `CONFIRM_MINT_REDEEM = 64` (`1 << 6`)
  - `ADD_COLLATERAL = 128` (`1 << 7`)
  - `REMOVE_COLLATERAL = 256` (`1 << 8`)
  - `BORROW = 512` (`1 << 9`)
  - `REPAY_DEBT = 1024` (`1 << 10`)
  - `REWARDS = 2048` (`1 << 11`)
  - `ETH_TO_WETH = 4096` (`1 << 12`)
  - `WETH_TO_ETH = 8192` (`1 << 13`)
  - `ADD_LIQ = 16384` (`1 << 14`)
  - `REMOVE_LIQ = 32768` (`1 << 15`)
  - `ADD_LIQ_CONC = 65536` (`1 << 16`)
  - `REMOVE_LIQ_CONC = 131072` (`1 << 17`)
  - `PAY_CHEQUE = 262144` (`1 << 18`)

### Constants declared by this source

- `MAX_TOKEN_PATH: uint256 = 5`
- `MAX_PROOFS: uint256 = 25`

### Structs declared by this source

- `MiniAddys(ledger: address, missionControl: address, legoBook: address, appraiser: address)`
- `SwapInstruction(legoId: uint256, amountIn: uint256, minAmountOut: uint256, tokenPath: DynArray[address, MAX_TOKEN_PATH], poolPath: DynArray[address, MAX_TOKEN_PATH - 1])`

<!-- END GENERATED API REFERENCE: UndyLego -->
