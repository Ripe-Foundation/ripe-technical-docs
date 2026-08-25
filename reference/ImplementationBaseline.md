# Documentation maintenance

This contributor-only page explains how the generated API inventories are
bound to protocol source. It is intentionally omitted from the published
navigation.

The machine-readable source identity and source-to-page map live in
[`implementation-baseline.json`](implementation-baseline.json). The baseline
pins a repository, branch, commit, and tree so documentation generation is
reproducible even while the protocol branch advances.

## Source coverage

The contract sweep covers:

- all non-mock Vyper sources under `contracts/config`, `contracts/core`,
  `contracts/data`, `contracts/modules`, `contracts/priceSources`,
  `contracts/registries`, `contracts/tokens`, and `contracts/vaults`;
- all first-party Vyper interfaces under `interfaces`; and
- the top-level first-party Solidity contracts configured in the baseline.

Mocks, test contracts, and vendored Chainlink or OpenZeppelin Solidity are not
separate component pages. The baseline maps every covered production source to
one documentation path. Validation fails on an unmapped source, stale mapping,
duplicate target, missing source object, or invalid source link.

## Exact API inventories

Each Vyper component page ends with a generated API block. Where the protocol
tracks an ABI, the block includes the full selector-facing function and event
surface, including inherited and exported module members. Sources without a
tracked ABI receive a source-declared external-function, event, and struct
inventory.

First-party Solidity pages receive generated inventories for constructors and
functions declared directly in the configured source. Inherited dependency APIs
are outside that source-declared inventory.

Verify the blocks against a local protocol clone:

```sh
python3 scripts/sync_api_reference.py \
  --protocol-repo /path/to/ripe-protocol \
  --check
```

Run the Markdown link, heading, fence, and published-navigation checks
separately:

```sh
python3 scripts/check_markdown.py
```

CI resolves the configured branch, requires its commit and tree to match the
baseline, recompiles production Vyper ABIs, compares them byte-for-byte with
the tracked artifacts, and then runs both documentation gates.

To move the baseline deliberately, update `implementation-baseline.json`, run
the API generator with `--write`, review every affected behavior section, and
rerun all checks.
