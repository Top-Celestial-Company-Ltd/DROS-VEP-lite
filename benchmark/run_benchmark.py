# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import yaml
import json
import time

# Adjust console encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCENARIOS_DIR = os.path.join(BASE_DIR, "scenarios")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
AUDIT_LOG = os.path.join(REPORTS_DIR, "audit.jsonl")
SUMMARY_LOG = os.path.join(REPORTS_DIR, "benchmark_summary.json")

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR, encoding='utf-8', errors='ignore')
    return res.stdout, res.stderr, res.returncode

def load_scenario(scenario_id):
    s_path = os.path.join(SCENARIOS_DIR, scenario_id)
    if not os.path.exists(s_path):
        return None
        
    with open(os.path.join(s_path, "metadata.yaml"), "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f)
        
    with open(os.path.join(s_path, "attack_prompt.txt"), "r", encoding="utf-8") as f:
        prompt = f.read().strip()
        
    with open(os.path.join(s_path, "expected_result.yaml"), "r", encoding="utf-8") as f:
        expected = yaml.safe_load(f)
        
    return {
        "metadata": meta,
        "prompt": prompt,
        "expected": expected
    }

def main():
    print("==================================================================")
    print("🚀 DROS-VEP Lite: AI Agent Security Benchmarking Engine")
    print("==================================================================")
    
    # 1. Clean previous audit and summary reports
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if os.path.exists(AUDIT_LOG):
        os.remove(AUDIT_LOG)
        
    scenarios = [d for d in os.listdir(SCENARIOS_DIR) if os.path.isdir(os.path.join(SCENARIOS_DIR, d))]
    scenarios.sort()
    
    results = []
    
    for s_id in scenarios:
        print(f"\n[+] Loading Scenario: {s_id}...")
        s_data = load_scenario(s_id)
        if not s_data:
            print(f"Error loading {s_id}")
            continue
            
        meta = s_data["metadata"]
        prompt = s_data["prompt"]
        expected = s_data["expected"]
        
        print(f"Name: {meta['name']}")
        print(f"Target Tool: {meta['target_tool']}")
        print(f"Risk Profile: {meta['risk']}")
        
        # 2. Trigger Container execution
        # We pass role from config or default to support-agent for testing privilege enforcement
        agent_role = "support-agent"
        print(f"Executing Agent with Role: '{agent_role}'...")
        
        # docker compose run autonomous-agent
        cmd = f'docker compose run --rm -e AGENT_ROLE={agent_role} -e AGENT_PROMPT="{prompt}" -e AGENT_SCENARIO_ID={s_id} autonomous-agent'
        stdout, stderr, code = run_cmd(cmd)
        
        # 3. Read audit log line for this execution
        policy_id = "DROS-POL-0000"
        rule_desc = ""
        exec_id = ""
        sha256_hash = ""
        
        if os.path.exists(AUDIT_LOG):
            with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_log = json.loads(lines[-1].strip())
                    if last_log.get("scenario_id") == s_id:
                        decision = last_log.get("decision")
                        latency_ms = last_log.get("evaluation_latency_ms", 0.0)
                        reason = last_log.get("reason", "")
                        policy_id = last_log.get("policy_id", "DROS-POL-0021")
                        rule_desc = last_log.get("rule_desc", "")
                        exec_id = last_log.get("execution_id", "")
                        sha256_hash = last_log.get("sha256_hash", "")
                        
        # 4. Compare expected vs actual
        expected_action = "deny" if expected.get("status") == "blocked" else "allow"
        is_match = (decision == expected_action)
        
        res_entry = {
            "scenario_id": s_id,
            "name": meta["name"],
            "target_tool": meta.get("target_tool", ""),
            "risk": meta["risk"],
            "expected": expected_action,
            "actual": decision,
            "match": is_match,
            "latency_ms": latency_ms,
            "policy_id": policy_id,
            "rule_desc": rule_desc,
            "execution_id": exec_id,
            "sha256_hash": sha256_hash,
            "reason": reason
        }
        results.append(res_entry)
        
        print(f"Actual Decision: {decision.upper()} | Expected: {expected_action.upper()} | Speed: {latency_ms:.4f} ms")
        if is_match:
            print("🛡️  Defensive Integrity: VALIDATED (PASS)")
        else:
            print("❌ Defensive Integrity: COMPROMISED (FAIL)")

    # 5. Output Summary JSON
    with open(SUMMARY_LOG, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # 6. Print Benchmark Summary Table
    print("\n" + "="*80)
    print("🏆 DROS-VEP Lite Benchmark Summary")
    print("="*80)
    print(f"{'Scenario ID':<15} | {'Scenario Name':<35} | {'Decision':<10} | {'Status':<10}")
    print("-"*80)
    
    passed_cnt = 0
    for r in results:
        status_str = "PASS" if r["match"] else "FAIL"
        if r["match"]:
            passed_cnt += 1
        print(f"{r['scenario_id']:<15} | {r['name'][:35]:<35} | {r['actual'].upper():<10} | {status_str:<10}")
    
    pass_rate = (passed_cnt / len(results)) * 100.0 if results else 0
    print("-"*80)
    print(f"Total Scenarios: {len(results)} | Passed: {passed_cnt} | Pass Rate: {pass_rate:.1f}%")
    print("="*80)

if __name__ == "__main__":
    main()
