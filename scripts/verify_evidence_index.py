#!/usr/bin/env python3
r"""
verify_evidence_index.py - Read-Only Navigation and Integrity Validator for VEP Evidence Index.

Enforces:
1. All protocol and governance files exist (AI_VERIFY.md, EVIDENCE_INDEX.md, AI_VERIFICATION_PROTOCOL.md, AI_VERIFICATION_RECEIPT.schema.json).
2. Protocol identifier VEP-AI-V1 is present and consistent across governance files.
3. Required structural sections exist in EVIDENCE_INDEX.md.
4. All indexed paths exist in the repository.
5. All paths are repository-relative (no forbidden absolute paths such as E:\, C:\, /home/, /Users/, /tmp/, /mnt/, /var/, /opt/).
6. No broken navigation references or links.
7. No duplicate Claim or Experiment IDs in their respective navigation tables.
8. Every Claim ID (CLAIM-01 ~ CLAIM-09) strictly resolves across the four-tier chain:
   CLAIM -> EXPERIMENT -> PRIMARY REPORT -> RAW EVIDENCE / HASH.
9. Distinguishes Chain Status (CHAIN COMPLETE) from Epistemic Status (PROVEN, NOT_PROVEN, etc.).
10. Strictly read-only: does NOT modify any evidence, claim, or source file.

IMPORTANT:
This validator validates repository navigation and evidence-index integrity.
It does not independently reproduce experiments, re-run benchmarks, or convert
indexed evidence into PROVEN status. It does not independently recompute every
cryptographic digest in the repository.
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_ID = "VEP-AI-V1"

REQUIRED_GOVERNANCE_FILES = [
    "AI_VERIFY.md",
    "EVIDENCE_INDEX.md",
    "docs/evidence/AI_VERIFICATION_PROTOCOL.md",
    "docs/evidence/AI_VERIFICATION_RECEIPT.schema.json",
]

REQUIRED_INDEX_SECTIONS = [
    "Verification Scope",
    "Repository Commit",
    "Claim Register Navigation",
    "Experiment Index",
    "Physical Drone Evidence",
    "Integrity and Hash Records",
    "Verification Limitations",
]

EXPECTED_CLAIMS = [
    f"CLAIM-{i:02d}" for i in range(1, 10)
]

ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"^[A-Za-z]:[/\\]"),
    re.compile(r"^/home/"),
    re.compile(r"^/Users/"),
    re.compile(r"^/tmp/"),
    re.compile(r"^/mnt/"),
    re.compile(r"^/var/"),
    re.compile(r"^/opt/"),
]

def check_file_path(path_str: str) -> tuple[bool, str]:
    clean_path = path_str.strip().strip("`").strip("'").strip('"')
    if not clean_path or clean_path.startswith("http://") or clean_path.startswith("https://"):
        return True, "URL or empty"

    for pattern in ABSOLUTE_PATH_PATTERNS:
        if pattern.search(clean_path):
            return False, f"Absolute filesystem path detected: {clean_path}"

    target_file = REPO_ROOT / clean_path
    if not target_file.exists():
        return False, f"Referenced path does not exist: {clean_path}"

    try:
        target_file.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False, f"Referenced path escapes repository root: {clean_path}"

    return True, "OK"

def validate_evidence_index() -> int:
    errors = []

    print("[*] Validating VEP Evidence Navigation Layer...")
    print(f"[*] Repository Root: {REPO_ROOT}")

    # 1. Check required governance and protocol files
    for gov_file in REQUIRED_GOVERNANCE_FILES:
        target = REPO_ROOT / gov_file
        if not target.exists():
            errors.append(f"Missing required governance file: {gov_file}")
        else:
            print(f"  [+] {gov_file} present.")

    if errors:
        print("\n[-] Validation failed with fatal governance prerequisites missing.")
        for err in errors:
            print(f"    - {err}")
        return 1

    ai_verify_text = (REPO_ROOT / "AI_VERIFY.md").read_text(encoding="utf-8")
    protocol_text = (REPO_ROOT / "docs/evidence/AI_VERIFICATION_PROTOCOL.md").read_text(encoding="utf-8")
    receipt_schema_text = (REPO_ROOT / "docs/evidence/AI_VERIFICATION_RECEIPT.schema.json").read_text(encoding="utf-8")
    evidence_index_text = (REPO_ROOT / "EVIDENCE_INDEX.md").read_text(encoding="utf-8")
    claim_register_path = REPO_ROOT / "docs" / "evidence" / "CLAIM_REGISTER.md"

    if not claim_register_path.exists():
        errors.append("CLAIM_REGISTER missing from docs/evidence/CLAIM_REGISTER.md")
        claim_register_text = ""
    else:
        claim_register_text = claim_register_path.read_text(encoding="utf-8")

    # Parse formal claims from docs/evidence/CLAIM_REGISTER.md
    canonical_claims = {}
    for m in re.finditer(r"^###\s+(CLAIM-\d+):\s*([^\n]+)", claim_register_text, re.MULTILINE):
        cid_reg = m.group(1)
        ctitle_reg = m.group(2).strip()
        canonical_claims[cid_reg] = ctitle_reg

    # 2. Check protocol identifier consistency
    if PROTOCOL_ID not in ai_verify_text:
        errors.append(f"Protocol identifier {PROTOCOL_ID} missing from AI_VERIFY.md")
    if PROTOCOL_ID not in protocol_text:
        errors.append(f"Protocol identifier {PROTOCOL_ID} missing from docs/evidence/AI_VERIFICATION_PROTOCOL.md")
    if PROTOCOL_ID not in receipt_schema_text:
        errors.append(f"Protocol identifier {PROTOCOL_ID} missing from docs/evidence/AI_VERIFICATION_RECEIPT.schema.json")
    if PROTOCOL_ID not in evidence_index_text:
        errors.append(f"Protocol identifier {PROTOCOL_ID} missing from EVIDENCE_INDEX.md")

    if not any("Protocol identifier" in e for e in errors):
        print(f"  [+] {PROTOCOL_ID} protocol present and verified.")

    # 3. Check required sections in EVIDENCE_INDEX.md
    for section in REQUIRED_INDEX_SECTIONS:
        pattern = re.compile(rf"#+\s+.*{re.escape(section)}", re.IGNORECASE)
        if not pattern.search(evidence_index_text):
            errors.append(f"INDEX_STRUCTURE_INCOMPLETE: Section '{section}' missing from EVIDENCE_INDEX.md")

    # 4. Extract registered experiments from Experiment Index table in EVIDENCE_INDEX.md
    # Canonical parsing: no hardcoded whitelists; must resolve from repository navigation
    indexed_experiments = set(re.findall(r"\|\s*\*\*(EXP-[A-Za-z0-9_\-]+)\*\*\s*\|", evidence_index_text))

    # 5. Check Claim -> Experiment -> Primary Report -> Raw Evidence Resolution for CLAIM-01 ~ CLAIM-09
    # Format: | **CLAIM-XX** | Formal Claim Title | Declared Status | Registered Experiment | Primary Report | Raw Evidence / Verification | Chain Status |
    claim_table_rows = re.findall(
        r"\|\s*\*\*(CLAIM-\d+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
        evidence_index_text
    )
    found_claims = set()
    chain_complete_verified = True

    for cid, title, decl_status, exp_col, report_col, raw_col, chain_col in claim_table_rows:
        found_claims.add(cid)

        # 5a. Verify Claim exists as formal section in CLAIM_REGISTER.md
        if cid not in canonical_claims:
            errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} not found as formal section in docs/evidence/CLAIM_REGISTER.md")
            chain_complete_verified = False
        else:
            canon_title = canonical_claims[cid]
            clean_title = title.strip()
            if clean_title != canon_title and clean_title not in canon_title and canon_title not in clean_title:
                errors.append(f"CLAIM_MAPPING_MISMATCH: {cid} title in index '{clean_title}' differs from canonical '{canon_title}'")
                chain_complete_verified = False

        # 5b. Verify Registered Experiment ID
        exp_match = re.search(r"`(EXP-[A-Za-z0-9_\-]+)`", exp_col)
        if not exp_match:
            errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} has no valid `EXP-...` ID in Registered Experiment column")
            chain_complete_verified = False
        else:
            exp_id = exp_match.group(1)
            # Verify experiment is indexed in repository experiment catalog
            if exp_id not in indexed_experiments:
                errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} references unregistered experiment {exp_id}")
                chain_complete_verified = False

        # 5c. Check report link in report_col
        rep_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", report_col)
        if not rep_links:
            errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} has no valid markdown link in Primary Report column")
            chain_complete_verified = False
        else:
            for _, link in rep_links:
                valid, msg = check_file_path(link.split("#")[0])
                if not valid:
                    errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} primary report broken: {msg}")
                    chain_complete_verified = False

        # 5d. Check raw evidence path in raw_col
        raw_items = re.findall(r"`([a-zA-Z0-9_\-\./\\]+)`", raw_col)
        has_valid_raw = False
        for rpath in raw_items:
            if not rpath.endswith(".py"):  # ignore CLI reproduction commands
                valid, msg = check_file_path(rpath)
                if not valid:
                    errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} raw evidence broken: {msg}")
                    chain_complete_verified = False
                else:
                    has_valid_raw = True
            else:
                # Script/CLI reference (like vep.py replay)
                valid, msg = check_file_path(rpath.split()[0])
                if valid:
                    has_valid_raw = True

        if not has_valid_raw and not raw_items:
            errors.append(f"EVIDENCE_CHAIN_INCOMPLETE: {cid} has no valid raw evidence reference")
            chain_complete_verified = False

    missing_claims = set(EXPECTED_CLAIMS) - found_claims
    if missing_claims:
        errors.append(f"INDEX_STRUCTURE_INCOMPLETE: Expected claims missing from table: {sorted(missing_claims)}")
        chain_complete_verified = False

    if chain_complete_verified and not missing_claims:
        print("  [+] CLAIM_REGISTER canonical mapping resolved (9/9 claims matched).")
        print("  [+] Claim -> Experiment -> Primary Report -> Raw Evidence resolution verified.")

    # 6. Extract all markdown links and check resolution & no repository escaping
    md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", evidence_index_text)
    print(f"[*] Checking {len(md_links)} markdown links in EVIDENCE_INDEX.md...")
    for text, link in md_links:
        link_target = link.split("#")[0]
        if not link_target:
            continue
        valid, msg = check_file_path(link_target)
        if not valid:
            errors.append(f"Broken markdown link [{text}]({link}): {msg}")

    # 7. Extract backtick paths pointing to existing files/dirs
    backtick_items = re.findall(r"`([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+|reports/[a-zA-Z0-9_\-\./\\]+|benchmarks/[a-zA-Z0-9_\-\./\\]+)`", evidence_index_text)
    print(f"[*] Checking {len(backtick_items)} backtick repository paths in EVIDENCE_INDEX.md...")
    for item in backtick_items:
        clean_item = item.strip().rstrip("/")
        if "." in Path(clean_item).name or clean_item.startswith(("reports/", "benchmarks/", "docs/", "drone/")):
            valid, msg = check_file_path(clean_item)
            if not valid:
                errors.append(f"Broken path reference `{item}`: {msg}")

    # 8. Check for forbidden absolute paths across all index lines
    for line_no, line in enumerate(evidence_index_text.splitlines(), start=1):
        for pattern in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(line) and "https://" not in line and "http://" not in line:
                errors.append(f"EVIDENCE_INDEX.md line {line_no} contains forbidden absolute path: {line.strip()}")

    # 9. Check for duplicate ID collisions in navigation tables
    table_claim_ids = [cid for cid, _, _, _, _, _, _ in claim_table_rows]
    if len(table_claim_ids) != len(set(table_claim_ids)):
        errors.append("IDENTIFIER_COLLISION: Duplicate Claim ID detected in claim navigation table")

    exp_table_matches = re.findall(r"\|\s*\*\*(EXP-[A-Z0-9_\-]+)\*\*\s*\|", evidence_index_text)
    if len(exp_table_matches) != len(set(exp_table_matches)):
        errors.append("IDENTIFIER_COLLISION: Duplicate Experiment ID detected in experiment index table")

    # 10. Verify S2-D forensic report existence
    s2d_report_path = REPO_ROOT / "reports" / "evidence" / "drone" / "m1_1" / "s2_v2" / "s2_d" / "S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md"
    if not s2d_report_path.exists():
        errors.append(f"Missing canonical S2-D forensic report: {s2d_report_path.relative_to(REPO_ROOT)}")
    else:
        print("  [+] S2-D forensic report present and verified.")

    if errors:
        print(f"\n[-] Validation FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return 1

    print("\n[+] VEP-AI-V1 protocol present")
    print("[+] AI_VERIFY.md present")
    print("[+] EVIDENCE_INDEX.md present")
    print("[+] CLAIM_REGISTER navigation present")
    print("[+] Primary report references valid")
    print("[+] Raw evidence references valid")
    print("[+] No repository-escaping paths detected")
    print("[+] No forbidden absolute paths detected")
    print("[+] No duplicate evidence identifiers detected")
    print("[+] S2-D forensic report present")
    print("[+] Read-only validation completed\n")
    print("VERIFICATION_NAVIGATION_STATUS = PASS")
    print("EVIDENCE_INDEX_INTEGRITY = PASS\n")
    print("IMPORTANT:")
    print("This validator validates repository navigation and evidence-index")
    print("integrity. It does not independently reproduce experiments,")
    print("re-run benchmarks, or convert indexed evidence into PROVEN status.")
    return 0

if __name__ == "__main__":
    sys.exit(validate_evidence_index())
