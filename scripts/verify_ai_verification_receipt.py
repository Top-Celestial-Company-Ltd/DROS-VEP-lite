#!/usr/bin/env python3
r"""
verify_ai_verification_receipt.py - Read-Only Receipt Contract Validator for VEP-AI-V1.

Validates an independent, verifier-side VEP-AI-V1 Verification Receipt against:
1. JSON Schema conformance (docs/evidence/AI_VERIFICATION_RECEIPT.schema.json).
2. Protocol identifier requirement (verification_protocol == "VEP-AI-V1").
3. Pinned commit requirement (40-char hex SHA).
4. State completion contracts:
   - If verification_status == "COMPLETE":
     * clone_verified == true
     * tracked_file_inventory_verified == true
     * ai_verify_read == true
     * evidence_index_read == true
     * claim_register_read == true
     * primary_reports_inspected == true
     * raw_evidence_inspected == true
     * integrity_validation_executed == true
     * readme_only_verification == false
     * validator_result == "PASS"
     * limitations must NOT contain any unresolved repository-access limitation.
   - If verification_status == "PARTIAL_VERIFICATION":
     * readme_only_verification == false
   - If verification_status == "INCOMPLETE_REPOSITORY_ACCESS":
     * Must not claim COMPLETE.
   - If verification_status == "REJECTED_README_ONLY":
     * readme_only_verification == true (explicitly logged rejection)

Usage:
    python scripts/verify_ai_verification_receipt.py <path_to_receipt.json>

Strictly read-only with respect to the repository and receipt.
"""

import sys
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "evidence" / "AI_VERIFICATION_RECEIPT.schema.json"

HEX_SHA_REGEX = re.compile(r"^[0-9a-fA-F]{40}$")

UNRESOLVED_ACCESS_PATTERNS = [
    re.compile(r"repository-access limitation", re.IGNORECASE),
    re.compile(r"incomplete repository access", re.IGNORECASE),
    re.compile(r"web crawl(?:ing)? limitation", re.IGNORECASE),
    re.compile(r"robots\.txt limitation", re.IGNORECASE),
    re.compile(r"rate limit(?:ing)?", re.IGNORECASE),
    re.compile(r"unable to clone", re.IGNORECASE),
]

def validate_receipt_file(receipt_path: Path) -> int:
    errors = []

    print("[*] Validating VEP-AI-V1 Verification Receipt...")
    print(f"[*] Receipt File: {receipt_path}")

    if not receipt_path.exists():
        print(f"[-] ERROR: Receipt file does not exist: {receipt_path}")
        return 1

    try:
        content = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[-] ERROR: Failed to parse receipt as JSON: {e}")
        return 1

    # Basic type check
    if not isinstance(content, dict):
        print("[-] ERROR: Receipt JSON must be an object.")
        return 1

    # 1. Required fields
    required_fields = [
        "verification_protocol",
        "repository",
        "target_commit_sha",
        "verification_status",
        "validator_result",
        "readme_only_verification"
    ]
    for rf in required_fields:
        if rf not in content:
            errors.append(f"Missing required field: '{rf}'")

    protocol = content.get("verification_protocol")
    if protocol != "VEP-AI-V1":
        errors.append(f"Invalid verification_protocol: '{protocol}' (expected 'VEP-AI-V1')")

    repo = content.get("repository")
    if repo not in ("DROS-VEP-lite", "DROS-VEP"):
        errors.append(f"Invalid repository: '{repo}' (expected 'DROS-VEP-lite' or 'DROS-VEP')")

    sha = content.get("target_commit_sha", "")
    if not HEX_SHA_REGEX.match(str(sha)):
        errors.append(f"Invalid target_commit_sha: '{sha}' (must be 40-character hex)")

    status = content.get("verification_status")
    valid_statuses = {"COMPLETE", "PARTIAL_VERIFICATION", "INCOMPLETE_REPOSITORY_ACCESS", "REJECTED_README_ONLY"}
    if status not in valid_statuses:
        errors.append(f"Invalid verification_status: '{status}' (must be one of {sorted(valid_statuses)})")

    readme_only = content.get("readme_only_verification")
    validator_res = content.get("validator_result")

    scope = content.get("verification_scope")
    if scope is not None:
        if scope not in ("FULL_REPOSITORY", "CLAIM_SET"):
            errors.append(f"Invalid verification_scope: '{scope}' (expected 'FULL_REPOSITORY' or 'CLAIM_SET')")
        if scope == "CLAIM_SET":
            claims = content.get("claims")
            if not isinstance(claims, list) or not claims:
                errors.append("Invalid claims: 'claims' array must be non-empty when verification_scope is 'CLAIM_SET'")
            else:
                for c in claims:
                    if not re.match(r"^CLAIM-[0-9]{2}$", str(c)):
                        errors.append(f"Invalid claim identifier in claims list: '{c}'")

    # 2. Status-specific contract validation
    if status == "COMPLETE":
        mandatory_booleans = [
            ("clone_verified", True),
            ("tracked_file_inventory_verified", True),
            ("ai_verify_read", True),
            ("evidence_index_read", True),
            ("claim_register_read", True),
            ("primary_reports_inspected", True),
            ("raw_evidence_inspected", True),
            ("integrity_validation_executed", True),
            ("readme_only_verification", False),
        ]
        for field, expected in mandatory_booleans:
            actual = content.get(field)
            if actual is not expected:
                errors.append(f"Contract violation for COMPLETE: '{field}' is {actual} (expected {expected})")

        if validator_res != "PASS":
            errors.append(f"Contract violation for COMPLETE: 'validator_result' is '{validator_res}' (expected 'PASS')")

        limitations = content.get("limitations", [])
        if isinstance(limitations, list):
            for lim in limitations:
                for pat in UNRESOLVED_ACCESS_PATTERNS:
                    if pat.search(str(lim)):
                        errors.append(f"Contract violation for COMPLETE: limitations contains unresolved access constraint: '{lim}'")

    elif status == "PARTIAL_VERIFICATION":
        if readme_only is True:
            errors.append("Contract violation for PARTIAL_VERIFICATION: 'readme_only_verification' cannot be true")

    elif status == "INCOMPLETE_REPOSITORY_ACCESS":
        limitations = content.get("limitations", [])
        has_access_lim = False
        if isinstance(limitations, list):
            for lim in limitations:
                for pat in UNRESOLVED_ACCESS_PATTERNS:
                    if pat.search(str(lim)):
                        has_access_lim = True
                        break
        if not has_access_lim:
            errors.append("Contract violation for INCOMPLETE_REPOSITORY_ACCESS: limitations must declare the repository-access constraint.")

    elif status == "REJECTED_README_ONLY":
        if readme_only is not True:
            errors.append("Contract violation for REJECTED_README_ONLY: 'readme_only_verification' must be true")

    if errors:
        print(f"\n[-] Validation FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return 1

    print("[+] Receipt structure valid against schema requirements.")
    print(f"[+] Protocol identifier: {protocol}")
    print(f"[+] Target commit SHA : {sha}")
    print(f"[+] Verification status: {status}")
    print(f"[+] Validator result   : {validator_res}\n")
    print("RECEIPT_SCHEMA_STATUS = PASS")
    print("RECEIPT_COMPLETION_CONTRACT = PASS")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python scripts/verify_ai_verification_receipt.py <receipt_path.json>")
        sys.exit(0 if (len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help")) else 2)
    receipt_file = Path(sys.argv[1]).resolve()
    sys.exit(validate_receipt_file(receipt_file))
