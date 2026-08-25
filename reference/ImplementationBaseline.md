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

Vyper sources with any `mock` or `testing` path segment and vendored Chainlink
or OpenZeppelin Solidity are not separate component pages. The baseline maps
every covered production source to one documentation path. Validation fails on
an unmapped source, stale mapping, duplicate target, missing source object, or
invalid source link.

## Exact API inventories

Each Vyper component page ends with a generated API block. Where the protocol
tracks an ABI, the block includes the full selector-facing function and event
surface, including inherited and exported module members. Optional-selector
families are paired with source declarations so their exact default expressions
are retained, and source-named return types supplement tuple-heavy ABI output.
Sources without a tracked ABI receive a source-declared initializer, external
function, public getter, event, struct, flag, constant, mutability, accepted
arity, and explicit-revert-reason inventory.

At this baseline the protocol tracks 58 ABI artifacts. Fifty-seven are
source-compiled production ABIs checked by `scripts/export_abis.py`; the
`DefaultsBaseSepolia` artifact is a separately hash-pinned legacy artifact and
has no production component page.

First-party Solidity pages receive generated Ripe-specific source deltas. The
inherited Chainlink `BurnMintTokenPool 1.5.1` page receives a generated exact
ABI inventory from a separately compiled Solidity artifact. The baseline pins
that artifact's SHA-256 digest, full compiler version, compiler-configuration
blob, entry source, and every protocol source blob in its recursive import
closure. Validation independently derives that closure and rejects missing or
extra manifest entries. CI then rebuilds the source, verifies the compiler
metadata, settings, target, source set, and byte-exact source-content hashes,
and compares the compiled ABI with the reviewed artifact before checking the
generated page.

Verify the blocks against a local protocol clone:

```sh
protocol_repo=/path/to/ripe-protocol
forge build --root "$protocol_repo/solidity" --force --skip test
python3 scripts/sync_api_reference.py \
  --protocol-repo "$protocol_repo" \
  --compiled-artifact-root "$protocol_repo" \
  --check
```

Run the Markdown link, heading, fence, and published-navigation checks
and the tooling regression suite separately:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/check_markdown.py
```

The external-link checker makes live network requests and is advisory:

```sh
python3 scripts/check_external_links.py
```

It scans published pages, deduplicates their external targets, and skips the
exact commit-pinned protocol source links already covered by source/API parity.
Requests are restricted to the reviewed HTTPS host/path scope in the script.

CI validates the configured repository and branch against a checked-in trust
policy, fetches that trusted branch, proves the pinned commit remains its
ancestor, checks out the exact commit, and verifies its exact tree. It then
recompiles production Vyper ABIs and the composed Solidity ABI, compares them
with the tracked artifacts, and runs the tooling tests and both documentation
gates. Branch advancement therefore does not invalidate an otherwise
reproducible pin. CI emits a non-failing warning when the trusted branch has
advanced beyond the pin so maintainers can distinguish reproducibility from
currentness. The full validation also runs weekly. After successful validation
on a scheduled run, a push to `master`, or a manual dispatch, a separate
non-blocking job checks the published external links. That network job does not
run for pull-request or merge-group events.

The Solidity lane pins the same Foundry action revision and Foundry 1.3.5
release used by the protocol CI; `foundry.toml` pins Solidity 0.8.26 and its
compiler settings. A clean GitHub runner downloads those tools, so this is a
reproducible online CI check rather than an air-gapped, repository-only build.

To move the baseline deliberately, update `implementation-baseline.json`, run
the API generator with `--write`, review every affected behavior section, and
rerun all checks. When a composed Solidity input changes, also build the exact
protocol checkout, extract the `BurnMintTokenPool` ABI from the compiler
artifact, and update its SHA-256, compiler identity/config blob, entry source,
compiled-artifact path, and complete source-blob manifest before regeneration.

## Published filename stability

Existing top-level filenames such as `CurrentImplementation.md` and
`Deployments.md` are retained to preserve established GitBook URLs even when
their visible titles and navigation labels evolve. Renaming them requires an
explicit URL migration and redirect plan.
