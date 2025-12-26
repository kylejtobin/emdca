import importlib.util
import sys
from pathlib import Path
from typing import Any

# Load Mirror
REPO_ROOT = Path(__file__).parent.parent
MIRROR_PATH = REPO_ROOT / ".cursor" / "hooks" / "mirror.py"
RULES_DIR = REPO_ROOT / ".cursor" / "rules"

spec = importlib.util.spec_from_file_location("mirror", MIRROR_PATH)
if spec is None or spec.loader is None:
    raise ImportError("Could not load mirror module")

mirror: Any = importlib.util.module_from_spec(spec)
sys.modules["mirror"] = mirror
spec.loader.exec_module(mirror)


# Helper to setup scanner
def get_scanner() -> Any:
    rules = mirror.load_rules(RULES_DIR)
    return mirror.FileScanner(rules)


def verify_domain_rules() -> None:
    print("\nVerifying Domain Rules...")
    scanner = get_scanner()

    # 1. Valid Domain Model
    valid_path = REPO_ROOT / "tests/fixtures/domain/clean/valid_model.py"
    valid_content = valid_path.read_text()
    valid_signals = scanner.scan_file(valid_path, valid_content)

    if valid_signals:
        print(f"❌ FAIL: Valid domain model triggered signals: {valid_signals}")
    else:
        print("✅ PASS: Valid domain model clean.")

    # 2. Invalid Logic (Try/Except in Domain)
    logic_path = REPO_ROOT / "tests/fixtures/domain/signals/invalid_logic.py"
    logic_content = logic_path.read_text()
    logic_signals = scanner.scan_file(logic_path, logic_content)

    has_try = any(s.kind == "try_block" for s in logic_signals)
    if has_try:
        print("✅ PASS: Detected try/except in domain.")
    else:
        print(f"❌ FAIL: Did not detect try/except in domain. Got: {logic_signals}")


def verify_service_rules() -> None:
    print("\nVerifying Service Rules...")
    scanner = get_scanner()

    # 1. Valid Service Class
    valid_path = REPO_ROOT / "tests/fixtures/service/clean/valid_service.py"
    valid_content = valid_path.read_text()
    valid_signals = scanner.scan_file(valid_path, valid_content)

    if valid_signals:
        print(f"❌ FAIL: Valid service class triggered signals: {valid_signals}")
    else:
        print("✅ PASS: Valid service class clean.")

    # 2. Invalid Service Model (Identity Violation)
    invalid_path = REPO_ROOT / "tests/fixtures/service/signals/invalid_model.py"
    invalid_content = invalid_path.read_text()
    invalid_signals = scanner.scan_file(invalid_path, invalid_content)

    has_identity_violation = any(s.kind == "service_identity" for s in invalid_signals)

    if has_identity_violation:
        print("✅ PASS: Detected Service Identity Violation (BaseModel inheritance).")
    else:
        print(
            f"❌ FAIL: Did not detect Service Identity Violation. Got: {invalid_signals}"
        )


if __name__ == "__main__":
    verify_domain_rules()
    verify_service_rules()
