# -*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
EVIDENCE_DIR = os.path.join(REPORTS_DIR, "evidence")
AUDIT_LOG = os.path.join(REPORTS_DIR, "audit.jsonl")
GUARD_URL = os.environ.get("DROS_GUARD_URL", "http://localhost:8082")

def replay_execution(target_exec_id=None):
    print("==================================================================")
    print("🔄 DROS-VEP Deterministic Replay Engine")
    print("==================================================================")

    recorded_decision = {}

    # 1. Try loading from evidence folder
    if os.path.exists(EVIDENCE_DIR):
        exec_folders = [f for f in os.listdir(EVIDENCE_DIR) if os.path.isdir(os.path.join(EVIDENCE_DIR, f))]
        if exec_folders:
            selected_folder = exec_folders[-1]
            if target_exec_id:
                for f in exec_folders:
                    if target_exec_id in f:
                        selected_folder = f
                        break
            evidence_file = os.path.join(EVIDENCE_DIR, selected_folder, "decision.json")
            if os.path.exists(evidence_file):
                with open(evidence_file, "r", encoding="utf-8") as f:
                    recorded_decision = json.load(f)

    # 2. Fallback: Read latest log from audit.jsonl
    if not recorded_decision and os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                recorded_decision = json.loads(lines[-1])

    if not recorded_decision:
        print("❌ Error: No audit logs or evidence packages found to replay.")
        sys.exit(1)

    print(f"[+] Replaying Execution Artifact ID: {recorded_decision.get('execution_id')}")
    print(f"   Recorded Scenario ID: {recorded_decision.get('scenario_id')}")
    print(f"   Recorded Role:        {recorded_decision.get('agent_role')}")
    print(f"   Recorded Path:        {recorded_decision.get('request_path')}")
    print(f"   Recorded Decision:    {recorded_decision.get('decision', '').upper()}")
    print(f"   SHA-256 Digest:       {recorded_decision.get('sha256_hash')}")

    # Re-execute payload against Guard
    url = f"{GUARD_URL}{recorded_decision.get('request_path')}"
    headers = {
        "X-Agent-Role": recorded_decision.get('agent_role', 'support-agent'),
        "X-Scenario-ID": recorded_decision.get('scenario_id', 'ATS-001'),
        "X-Replay-Mode": "true"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            replayed_code = resp.status
    except urllib.error.HTTPError as e:
        replayed_code = e.code
    except Exception as e:
        replayed_code = 500

    replayed_decision = "deny" if replayed_code == 403 else "allow"
    is_replayed_match = (replayed_decision == recorded_decision.get('decision'))

    print("\n------------------------------------------------------------------")
    print(f"Replay Verification Status: {'✅ DETERMINISTIC REPLAY MATCH (PASS)' if is_replayed_match else '❌ REPLAY MISMATCH (FAIL)'}")
    print(f"Recorded Decision: {recorded_decision.get('decision', '').upper()} | Replayed Decision: {replayed_decision.upper()}")
    print("==================================================================\n")

if __name__ == "__main__":
    exec_id = sys.argv[1] if len(sys.argv) > 1 else None
    replay_execution(exec_id)
