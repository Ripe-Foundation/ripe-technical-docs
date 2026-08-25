# AuctionHouseNFT

[📄 View Source Code](https://github.com/Ripe-Foundation/ripe-protocol/blob/4701c43613253fd12e33ac57aaa818caf09b5840/contracts/core/AuctionHouseNFT.vy)

## Contract surface

`AuctionHouseNFT` is a minimal department contract. Its constructor registers
the RipeHQ address and initializes the standard department module with no
GREEN-minting capability.

The contract exports the common Addys and DeptBasics interfaces, but defines no
NFT auction, liquidation, bidding, settlement, or custody operation.

An AuctionHouseNFT registry slot does not add NFT-liquidation behavior. The
contract exposes no NFT collateral operation.

## Security and lifecycle note

Only the standard inherited department administration and introspection
surface exists. There is no user action or auction state in this contract.

<!-- BEGIN GENERATED API REFERENCE: AuctionHouseNFT -->
## Exact API reference

> Generated from `contracts/core/AuctionHouseNFT.vy` and its tracked ABI. The ABI inventory includes inherited and exported module members and is the selector-facing reference.

### Constructor

- `constructor(address _ripeHq)`

### Functions

| Signature | Mutability | Returns |
| --- | --- | --- |
| `canMintGreen()` | `view` | `bool` |
| `canMintRipe()` | `view` | `bool` |
| `getAddys()` | `view` | `(address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address,address)` |
| `getRipeHq()` | `view` | `address` |
| `isPaused()` | `view` | `bool` |
| `pause(bool _shouldPause)` | `nonpayable` | — |
| `recoverFunds(address _recipient, address _asset)` | `nonpayable` | — |
| `recoverFundsMany(address _recipient, address[] _assets)` | `nonpayable` | — |

### Events

| Event | Fields |
| --- | --- |
| `DepartmentFundsRecovered` | `address asset indexed, address recipient indexed, uint256 balance` |
| `DepartmentPauseModified` | `bool isPaused` |

<!-- END GENERATED API REFERENCE: AuctionHouseNFT -->
