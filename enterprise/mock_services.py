# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
import time

app = Flask(__name__)

FINANCIAL_RECORDS = [
    {"date": "2026-07-01", "description": "CEO Bonus Payment", "amount": 1000000.00, "status": "Confidential"},
    {"date": "2026-07-15", "description": "ST Engineering Joint Venture Deposit", "amount": 5000000.00, "status": "Confidential"},
    {"date": "2026-07-20", "description": "Intellectual Property Acquisition", "amount": 250000.00, "status": "Confidential"}
]

INVENTORY_RECORDS = [
    {"item": "DROS-PGM-x86-Dongle", "qty": 150, "location": "Warehouse-A"},
    {"item": "Jetson-Orin-Nano-Module", "qty": 45, "location": "Warehouse-B"},
    {"item": "VajraClaw-Gateway-Rack", "qty": 12, "location": "Warehouse-A"}
]

# RFC-010 Section 5.2: Enterprise Network Jitter & Transactional State Simulation
ENABLE_JITTER = True

@app.route('/api/erp/inventory', methods=['GET'])
def get_inventory():
    if ENABLE_JITTER:
        time.sleep(0.002) # 2ms micro-jitter simulation
    return jsonify({
        "status": "success",
        "system_target": "SAP-RFC-Mock",
        "data": INVENTORY_RECORDS
    })

@app.route('/api/erp/finance', methods=['GET'])
def get_finance():
    if ENABLE_JITTER:
        time.sleep(0.003) # 3ms network jitter simulation
    auth_header = request.headers.get("X-Privileged-Token")
    if auth_header != "ERP-ADMIN-TOKEN-999":
        return jsonify({
            "status": "error",
            "message": "Unauthorized SAP RFC/SNC Session. Requires X-Privileged-Token"
        }), 403
        
    return jsonify({
        "status": "success",
        "system_target": "SAP-SNC-Binary-Mock",
        "data": FINANCIAL_RECORDS
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
