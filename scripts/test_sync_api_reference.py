from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import sync_api_reference as api
from baseline_policy import validate_baseline_identity


SOURCE = """# @version 0.4.3

flag ActionType:
    FIRST
    SECOND

MAX_ROWS: constant(uint256) = 25
PUBLIC_LIMIT: public(constant(uint256)) = 5
OWNER: public(immutable(address))
records: public(HashMap[address, HashMap[uint256, Record]])
isPaused: public(bool)

struct Record:
    value: uint256

event Changed:
    user: indexed(address)

@deploy
def __init__(_owner: address):
    pass

@view
@external
def read(
    _user: address = msg.sender,
    _amount: uint256 = max_value(uint256),
) -> Record:
    assert _amount != 0  # dev: zero amount
    return empty(Record)
"""


MINIMAL_SOLIDITY_ABI = [
    {
        "type": "constructor",
        "inputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "ping",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "ok", "type": "bool"}],
        "stateMutability": "view",
    },
    {
        "type": "event",
        "name": "Pinged",
        "inputs": [
            {
                "name": "account",
                "type": "address",
                "indexed": True,
            }
        ],
        "anonymous": False,
    },
    {
        "type": "error",
        "name": "Failed",
        "inputs": [{"name": "code", "type": "uint256"}],
    },
]


FOUNDRY_CONFIG = """[profile.default]
solc_version = "0.8.26"
evm_version = "paris"
optimizer = true
optimizer_runs = 80000
via_ir = true
bytecode_hash = "none"
"""

MAIN_SOLIDITY = (
    "pragma solidity ^0.8.26;\n"
    'import {Dep} from "./lib/Dep.sol";\n'
    "contract Main is Dep {}\n"
)
DEP_SOLIDITY = "pragma solidity ^0.8.26;\ncontract Dep {}\n"


class ApiReferenceTests(unittest.TestCase):
    @staticmethod
    def _git_blob_id(content: str) -> str:
        payload = content.encode()
        return hashlib.sha1(
            f"blob {len(payload)}\0".encode() + payload
        ).hexdigest()

    def _composed_fixture(
        self, root: Path
    ) -> tuple[dict[str, object], dict[str, str], dict[str, str]]:
        abi_directory = root / "reference" / "abis"
        documentation_directory = root / "cross-chain"
        compiled_directory = root / "solidity" / "out" / "Main.sol"
        abi_directory.mkdir(parents=True)
        documentation_directory.mkdir(parents=True)
        compiled_directory.mkdir(parents=True)

        artifact_path = abi_directory / "Fixture.json"
        artifact_path.write_text(json.dumps(MINIMAL_SOLIDITY_ABI, indent=2) + "\n")
        (documentation_directory / "Fixture.md").write_text("# Fixture\n")

        sources = {
            "solidity/foundry.toml": FOUNDRY_CONFIG,
            "solidity/src/Main.sol": MAIN_SOLIDITY,
            "solidity/src/lib/Dep.sol": DEP_SOLIDITY,
        }
        blobs = {
            source_path: self._git_blob_id(content)
            for source_path, content in sources.items()
        }
        baseline: dict[str, object] = {
            "protocol_commit": "a" * 40,
            "composed_solidity_abis": {
                "Fixture": {
                    "contract_name": "Main",
                    "display_name": "Main 1.0.0",
                    "entry_source": "solidity/src/Main.sol",
                    "compiler_version": "0.8.26+commit.8a97fa7a",
                    "compiler_config_path": "solidity/foundry.toml",
                    "compiler_config_blob": blobs["solidity/foundry.toml"],
                    "artifact_path": "reference/abis/Fixture.json",
                    "artifact_sha256": hashlib.sha256(
                        artifact_path.read_bytes()
                    ).hexdigest(),
                    "compiled_artifact_path": "solidity/out/Main.sol/Main.json",
                    "documentation_path": "cross-chain/Fixture.md",
                    "source_blobs": {
                        path: blobs[path]
                        for path in (
                            "solidity/src/Main.sol",
                            "solidity/src/lib/Dep.sol",
                        )
                    },
                }
            },
        }
        return baseline, sources, blobs

    @staticmethod
    def _mock_git(
        sources: dict[str, str], blobs: dict[str, str]
    ) -> mock.Mock:
        def run_git(_repository: Path, *args: str) -> str:
            if args[0] == "show":
                source_path = args[1].split(":", 1)[1]
                return sources[source_path]
            if args[:2] == ("cat-file", "-t"):
                return "blob\n"
            if args[0] == "rev-parse":
                source_path = args[1].split(":", 1)[1]
                return blobs[source_path] + "\n"
            raise AssertionError(f"unexpected Git arguments: {args!r}")

        return mock.Mock(side_effect=run_git)

    @staticmethod
    def _set_reviewed_abi(
        root: Path, baseline: dict[str, object], abi: list[dict[str, object]]
    ) -> None:
        artifact_path = root / "reference" / "abis" / "Fixture.json"
        artifact_path.write_text(json.dumps(abi, indent=2) + "\n")
        configured = baseline["composed_solidity_abis"]
        assert isinstance(configured, dict)
        fixture = configured["Fixture"]
        assert isinstance(fixture, dict)
        fixture["artifact_sha256"] = hashlib.sha256(
            artifact_path.read_bytes()
        ).hexdigest()

    @staticmethod
    def _compiled_artifact(
        abi: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        selected_abi = copy.deepcopy(MINIMAL_SOLIDITY_ABI if abi is None else abi)
        metadata: dict[str, object] = {
            "language": "Solidity",
            "compiler": {"version": "0.8.26+commit.8a97fa7a"},
            "sources": {
                "src/Main.sol": {
                    "keccak256": "0x" + hashlib.sha256(MAIN_SOLIDITY.encode()).hexdigest()
                },
                "src/lib/Dep.sol": {
                    "keccak256": "0x" + hashlib.sha256(DEP_SOLIDITY.encode()).hexdigest()
                },
            },
            "settings": {
                "compilationTarget": {"src/Main.sol": "Main"},
                "evmVersion": "paris",
                "viaIR": True,
                "optimizer": {"enabled": True, "runs": 80000},
                "metadata": {"bytecodeHash": "none"},
            },
            "output": {"abi": copy.deepcopy(selected_abi)},
        }
        method_identifiers = {
            f"{item['name']}({','.join(api.canonical_type_list(item.get('inputs', [])))})": (
                f"{index:08x}"
            )
            for index, item in enumerate(selected_abi, start=1)
            if item.get("type") == "function"
        }
        return {
            "abi": selected_abi,
            "metadata": metadata,
            "rawMetadata": json.dumps(metadata, separators=(",", ":")),
            "methodIdentifiers": method_identifiers,
        }

    @staticmethod
    def _write_compiled_artifact(root: Path, payload: dict[str, object]) -> None:
        artifact_path = root / "solidity" / "out" / "Main.sol" / "Main.json"
        artifact_path.write_text(json.dumps(payload, indent=2) + "\n")

    def _load_composed_fixture(
        self,
        root: Path,
        baseline: dict[str, object],
        sources: dict[str, str],
        blobs: dict[str, str],
        *,
        compiled: bool = False,
        git_mock: mock.Mock | None = None,
    ) -> dict[str, dict[str, object]]:
        with (
            mock.patch.object(api, "DOCS_ROOT", root),
            mock.patch.object(api, "run_git", git_mock or self._mock_git(sources, blobs)),
            mock.patch.object(
                api,
                "git_show_bytes",
                side_effect=lambda _repo, _commit, path: sources[path].encode(),
            ),
            mock.patch.object(
                api,
                "cast_keccak256",
                side_effect=lambda data, *, field: (
                    "0x" + hashlib.sha256(data).hexdigest()
                ),
            ),
        ):
            return api.composed_solidity_abi_references(
                Path("/protocol"),
                baseline,
                root if compiled else None,
            )

    def test_structured_source_inventory(self) -> None:
        declarations = api.source_declarations(SOURCE)
        initializer = next(
            item for item in declarations["functions"] if item["initializer"]
        )
        function = next(item for item in declarations["functions"] if item["name"] == "read")

        self.assertEqual("__init__", initializer["name"])
        self.assertEqual("def __init__(_owner: address)", initializer["signature"])
        self.assertEqual("view", function["mutability"])
        self.assertFalse(function["signature"].startswith("def read( "))
        self.assertNotIn(", )", function["signature"])
        self.assertEqual("msg.sender", function["arguments"][0]["default"])
        self.assertEqual("max_value(uint256)", function["arguments"][1]["default"])
        self.assertIn(("records", ["address", "uint256"], "Record"), declarations["public_getters"])
        self.assertIn(("isPaused", [], "bool"), declarations["public_getters"])
        self.assertIn(("PUBLIC_LIMIT", [], "uint256"), declarations["public_getters"])
        self.assertEqual(1, declarations["public_getters"].count(("PUBLIC_LIMIT", [], "uint256")))
        self.assertIn(("OWNER", [], "address"), declarations["public_getters"])
        self.assertIn(("ActionType", ["FIRST", "SECOND"]), declarations["flags"])
        self.assertIn(("MAX_ROWS", "uint256", "25"), declarations["constants"])
        self.assertIn("zero amount", declarations["revert_reasons"])

    def test_bounded_string_and_bytes_public_getters_are_not_fixed_arrays(self) -> None:
        declarations = api.source_declarations(
            """NAME: public(String[64])
PAYLOADS: public(Bytes[32][2])
LOOKUP: public(HashMap[address, Bytes[64]])
"""
        )
        self.assertIn(("NAME", [], "String[64]"), declarations["public_getters"])
        self.assertIn(
            ("PAYLOADS", ["uint256"], "Bytes[32]"),
            declarations["public_getters"],
        )
        self.assertIn(
            ("LOOKUP", ["address"], "Bytes[64]"),
            declarations["public_getters"],
        )

    def test_optional_guide_renders_exact_defaults(self) -> None:
        declarations = api.source_declarations(SOURCE)
        catalog = {"read": [next(item for item in declarations["functions"] if item["name"] == "read")]}
        abi_functions = [
            {
                "type": "function",
                "name": "read",
                "inputs": [],
                "outputs": [],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "read",
                "inputs": [{"name": "_user", "type": "address"}],
                "outputs": [],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "read",
                "inputs": [
                    {"name": "_user", "type": "address"},
                    {"name": "_amount", "type": "uint256"},
                ],
                "outputs": [],
                "stateMutability": "view",
            },
        ]
        rendered = "\n".join(api.render_optional_argument_guide(abi_functions, catalog))
        self.assertIn("`_user = msg.sender`", rendered)
        self.assertIn("`_amount = max_value(uint256)`", rendered)

    def test_source_only_block_expands_default_argument_call_forms(self) -> None:
        declarations = api.source_declarations(SOURCE)
        catalog = {
            item["name"]: [item]
            for item in declarations["functions"]
            if item["external"]
        }
        rendered = api.render_api_block("Fixture", "contracts/Fixture.vy", SOURCE, None, catalog)
        self.assertIn("`read()`", rendered)
        self.assertIn("`read(address _user)`", rendered)
        self.assertIn("`read(address _user, uint256 _amount)`", rendered)
        self.assertIn("### Source-declared call forms", rendered)
        self.assertIn(
            "not canonical ABI signatures or selector-hash preimages", rendered
        )
        self.assertNotIn("### Source-declared selector arities", rendered)

    def test_source_only_provenance_lists_every_rendered_declaration_class(self) -> None:
        declarations = api.source_declarations(SOURCE)
        catalog = {
            item["name"]: [item]
            for item in declarations["functions"]
            if item["external"]
        }
        rendered = api.render_api_block(
            "Fixture", "contracts/Fixture.vy", SOURCE, None, catalog
        )
        for expected in (
            "deployment/module initializers",
            "default-argument call forms",
            "compiler-generated public getters",
            "events, flags, constants, structs",
            "source-declared revert reasons",
        ):
            self.assertIn(expected, rendered)

    def test_abi_paths_accepts_only_direct_json_children(self) -> None:
        listing = (
            "scripts/abis/Alpha.json\n"
            "scripts/abis/Beta.json\n"
            "scripts/abis/README.md\n"
        )
        with mock.patch.object(api, "run_git", return_value=listing) as runner:
            self.assertEqual(
                {
                    "Alpha": "scripts/abis/Alpha.json",
                    "Beta": "scripts/abis/Beta.json",
                },
                api.abi_paths(Path("/protocol"), "a" * 40),
            )
        runner.assert_called_once_with(
            Path("/protocol"),
            "ls-tree",
            "-r",
            "--name-only",
            "a" * 40,
            "scripts/abis",
        )

    def test_abi_paths_rejects_nested_json(self) -> None:
        listing = "scripts/abis/Alpha.json\nscripts/abis/archive/Beta.json\n"
        with (
            mock.patch.object(api, "run_git", return_value=listing),
            self.assertRaisesRegex(
                RuntimeError,
                r"nested ABI JSON paths.*scripts/abis/archive/Beta\.json",
            ),
        ):
            api.abi_paths(Path("/protocol"), "a" * 40)

    def test_abi_paths_rejects_duplicate_stems(self) -> None:
        listing = (
            "scripts/abis/archive/Alpha.json\n"
            "scripts/abis/legacy/Alpha.json\n"
        )
        with (
            mock.patch.object(api, "run_git", return_value=listing),
            self.assertRaisesRegex(RuntimeError, r"duplicate ABI stems.*Alpha"),
        ):
            api.abi_paths(Path("/protocol"), "a" * 40)

    def test_named_tuple_outputs_preserve_components(self) -> None:
        rendered = api.output_items(
            [
                {
                    "name": "config",
                    "type": "tuple",
                    "components": [
                        {"name": "asset", "type": "address"},
                        {
                            "name": "terms",
                            "type": "tuple",
                            "components": [{"name": "ltv", "type": "uint256"}],
                        },
                    ],
                }
            ]
        )
        self.assertEqual("`(address asset, (uint256 ltv) terms) config`", rendered)

    def test_source_return_inference_is_scoped_to_the_mapped_source(self) -> None:
        local = next(
            item for item in api.source_declarations(SOURCE)["functions"] if item["name"] == "read"
        )
        conflicting = dict(local, returns="uint256")
        abi = [
            {
                "type": "function",
                "name": "read",
                "inputs": [
                    {"name": "_user", "type": "address"},
                    {"name": "_amount", "type": "uint256"},
                ],
                "outputs": [{"name": "", "type": "tuple", "components": []}],
                "stateMutability": "view",
            },
            {
                "type": "event",
                "name": "Changed",
                "inputs": [{"name": "user", "type": "address", "indexed": True}],
            },
        ]
        rendered = api.render_api_block(
            "Fixture",
            "contracts/Fixture.vy",
            SOURCE,
            abi,
            {"read": [local, conflicting]},
        )
        self.assertIn("| `read(address _user, uint256 _amount)` | `view` | `()` | `Record` |", rendered)

    def test_source_link_is_normalized_after_h1(self) -> None:
        content = "# Page\n\nIntro.\n\n[📄 View Source Code](old)\n"
        updated = api.pin_source_link(content, "https://example.test/source")
        self.assertTrue(
            updated.startswith(
                "# Page\n\n[📄 View Source Code](https://example.test/source)\n\nIntro."
            )
        )
        self.assertNotIn("(old)", updated)
        self.assertNotIn("\n\n\n", updated)

    def test_testing_and_mock_sources_are_excluded(self) -> None:
        listing = "\n".join(
            [
                "contracts/core/Real.vy",
                "contracts/mock/Mock.vy",
                "contracts/testing/Harness.vy",
                "contracts/core/nested/mock/NestedMock.vy",
                "contracts/core/nested/testing/NestedHarness.vy",
                "interfaces/Real.vyi",
            ]
        )
        with mock.patch.object(api, "run_git", return_value=listing):
            self.assertEqual(
                ["contracts/core/Real.vy", "interfaces/Real.vyi"],
                api.first_party_vyper_paths(api.Path("/tmp/repo"), "a" * 40),
            )

    def test_solidity_import_parser_ignores_comments_and_string_literals(self) -> None:
        source = r'''
// import "./Commented.sol";
string constant TEXT = "import './Literal.sol';";
import "./Direct.sol";
import {Thing as RenamedThing} from
    "../Named.sol";
import "./Aliased.sol" as Aliased;
/* import "./Blocked.sol"; */
'''
        self.assertEqual(
            ("./Direct.sol", "../Named.sol", "./Aliased.sol"),
            api.solidity_import_paths(source),
        )
        with self.assertRaisesRegex(RuntimeError, "non-relative Solidity import"):
            api.resolve_solidity_import(
                "solidity/src/Main.sol", "@openzeppelin/contracts/Thing.sol"
            )
        with self.assertRaisesRegex(RuntimeError, "escapes source tree"):
            api.resolve_solidity_import(
                "solidity/src/Main.sol", "../../../Outside.sol"
            )

    def test_cast_keccak_runner_hashes_exact_source_bytes(self) -> None:
        source_bytes = b"line one\r\nline two\n\x00"
        completed = mock.Mock(stdout=("0x" + "12" * 32 + "\n").encode())
        with mock.patch.object(api.subprocess, "run", return_value=completed) as runner:
            self.assertEqual(
                "0x" + "12" * 32,
                api.cast_keccak256(source_bytes, field="fixture"),
            )
        runner.assert_called_once_with(
            ["cast", "keccak"],
            input=source_bytes,
            check=True,
            capture_output=True,
        )

        with mock.patch.object(
            api.subprocess, "run", return_value=mock.Mock(stdout=b"not-a-hash\n")
        ):
            with self.assertRaisesRegex(RuntimeError, "invalid digest"):
                api.cast_keccak256(source_bytes, field="fixture")

    def test_git_byte_runner_does_not_enable_text_newline_normalization(self) -> None:
        completed = mock.Mock(stdout=b"line one\r\nline two\n")
        with mock.patch.object(api.subprocess, "run", return_value=completed) as runner:
            self.assertEqual(
                completed.stdout,
                api.run_git_bytes(Path("/protocol"), "show", "a" * 40 + ":Main.sol"),
            )
        runner.assert_called_once_with(
            ["git", "-C", "/protocol", "show", "a" * 40 + ":Main.sol"],
            check=True,
            capture_output=True,
        )

    def test_baseline_policy_rejects_untrusted_branch(self) -> None:
        baseline = {
            "protocol_repository": "https://github.com/Ripe-Foundation/ripe-protocol",
            "protocol_branch": "rh",
            "protocol_commit": "a" * 40,
            "protocol_tree": "b" * 40,
        }
        validate_baseline_identity(baseline)
        baseline["protocol_branch"] = "feature/untrusted"
        with self.assertRaisesRegex(RuntimeError, "untrusted protocol_branch"):
            validate_baseline_identity(baseline)

    def test_ccip_inherited_reference_keeps_composed_boundary(self) -> None:
        content = (api.DOCS_ROOT / "cross-chain" / "BurnMintTokenPool151.md").read_text()
        abi = api.json.loads(
            (api.DOCS_ROOT / "reference" / "abis" / "BurnMintTokenPool151.json").read_text()
        )
        self.assertIn("## Exact composed ABI reference", content)
        for item in abi:
            if item["type"] in {"function", "event", "error"}:
                self.assertIn(f"`{item['name']}`", content)

        # Tuple members, return shapes, event field types/indexing, and error
        # arguments are part of the generated reference, not merely names.
        for required in (
            "bytes receiver",
            "bytes destTokenAddress",
            "uint256 destinationAmount",
            "uint64 remoteChainSelector",
            "uint256 minWaitInSeconds",
            "address tokenAddress",
        ):
            self.assertIn(required, content)

    def test_composed_solidity_renderer_preserves_struct_and_index_metadata(self) -> None:
        artifact = api.DOCS_ROOT / "reference" / "abis" / "BurnMintTokenPool151.json"
        rendered = api.render_composed_solidity_abi_block(
            "Fixture",
            {
                "abi": api.json.loads(artifact.read_text()),
                "artifact_path_resolved": artifact,
                "contract_name": "BurnMintTokenPool",
                "compiler_version": "0.8.26+commit.8a97fa7a",
            },
        )
        self.assertIn("(bytes receiver, uint64 remoteChainSelector", rendered)
        self.assertIn("(bytes destTokenAddress, bytes destPoolData)", rendered)
        self.assertIn("address sender indexed", rendered)
        self.assertIn("uint256 minWaitInSeconds", rendered)

    def test_composed_solidity_renderer_labels_anonymous_events(self) -> None:
        artifact = api.DOCS_ROOT / "reference" / "abis" / "BurnMintTokenPool151.json"
        abi = copy.deepcopy(MINIMAL_SOLIDITY_ABI)
        event = next(item for item in abi if item["type"] == "event")
        event["anonymous"] = True
        rendered = api.render_composed_solidity_abi_block(
            "Fixture",
            {
                "abi": abi,
                "artifact_path_resolved": artifact,
                "contract_name": "Main",
                "compiler_version": "0.8.26+commit.8a97fa7a",
            },
        )
        self.assertIn("`Pinged (anonymous)`", rendered)

    def test_solidity_inherited_api_claim_requires_explicit_source_mapping(self) -> None:
        source = "contract FutureStandalone { function ping() external {} }\n"
        unrelated = api.render_solidity_api_block(
            "solidity/src/FutureStandalone.sol", source
        )
        self.assertIn("does not claim inherited APIs", unrelated)
        self.assertNotIn("BurnMintTokenPool", unrelated)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            current_page = root / "cross-chain" / "FutureStandalone.md"
            inherited_page = root / "cross-chain" / "Inherited.md"
            current_page.parent.mkdir(parents=True)
            inherited_page.write_text("# Inherited\n")
            with mock.patch.object(api, "DOCS_ROOT", root):
                inherited = api.render_solidity_api_block(
                    "solidity/src/FutureStandalone.sol",
                    source,
                    documentation_path=current_page,
                    inherited_reference={
                        "contract_name": "InheritedPool",
                        "display_name": "InheritedPool 2.0",
                        "documentation_path_resolved": inherited_page,
                    },
                )
        self.assertIn(
            "[composed InheritedPool 2.0 reference](Inherited.md)", inherited
        )

        references = {"Known": {"contract_name": "InheritedPool"}}
        configured = api.configured_solidity_inherited_api_references(
            {
                "solidity_inherited_api_markers": {
                    "solidity/src/FutureStandalone.sol": "Known"
                }
            },
            ["solidity/src/FutureStandalone.sol"],
            references,
        )
        self.assertIs(references["Known"], configured["solidity/src/FutureStandalone.sol"])
        with self.assertRaisesRegex(RuntimeError, "undiscovered source"):
            api.configured_solidity_inherited_api_references(
                {
                    "solidity_inherited_api_markers": {
                        "solidity/src/Unknown.sol": "Known"
                    }
                },
                ["solidity/src/FutureStandalone.sol"],
                references,
            )

    def test_composed_loader_accepts_exact_recursive_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            references = self._load_composed_fixture(root, baseline, sources, blobs)
        self.assertEqual(["Fixture"], list(references))
        self.assertEqual(MINIMAL_SOLIDITY_ABI, references["Fixture"]["abi"])

    def test_composed_manifest_requires_exact_recursive_import_closure(self) -> None:
        for mutation, expected in (("missing", "missing="), ("extra", "extra=")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                baseline, sources, blobs = self._composed_fixture(root)
                configured = baseline["composed_solidity_abis"]
                assert isinstance(configured, dict)
                fixture = configured["Fixture"]
                assert isinstance(fixture, dict)
                source_blobs = fixture["source_blobs"]
                assert isinstance(source_blobs, dict)
                if mutation == "missing":
                    source_blobs.pop("solidity/src/lib/Dep.sol")
                else:
                    extra_path = "solidity/src/Extra.sol"
                    sources[extra_path] = "contract Extra {}\n"
                    blobs[extra_path] = self._git_blob_id(sources[extra_path])
                    source_blobs[extra_path] = blobs[extra_path]
                with self.assertRaisesRegex(
                    RuntimeError,
                    f"source manifest mismatch.*{expected}",
                ):
                    self._load_composed_fixture(root, baseline, sources, blobs)

    def test_composed_loader_checks_compiler_config_and_git_object_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            configured = baseline["composed_solidity_abis"]
            assert isinstance(configured, dict)
            fixture = configured["Fixture"]
            assert isinstance(fixture, dict)
            fixture["compiler_version"] = "0.8.27+commit.40a35a09"
            with self.assertRaisesRegex(RuntimeError, "compiler version/config mismatch"):
                self._load_composed_fixture(root, baseline, sources, blobs)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            normal_git = self._mock_git(sources, blobs)

            def non_blob(_repository: Path, *args: str) -> str:
                if args[:2] == ("cat-file", "-t"):
                    return "tree\n"
                return normal_git(_repository, *args)

            with self.assertRaisesRegex(RuntimeError, "is tree, not blob"):
                self._load_composed_fixture(
                    root,
                    baseline,
                    sources,
                    blobs,
                    git_mock=mock.Mock(side_effect=non_blob),
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            sources["solidity/foundry.toml"] = FOUNDRY_CONFIG.replace(
                "optimizer_runs = 80000\n", ""
            )
            blobs["solidity/foundry.toml"] = self._git_blob_id(
                sources["solidity/foundry.toml"]
            )
            configured = baseline["composed_solidity_abis"]
            assert isinstance(configured, dict)
            fixture = configured["Fixture"]
            assert isinstance(fixture, dict)
            fixture["compiler_config_blob"] = blobs["solidity/foundry.toml"]
            with self.assertRaisesRegex(RuntimeError, "incomplete compiler settings"):
                self._load_composed_fixture(root, baseline, sources, blobs)

    def test_composed_abi_schema_rejects_duplicates_and_unknown_fields(self) -> None:
        for mutation, expected in (
            ("duplicate", "duplicate composed Solidity ABI declaration"),
            ("identifier", "invalid ABI declaration name"),
            ("field", "unexpected ABI entry field"),
            ("parameter-field", "unexpected ABI parameter field"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                baseline, sources, blobs = self._composed_fixture(root)
                abi = copy.deepcopy(MINIMAL_SOLIDITY_ABI)
                function = next(item for item in abi if item["type"] == "function")
                if mutation == "duplicate":
                    abi.append(copy.deepcopy(function))
                elif mutation == "identifier":
                    function["name"] = "not-valid"
                elif mutation == "field":
                    function["unexpected"] = True
                else:
                    function["inputs"][0]["unexpected"] = True
                self._set_reviewed_abi(root, baseline, abi)
                with self.assertRaisesRegex(RuntimeError, expected):
                    self._load_composed_fixture(root, baseline, sources, blobs)

    def test_composed_loader_rejects_orphan_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            (root / "reference" / "abis" / "Orphan.json").write_text("[]\n")
            with self.assertRaisesRegex(RuntimeError, "unconfigured.*Orphan.json"):
                self._load_composed_fixture(root, baseline, sources, blobs)

    def test_fresh_compiled_artifact_is_compared_canonically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            reordered = list(reversed(copy.deepcopy(MINIMAL_SOLIDITY_ABI)))
            self._write_compiled_artifact(root, self._compiled_artifact(reordered))
            references = self._load_composed_fixture(
                root, baseline, sources, blobs, compiled=True
            )
            self.assertIsNotNone(
                references["Fixture"]["compiled_artifact_path_resolved"]
            )

            mismatched = copy.deepcopy(MINIMAL_SOLIDITY_ABI)
            function = next(item for item in mismatched if item["type"] == "function")
            function["outputs"][0]["type"] = "uint256"
            self._write_compiled_artifact(root, self._compiled_artifact(mismatched))
            with self.assertRaisesRegex(RuntimeError, "freshly compiled Solidity ABI mismatch"):
                self._load_composed_fixture(
                    root, baseline, sources, blobs, compiled=True
                )

    def test_fresh_compiled_artifact_binds_version_sources_settings_and_target(self) -> None:
        cases = (
            (
                "version",
                lambda payload: payload["metadata"]["compiler"].update(
                    {"version": "0.8.27+commit.40a35a09"}
                ),
                "compiled Solidity version mismatch",
            ),
            (
                "sources",
                lambda payload: payload["metadata"]["sources"].pop(
                    "src/lib/Dep.sol"
                ),
                "source-set mismatch",
            ),
            (
                "source-content",
                lambda payload: payload["metadata"]["sources"][
                    "src/Main.sol"
                ].update({"keccak256": "0x" + "00" * 32}),
                "source-content mismatch",
            ),
            (
                "settings",
                lambda payload: payload["metadata"]["settings"]["optimizer"].update(
                    {"runs": 1}
                ),
                "settings mismatch",
            ),
            (
                "target",
                lambda payload: payload["metadata"]["settings"].update(
                    {"compilationTarget": {"src/Main.sol": "Other"}}
                ),
                "target mismatch",
            ),
        )
        for name, mutate, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                baseline, sources, blobs = self._composed_fixture(root)
                payload = self._compiled_artifact()
                mutate(payload)
                payload["rawMetadata"] = json.dumps(
                    payload["metadata"], separators=(",", ":")
                )
                self._write_compiled_artifact(root, payload)
                with self.assertRaisesRegex(RuntimeError, expected):
                    self._load_composed_fixture(
                        root, baseline, sources, blobs, compiled=True
                    )

    def test_fresh_compiled_artifact_rejects_metadata_drift_and_selector_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            payload = self._compiled_artifact()
            raw_metadata = json.loads(payload["rawMetadata"])
            raw_function = next(
                item
                for item in raw_metadata["output"]["abi"]
                if item["type"] == "function"
            )
            raw_function["outputs"][0]["type"] = "uint256"
            payload["rawMetadata"] = json.dumps(raw_metadata, separators=(",", ":"))
            self._write_compiled_artifact(root, payload)
            with self.assertRaisesRegex(RuntimeError, "artifact/metadata ABI mismatch"):
                self._load_composed_fixture(
                    root, baseline, sources, blobs, compiled=True
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            baseline, sources, blobs = self._composed_fixture(root)
            abi = copy.deepcopy(MINIMAL_SOLIDITY_ABI)
            second_function = copy.deepcopy(
                next(item for item in abi if item["type"] == "function")
            )
            second_function["name"] = "pong"
            abi.append(second_function)
            self._set_reviewed_abi(root, baseline, abi)
            payload = self._compiled_artifact(abi)
            identifiers = payload["methodIdentifiers"]
            assert isinstance(identifiers, dict)
            identifiers["ping(address)"] = "12345678"
            identifiers["pong(address)"] = "12345678"
            self._write_compiled_artifact(root, payload)
            with self.assertRaisesRegex(RuntimeError, "selector collision"):
                self._load_composed_fixture(
                    root, baseline, sources, blobs, compiled=True
                )

    def test_generated_marker_names_cannot_collide_across_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first = root / "first.md"
            second = root / "second.md"
            first.write_text(
                "<!-- BEGIN GENERATED API REFERENCE: Same -->\n"
                "<!-- END GENERATED API REFERENCE: Same -->\n"
            )
            second.write_text(
                "<!-- BEGIN GENERATED API REFERENCE: Same -->\n"
                "<!-- END GENERATED API REFERENCE: Same -->\n"
            )
            with (
                mock.patch.object(api, "DOCS_ROOT", root),
                self.assertRaisesRegex(RuntimeError, "marker collision"),
            ):
                api.validate_generated_marker_topology(
                    {"contracts/Same.vy": first}, {second: "Same"}
                )

    def test_high_risk_defaults_are_rendered_in_generated_pages(self) -> None:
        teller = (api.DOCS_ROOT / "core" / "Teller.md").read_text()
        psm = (api.DOCS_ROOT / "treasury" / "EndaomentPSM.md").read_text()
        erc4626 = (api.DOCS_ROOT / "tokens" / "modules" / "Erc4626Token.md").read_text()

        for expected in (
            "`_canWithdraw = True`",
            "`_canBorrow = True`",
            "`_greenAmount = max_value(uint256)`",
            "`_isPaymentSavingsGreen = False`",
            "`_amount = max_value(uint256)`",
            "`_shouldStake = True`",
        ):
            self.assertIn(expected, teller)
        for expected in (
            "`_usdcAmount = max_value(uint256)`",
            "`_recipient = msg.sender`",
            "`_shouldFullSweep = False`",
        ):
            self.assertIn(expected, psm)
        for expected in (
            "_receiver: address = msg.sender",
            "_owner: address = msg.sender",
        ):
            self.assertIn(expected, erc4626)

    def test_source_returns_do_not_leak_between_same_named_functions(self) -> None:
        deleverage = (api.DOCS_ROOT / "core" / "Deleverage.md").read_text()
        credit = (api.DOCS_ROOT / "core" / "CreditEngine.md").read_text()
        ledger = (api.DOCS_ROOT / "core" / "Ledger.md").read_text()
        teller = (api.DOCS_ROOT / "core" / "Teller.md").read_text()

        for expected in (
            "| `setDeleverageBuffer(uint256 _bps)` | `nonpayable` | — | — |",
            "| `setDeleverageCooldown(uint256 _blocks)` | `nonpayable` | — | — |",
        ):
            self.assertIn(expected, deleverage)
        self.assertIn(
            "| `setBuybackRatio(uint256 _ratio)` | `nonpayable` | — | — |",
            credit,
        )
        self.assertIn(
            "| `setBadDebt(uint256 _amount)` | `nonpayable` | — | — |",
            ledger,
        )
        self.assertIn(
            "| `setLockedAccount(address _wallet, bool _shouldLock)` | `nonpayable` | — | — |",
            ledger,
        )
        self.assertIn(
            "| `setUserConfig()` | `nonpayable` | `bool` | `bool` |",
            teller,
        )


if __name__ == "__main__":
    unittest.main()
