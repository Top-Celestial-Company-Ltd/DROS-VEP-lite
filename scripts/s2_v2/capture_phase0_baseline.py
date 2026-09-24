import subprocess, json, time, os

now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# 1. iptables
res_v4 = subprocess.run(["sudo", "iptables", "-S"], capture_output=True, text=True)
res_v6 = subprocess.run(["sudo", "ip6tables", "-S"], capture_output=True, text=True)

# 2. UDP sockets
res_ss = subprocess.run(["ss", "-ulpn"], capture_output=True, text=True)

# 3. Process tree
res_ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)

# 4. /tmp artifacts
tmp_files = [f for f in os.listdir("/tmp") if "dros" in f or "evidence" in f]

baseline = {
    "observation_timestamp_iso": now,
    "host_identifier": "Agent-server (Ubuntu 24.04 SITL testbed)",
    "iptables": {
        "ipv4_rules": res_v4.stdout.strip().splitlines(),
        "ipv6_rules": res_v6.stdout.strip().splitlines(),
        "has_custom_drop_reject": any("DROP" in r or "REJECT" in r for r in res_v4.stdout.splitlines()),
        "assessment": "No test-introduced firewall rules detected" if not any("multiport" in r for r in res_v4.stdout.splitlines()) else "Warning: residual multiport rules detected"
    },
    "udp_sockets_raw": res_ss.stdout.strip().splitlines(),
    "px4_process_running": any("bin/px4" in l for l in res_ps.stdout.splitlines()),
    "multi_pep_running": any("multi_pep_proxy" in l for l in res_ps.stdout.splitlines()),
    "tmp_residual_files": tmp_files
}

out_path = "/home/ai_user/dros_drone_real/reports/evidence/drone/m1_1/s2_v2/s2_v2_p0_baseline.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(baseline, f, indent=2)

print("P0_BASELINE_CAPTURED")
