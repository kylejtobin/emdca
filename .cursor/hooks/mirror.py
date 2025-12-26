"""
The Architect's Mirror
======================

A self-correcting feedback loop for EMDCA compliance.

Architecture:
    1. DOMAIN: Pure AST analysis logic (SignalDetector).
    2. SERVICE: Orchestration of file reading and rule loading (MirrorExecutor).
    3. SHELL: CLI/Hook entry point.

Constraints:
    - Pure Logic: AST traversal and signal generation.
    - Impure Shell: File I/O, System Exit.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import re
import sys
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, NewType, TextIO

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    RootModel,
    ValidationError,
)

# =============================================================================
# 1. DOMAIN (Types & Logic)
# =============================================================================


class PatternId(StrEnum):
    P00_MASTER = "00"
    P01_FACTORY = "01"
    P02_STATE = "02"
    P03_RAILWAY = "03"
    P04_EXECUTION = "04"
    P05_CONFIG = "05"
    P06_STORAGE = "06"
    P07_TRANSLATION = "07"
    P08_ORCHESTRATOR = "08"
    P09_WORKFLOW = "09"
    P10_INFRA = "10"


class SignalKind(StrEnum):
    SERVICE_IDENTITY = "service_identity"
    DOMAIN_IDENTITY = "domain_identity"
    SERVICE_IN_DOMAIN = "service_in_domain"
    VALIDATE_FUNCTION = "validate_function"
    TRY_BLOCK = "try_block"
    RAISE_STMT = "raise_stmt"
    AWAIT_EXPR = "await_expr"
    PRIMITIVE_TYPE = "primitive_type"
    FIELD_DEFAULT = "field_default"
    BOOLEAN_FLAG = "boolean_flag"


SignalHint = NewType("SignalHint", str)


class AnalysisContext(BaseModel):
    """Context for the analysis logic."""

    model_config = {"frozen": True}
    file_path: Path

    @property
    def is_domain(self) -> bool:
        return "domain" in self.file_path.parts

    @property
    def is_service(self) -> bool:
        return "service" in self.file_path.parts


class Signal(BaseModel):
    """A detected violation of EMDCA principles."""

    model_config = {"frozen": True}
    kind: SignalKind
    pattern_id: PatternId
    line: PositiveInt
    content: str
    hint: SignalHint


class RuleRef(BaseModel):
    """Reference to an architectural rule."""

    model_config = {"frozen": True}
    pattern_id: PatternId
    name: str
    globs: tuple[str, ...]

    def matches(self, path: Path) -> bool:
        path_str = str(path)
        for g in self.globs:
            p = g.replace("**", "*")
            if fnmatch.fnmatch(path_str, f"*{p}") or fnmatch.fnmatch(path_str, p):
                return True
        return False


# --- PURE LOGIC: Signal Detection ---


class SignalDetector:
    """Pure Domain Service: Maps AST Nodes to Signals."""

    @staticmethod
    def check_node(
        node: ast.AST, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        """Dispatch node to specific checks."""
        if isinstance(node, ast.ClassDef):
            return SignalDetector._check_class(node, context, get_line)
        if isinstance(node, ast.FunctionDef):
            return SignalDetector._check_function(node, context, get_line)
        if isinstance(node, ast.Try):
            return SignalDetector._check_try(node, context, get_line)
        if isinstance(node, ast.Raise):
            return SignalDetector._check_raise(node, context, get_line)
        if isinstance(node, ast.Await):
            return SignalDetector._check_await(node, context, get_line)
        if isinstance(node, ast.AnnAssign):
            return SignalDetector._check_annotation(node, context, get_line)
        return None

    @staticmethod
    def _check_class(
        node: ast.ClassDef, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # 1. Service Identity Violation: Service Class inheriting BaseModel
        if context.is_service:
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "BaseModel":
                    return Signal(
                        kind=SignalKind.SERVICE_IDENTITY,
                        pattern_id=PatternId.P00_MASTER,
                        line=node.lineno,
                        content=get_line(node.lineno),
                        hint=SignalHint(
                            "Service classes must be Plain Classes, not Pydantic Models."
                        ),
                    )

        # 2. Domain Identity Violation: Domain Object NOT inheriting BaseModel (or Enum/Exception)
        if context.is_domain:
            is_model = any(
                (isinstance(b, ast.Name) and b.id == "BaseModel") for b in node.bases
            )
            is_enum = any(
                "Enum" in (b.id if isinstance(b, ast.Name) else "") for b in node.bases
            )
            is_exc = node.name.endswith("Error") or "Exception" in [
                b.id for b in node.bases if isinstance(b, ast.Name)
            ]

            if not is_model and not is_enum and not is_exc:
                return Signal(
                    kind=SignalKind.DOMAIN_IDENTITY,
                    pattern_id=PatternId.P00_MASTER,
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint(
                        "Domain objects must be Pydantic Models (Data) or Enums."
                    ),
                )

        # 3. Service Injection Violation: Service class defined in Domain
        if context.is_domain and re.search(
            r"(Service|Manager|Handler|Processor)$", node.name
        ):
            return Signal(
                kind=SignalKind.SERVICE_IN_DOMAIN,
                pattern_id=PatternId.P04_EXECUTION,
                line=node.lineno,
                content=get_line(node.lineno),
                hint=SignalHint(
                    "Service/Manager classes belong in service/, not domain/."
                ),
            )

        return None

    @staticmethod
    def _check_function(
        node: ast.FunctionDef, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # Pattern 01: Factory Naming
        if re.match(r"^(validate_|check_|verify_)", node.name):
            return Signal(
                kind=SignalKind.VALIDATE_FUNCTION,
                pattern_id=PatternId.P01_FACTORY,
                line=node.lineno,
                content=get_line(node.lineno),
                hint=SignalHint(
                    "Avoid validation functions. Use Parse-Don't-Validate via Types."
                ),
            )
        return None

    @staticmethod
    def _check_try(
        node: ast.Try, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # Pattern 03: No Try/Catch in Logic
        if context.is_domain:
            return Signal(
                kind=SignalKind.TRY_BLOCK,
                pattern_id=PatternId.P03_RAILWAY,
                line=node.lineno,
                content=get_line(node.lineno),
                hint=SignalHint(
                    "Avoid try/except in Domain. Use Result Types or Let it Crash."
                ),
            )
        return None

    @staticmethod
    def _check_raise(
        node: ast.Raise, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # Pattern 03: No Raise in Logic
        if context.is_domain:
            return Signal(
                kind=SignalKind.RAISE_STMT,
                pattern_id=PatternId.P03_RAILWAY,
                line=node.lineno,
                content=get_line(node.lineno),
                hint=SignalHint("Avoid raise in Domain. Return Failure Result Types."),
            )
        return None

    @staticmethod
    def _check_await(
        node: ast.Await, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # Pattern 04: Domain should be Pure (Synchronous)
        if context.is_domain:
            return Signal(
                kind=SignalKind.AWAIT_EXPR,
                pattern_id=PatternId.P04_EXECUTION,
                line=node.lineno,
                content=get_line(node.lineno),
                hint=SignalHint(
                    "Domain Logic should be Pure/Synchronous. Async/IO belongs in Shell."
                ),
            )
        return None

    @staticmethod
    def _check_annotation(
        node: ast.AnnAssign, context: AnalysisContext, get_line: Callable[[int], str]
    ) -> Signal | None:
        # Pattern 01: Primitive Types
        if context.is_domain:
            if isinstance(node.annotation, ast.Name) and node.annotation.id in (
                "str",
                "int",
                "float",
                "bool",
            ):
                return Signal(
                    kind=SignalKind.PRIMITIVE_TYPE,
                    pattern_id=PatternId.P01_FACTORY,
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint(
                        f"Primitive type '{node.annotation.id}' — use Value Object (e.g. Email, UserId)."
                    ),
                )
        return None


# =============================================================================
# 2. SERVICE (Orchestration & IO)
# =============================================================================


class FileScanner:
    """Service Class: Orchestrates scanning of a single file."""

    def __init__(self, rules: tuple[RuleRef, ...]):
        self.rules = rules

    def scan_file(self, path: Path, content: str) -> tuple[Signal, ...]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return ()

        lines = content.splitlines()

        def get_line(n: int) -> str:
            if 1 <= n <= len(lines):
                line_content = lines[n - 1].strip()
                return (
                    line_content[:60] + "..."
                    if len(line_content) > 60
                    else line_content
                )
            return ""

        context = AnalysisContext(file_path=path)
        signals: list[Signal] = []

        for node in ast.walk(tree):
            sig = SignalDetector.check_node(node, context, get_line)
            if sig:
                signals.append(sig)

        return tuple(signals)

    def get_applicable_rules(self, path: Path) -> tuple[RuleRef, ...]:
        return tuple(r for r in self.rules if r.matches(path))


# =============================================================================
# 3. SHELL (Entry Point)
# =============================================================================

# -- Hook Input Models (Discriminated Union) --


class FileEditInput(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["file_edit"]
    file_path: Path


class StopInput(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["stop"]
    status: Literal["completed", "aborted", "error"]


class EmptyInput(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["empty"]


# The Sum Type
HookInputType = Annotated[
    FileEditInput | StopInput | EmptyInput, Field(discriminator="kind")
]


class HookInput(RootModel[HookInputType]):
    """Parsed input from the hook (Polymorphic)."""

    root: HookInputType


# -- Hook Output Models --


class HookOutput(BaseModel):
    """Base class for all hook outputs."""

    model_config = {"frozen": True}


class MessageOutput(HookOutput):
    kind: Literal["message"] = "message"
    agent_message: str


class NoOutput(HookOutput):
    kind: Literal["no_output"] = "no_output"


class EditInput(BaseModel):
    """Internal model for the content to be edited."""

    model_config = {"frozen": True}
    file_path: Path
    content: str


def load_rules(rules_dir: Path) -> tuple[RuleRef, ...]:
    """Load rules from disk."""
    if not rules_dir.exists():
        return ()

    rules: list[RuleRef] = []
    for d in rules_dir.iterdir():
        if d.is_dir() and d.name.startswith("pattern-"):
            rule_path = d / "RULE.md"
            if rule_path.exists():
                content = rule_path.read_text(encoding="utf-8")
                # Parse globs (simple regex)
                m = re.search(r"globs:\s*\[(.*?)\]", content)
                globs: list[str] = []
                if m:
                    globs = [
                        g.strip().strip("'\"")
                        for g in m.group(1).split(",")
                        if g.strip()
                    ]

                # Parse ID
                pid = re.match(r"pattern-(\d+)", d.name)
                # Map regex match to Enum if possible, else default
                pid_str = pid.group(1) if pid else "00"
                # Simple lookup or default
                try:
                    pattern_id = PatternId(pid_str)
                except ValueError:
                    pattern_id = PatternId.P00_MASTER

                rules.append(
                    RuleRef(pattern_id=pattern_id, name=d.name, globs=tuple(globs))
                )
    return tuple(rules)


def parse_cli_args(args: list[str]) -> EditInput | None:
    """Parse CLI arguments."""
    try:
        path = Path(args[1])
        content = path.read_text(encoding="utf-8")
        return EditInput(file_path=path, content=content)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def parse_stdin(stdin: TextIO) -> EditInput | None:
    """Parse stdin as HookInput JSON."""
    if stdin.isatty():
        return None
    raw = stdin.read()
    if not raw:
        return None

    try:
        # Parse Don't Validate (Polymorphic)
        hook_input = HookInput.model_validate_json(raw)

        match hook_input.root:
            case FileEditInput(file_path=fp):
                content = fp.read_text(encoding="utf-8")
                return EditInput(file_path=fp, content=content)
            case StopInput() | EmptyInput():
                print(NoOutput().model_dump_json())
                return None

            # Exhaustiveness: Pyright might complain if we miss a case or if it can't infer union.
            # But with RootModel[Union], it should be safe.
            # Removing `case _` to prove exhaustiveness.
    except (ValidationError, json.JSONDecodeError):
        # Structural failure of hook input -> No Output
        return None

    return None


def main() -> None:
    # 1. Parse Input (Strategy Selection)
    cli_mode = len(sys.argv) > 1
    edit_input: EditInput | None = None

    if cli_mode:
        edit_input = parse_cli_args(sys.argv)
    else:
        edit_input = parse_stdin(sys.stdin)

    if not edit_input:
        return

    # 2. Wire Service
    repo_root = Path(__file__).parent.parent.parent
    rules_dir = repo_root / ".cursor" / "rules"
    rules = load_rules(rules_dir)
    scanner = FileScanner(rules)

    # 3. Execute
    signals = scanner.scan_file(edit_input.file_path, edit_input.content)
    applicable = scanner.get_applicable_rules(edit_input.file_path)

    if not signals and not applicable:
        if cli_mode:
            print("✅ No signals.")
        else:
            print(NoOutput().model_dump_json())
        return

    # 4. Format Output
    output_lines = [f"## Architect's Mirror: {edit_input.file_path.name}\n"]

    if signals:
        output_lines.append("### Signals Detected\n")
        for sig in signals:
            output_lines.append(f"- **Line {sig.line}** [{sig.kind}]: `{sig.content}`")
            output_lines.append(f"  - Hint: {sig.hint}")
            output_lines.append(f"  - Pattern: {sig.pattern_id}\n")

    if applicable:
        output_lines.append("\n### Applicable Patterns\n")
        for r in applicable:
            output_lines.append(f"- {r.name} (ID: {r.pattern_id})")

    msg = "\n".join(output_lines)

    if cli_mode:
        print(msg)
    else:
        print(MessageOutput(agent_message=msg).model_dump_json())


if __name__ == "__main__":
    main()
