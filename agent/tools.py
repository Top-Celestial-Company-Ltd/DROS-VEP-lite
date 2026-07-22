# -*- coding: utf-8 -*-
import os
import requests

DROS_GUARD_URL = os.environ.get("DROS_GUARD_URL", "http://dros-guard:8082")
AGENT_ROLE = os.environ.get("AGENT_ROLE", "support-agent")

def get_headers(scenario_id="unknown"):
    return {
        "X-Agent-Role": AGENT_ROLE,
        "X-Agent-Token": "DIT-TOKEN-ABC-123",
        "X-Scenario-ID": scenario_id
    }

def get_inventory(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/erp/inventory"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_finance_records(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/erp/finance"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_env_secrets(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/system/secrets"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def deploy_production(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/devops/deploy"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def pip_install_package(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/system/pip"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_hr_database(scenario_id="unknown"):
    url = f"{DROS_GUARD_URL}/api/hr/payroll"
    try:
        resp = requests.get(url, headers=get_headers(scenario_id), timeout=5)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
