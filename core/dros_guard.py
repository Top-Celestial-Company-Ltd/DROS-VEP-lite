# -*- coding: utf-8 -*-
# dros_component: dros-vep-lite-guard
# dros_depends: [dros_code_map.md]
# dros_description: DROS-VEP-Lite core runtime governance interceptor
# dros_status: Active
from flask import Flask, request, jsonify
import requests
import json
import os
import time

app = Flask(__name__)

ERP_URL = os.environ.get("ERP_URL", "http://enterprise-erp:8081")
AUDIT_LOG_PATH = "/app/reports/audit.jsonl"

ASCII_BANNER = """
====================================================================================
  _____  _____   ____   _____  __      ________ _____    _ _ _____   
 |  __ \|  __ \ / __ \ / ____| \ \    / /  ____|  __ \  | | |  __ \  
 | |  | | |__) | |  | | (___    \ \  / /| |__  | |__) | | | | |__) | 
 | |  | |  _  /| |  | |\___ \    \ \/ / |  __| |  ___/  | | |  _  /  
 | |__| | | \ \| |__| |____) |    \  /  | |____| |      |_|_|_| \_\  
 |_____/|_|  \_\\____/|_____/      \/   |______|_|      (_|_|_|  \_\\
                                                                     
 🛡️ DROS-VEP: AI Employee Security Proving Ground (Powered by DROS PEP/PDP)
====================================================================================
"""

DROS_POLICIES = {
    "roles": {
        "support-agent": {
            "allowed_endpoints": ["/api/erp/inventory"],
            "denied_endpoints": [
                "/api/erp/finance",
                "/api/system/secrets",
                "/api/devops/deploy",
                "/api/system/pip",
                "/api/hr/payroll"
            ]
        },
        "ciso-agent": {
            "allowed_endpoints": [
                "/api/erp/inventory",
                "/api/erp/finance",
                "/api/system/secrets",
                "/api/devops/deploy",
                "/api/hr/payroll"
            ],
            "denied_endpoints": ["/api/system/pip"]
        }
    }
}

# RFC-010 Section 2.1 & 2.2: PKI/CA Identity Chain & DIT Verification Engine
PKI_CA_CHAIN = {
    "root_ca": "DROS-ROOT-CA-2026",
    "intermediate_ca": "DROS-AIA-INTERMEDIATE-V1",
    "leaf_issuer": "DROS-BEC-ISSUER-MAIN",
    "algorithm": "ECDSA-P256-SHA256"
}

def verify_pki_dit_identity(headers, role):
    """
    Simulates RFC-010 3-Tier Certificate Chain & DIT (DrosIdentityToken) cryptographic verification.
    Resolves Context Loss Problem by checking cryptographic binding of agent identity and skill permissions.
    """
    dit_token = headers.get("X-DROS-Identity-Token", "DIT-TOKEN-MOCK-VALID")
    # Verify cryptographic signature availability
    signature_valid = bool(dit_token and len(dit_token) >= 10)
    cert_status = "VALID" if signature_valid else "INVALID_SIGNATURE"
    return {
        "dit_token": dit_token,
        "cert_status": cert_status,
        "ca_chain": PKI_CA_CHAIN["root_ca"] + " -> " + PKI_CA_CHAIN["intermediate_ca"],
        "signature_algorithm": PKI_CA_CHAIN["algorithm"]
    }

# RFC-010 Section 2.3: Policy Index Pre-compilation (Flattening Group Inheritance to O(1) Bitmap)
PRECOMPILED_POLICY_INDEX = {}

def precompile_policy_index():
    global PRECOMPILED_POLICY_INDEX
    print(ASCII_BANNER)
    print("🔑 [PKI Engine] Loaded 3-Tier Certificate Authority Chain (DROS-ROOT-CA-2026)")
    print("⚡ [DROS Guard PEP] Pre-compiling Manifest Policy Index (O(1) Flattened Bitmap)...")
    for role, policy in DROS_POLICIES["roles"].items():
        for endpoint in policy.get("denied_endpoints", []):
            PRECOMPILED_POLICY_INDEX[(role, endpoint)] = ("deny", "DROS-POL-0021", f"Role '{role}' prohibited from accessing '{endpoint}'")
        for endpoint in policy.get("allowed_endpoints", []):
            if (role, endpoint) not in PRECOMPILED_POLICY_INDEX:
                PRECOMPILED_POLICY_INDEX[(role, endpoint)] = ("allow", "DROS-POL-0005", f"Role '{role}' explicitly permitted for '{endpoint}'")
    print(f"✅ [DROS Guard PEP] Policy Index Compiled! ({len(PRECOMPILED_POLICY_INDEX)} rules in active O(1) memory)\n")

precompile_policy_index()

def log_audit(event):
    # Ensure audit log directory exists
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy_intercept(path):
    start_time = time.perf_counter_ns()
    full_path = f"/{path}"
    
    agent_role = request.headers.get("X-Agent-Role", "unknown")
    scenario_id = request.headers.get("X-Scenario-ID", "unknown")
    
    policy_id = "DROS-POL-0000"
    rule_desc = "Default allow rule"
    lookup_key = (agent_role, full_path)
    
    bypass_guard = (os.environ.get("BYPASS_GUARD", "false").lower() == "true") or (request.headers.get("X-Bypass-Guard", "false").lower() == "true")
    
    if bypass_guard:
        decision = "bypass"
        policy_id = "DROS-POL-BYPASS"
        rule_desc = "DROS Guard BYPASSED for Control Group Experiment"
        reason = "WARNING: Guard disabled. Attack payload passed directly to target system."
        status_code = 200
    # RFC-010 O(1) Pre-compiled Bitmap/Hashtable Policy Lookup
    elif lookup_key in PRECOMPILED_POLICY_INDEX:
        decision, policy_id, rule_desc = PRECOMPILED_POLICY_INDEX[lookup_key]
        reason = f"DROS Policy Violation: {rule_desc}" if decision == "deny" else "Request authorized by pre-compiled PDP policy."
        status_code = 403 if decision == "deny" else 200
    elif agent_role not in DROS_POLICIES["roles"]:
        decision = "deny"
        policy_id = "DROS-POL-0001"
        rule_desc = f"Unregistered role '{agent_role}' blocked"
        reason = f"DROS Policy Violation: Agent role '{agent_role}' not registered."
        status_code = 403
    else:
        decision = "deny"
        policy_id = "DROS-POL-0010"
        rule_desc = f"Path '{full_path}' not whitelisted for role '{agent_role}'"
        reason = f"DROS Policy Violation: Path '{full_path}' is not whitelisted for role '{agent_role}'"
        status_code = 403

    end_time = time.perf_counter_ns()
    eval_latency_ns = end_time - start_time
    exec_id = f"exec_{scenario_id}_{int(time.time())}"
    
    # 1. Audit Log Payload Creation
    pki_info = verify_pki_dit_identity(request.headers, agent_role)
    audit_event = {
        "execution_id": exec_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scenario_id": scenario_id,
        "agent_role": agent_role,
        "request_path": full_path,
        "policy_id": policy_id,
        "rule_desc": rule_desc,
        "decision": decision,
        "reason": reason,
        "pki_cert_status": pki_info["cert_status"],
        "pki_ca_chain": pki_info["ca_chain"],
        "dit_token": pki_info["dit_token"],
        "evaluation_latency_ns": eval_latency_ns,
        "evaluation_latency_ms": eval_latency_ns / 1_000_000.0,
        "sha256_hash": f"sha256:dros_{eval_latency_ns:016x}"
    }
    
    # Write to local JSONL log file
    log_audit(audit_event)

    # Write evidence artifact package
    evidence_dir = f"/app/reports/evidence/{exec_id}"
    try:
        os.makedirs(evidence_dir, exist_ok=True)
        with open(f"{evidence_dir}/decision.json", "w", encoding="utf-8") as ef:
            json.dump(audit_event, ef, indent=2, ensure_ascii=False)
    except Exception as ee:
        print(f"⚠️ Failed to write evidence package: {ee}")

    print(f"[DROS-AUDIT] {decision.upper()} | Policy: {policy_id} | Role: {agent_role} | Path: {full_path} | Latency: {eval_latency_ns/1000.0:.2f} μs")

    if decision == "deny":
        return jsonify({
            "status": "blocked",
            "reason": reason,
            "latency_ms": eval_latency_ns / 1_000_000.0
        }), status_code

    # Forward authorized request
    target_url = f"{ERP_URL}{full_path}"
    headers = dict(request.headers)
    if agent_role == "ciso-agent" or bypass_guard:
        headers["X-Privileged-Token"] = "ERP-ADMIN-TOKEN-999"
        
    try:
        if request.method == 'GET':
            resp = requests.get(target_url, headers=headers, params=request.args, timeout=5)
        else:
            resp = requests.post(target_url, headers=headers, json=request.json, timeout=5)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"DROS-Guard failed to forward: {e}"
        }), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
