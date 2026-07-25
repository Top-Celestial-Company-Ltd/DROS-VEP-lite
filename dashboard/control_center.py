# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request, send_from_directory
import os
import sys
import yaml
import json
import subprocess

app = Flask(__name__, static_folder='.', template_folder='.')

# Support both Docker (/app/scenarios) and standalone execution (../scenarios)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCENARIOS_DIR = os.path.join(CURRENT_DIR, "scenarios") if os.path.exists(os.path.join(CURRENT_DIR, "scenarios")) else os.path.join(BASE_DIR, "scenarios")
REPORTS_DIR = os.path.join(CURRENT_DIR, "reports") if os.path.exists(os.path.join(CURRENT_DIR, "reports")) else os.path.join(BASE_DIR, "reports")
AUDIT_LOG = os.path.join(REPORTS_DIR, "audit.jsonl")
SUMMARY_LOG = os.path.join(REPORTS_DIR, "benchmark_summary.json")

ASCII_BANNER = """
====================================================================================
  _____  _____   ____   _____  __      ________ _____    _ _ _____   
 |  __ \|  __ \ / __ \ / ____| \ \    / /  ____|  __ \  | | |  __ \  
 | |  | | |__) | |  | | (___    \ \  / /| |__  | |__) | | | | |__) | 
 | |  | |  _  /| |  | |\___ \    \ \/ / |  __| |  ___/  | | |  _  /  
 | |__| | | \ \| |__| |____) |    \  /  | |____| |      |_|_|_| \_\  
 |_____/|_|  \_\\____/|_____/      \/   |______|_|      (_|_|_|  \_\\
                                                                     
 🚀 Welcome to DROS-VEP: AI Employee Security Proving Ground Console
 👉 Control Center active on http://localhost:8080
====================================================================================
"""
print(ASCII_BANNER)

# License & Limits Configuration
COMMUNITY_CONFIG = {
    "edition": "Community Eval Edition",
    "watermark": True,
    "agent_role_limit": 2,
    "max_trial_tokens_per_month": 1,
    "trial_tokens_remaining": 1,
    "status": "Active (Local E: Sandbox)"
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/system-info')
def system_info():
    return jsonify(COMMUNITY_CONFIG)

@app.route('/api/scenarios')
def list_scenarios():
    scenarios = []
    if os.path.exists(SCENARIOS_DIR):
        for item in sorted(os.listdir(SCENARIOS_DIR)):
            meta_path = os.path.join(SCENARIOS_DIR, item, "metadata.yaml")
            if os.path.isfile(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    data["folder"] = item
                    scenarios.append(data)
    return jsonify(scenarios)

@app.route('/api/audit-logs')
def get_audit_logs():
    logs = []
    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line.strip()))
                    except Exception:
                        pass
    return jsonify(logs[-50:]) # Return last 50 entries

@app.route('/api/conformance')
def run_conformance_check():
    conf_script = os.path.join(BASE_DIR, "benchmark", "conformance_test.py")
    try:
        res = subprocess.run([sys.executable, conf_script], capture_output=True, text=True, cwd=BASE_DIR, encoding='utf-8', errors='ignore')
        conf_report_file = os.path.join(REPORTS_DIR, "conformance_report.json")
        report = {}
        if os.path.exists(conf_report_file):
            with open(conf_report_file, "r", encoding="utf-8") as f:
                report = json.load(f)
        return jsonify({"status": "success", "stdout": res.stdout, "report": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/run-benchmark', methods=['POST'])
def trigger_benchmark():
    data = request.json or {}
    selected_scenarios = data.get("scenarios", [])
    duration_mode = data.get("duration", "quick")
    agent_roles = data.get("agent_roles", ["support-agent"])
    bypass_guard = data.get("bypass_guard", False)
    
    # Enforce Agent Role Limit for Community Edition
    if len(agent_roles) > COMMUNITY_CONFIG["agent_role_limit"]:
        return jsonify({
            "status": "error",
            "message": f"Community Edition limit exceeded! Maximum allowed agent roles: {COMMUNITY_CONFIG['agent_role_limit']}. Requested: {len(agent_roles)}. Please upgrade to Enterprise Edition for unlimited Multi-Agent Swarm testing."
        }), 403

    # Trigger run_benchmark.py via subprocess
    benchmark_script = os.path.join(BASE_DIR, "benchmark", "run_benchmark.py")
    env = dict(os.environ)
    if bypass_guard:
        env["BYPASS_GUARD"] = "true"

    try:
        res = subprocess.run([sys.executable, benchmark_script], capture_output=True, text=True, cwd=BASE_DIR, env=env, encoding='utf-8', errors='ignore')
        
        summary = []
        if os.path.exists(SUMMARY_LOG):
            with open(SUMMARY_LOG, "r", encoding="utf-8") as f:
                summary = json.load(f)
                
        return jsonify({
            "status": "success",
            "stdout": res.stdout,
            "summary": summary,
            "community_info": COMMUNITY_CONFIG
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
