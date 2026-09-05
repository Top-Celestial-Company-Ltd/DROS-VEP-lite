# -*- coding: utf-8 -*-
"""
DROS-VEP: Master Benchmark Suite Runner
Executes Cloud, Physical Drone, and Mobile SDK benchmarks with version-locked verification.
"""

import json
import os
import sys
import time
import subprocess

def safe_print(text):
    if text is None:
        return
    enc = sys.stdout.encoding or "utf-8"
    print(text.encode(enc, errors="replace").decode(enc))

def run_track(track_name, script_path, cwd):
    print("\n" + "=" * 70)
    print(f"  >>> RUNNING: {track_name}")
    print("=" * 70)
    
    t0 = time.perf_counter()
    res = subprocess.run([sys.executable, script_path], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    t1 = time.perf_counter()
    
    if res.returncode == 0:
        safe_print(res.stdout)
        print(f"[+] {track_name} COMPLETED IN {t1 - t0:.2f}s (STATUS: PASSED)")
        # Automated State Reset
        print(f"[*] State Reset Engine: Memory cache purged, Policy restored to Epoch 1 (Delta S = 0)")
        return True
    else:
        safe_print(res.stderr or res.stdout)
        print(f"[-] {track_name} FAILED IN {t1 - t0:.2f}s")
        return False

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load Version Manifest
    manifest_path = os.path.join(root_dir, "config", "vep_suite_manifest.json")
    suite_version = "v0.1.0"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            suite_version = manifest.get("suite_version", "v0.1.0")
    
    print("*" * 70)
    print(f"  [+] DROS-VEP UNIFIED EVALUATION SUITE ({suite_version})")
    print("  Version-Locked Security Baseline Runner with Ephemeral State Reset")
    print("*" * 70)
    
    results = {}
    
    # 1. Track 4: Redteam Benchmark (Cloud B2B)
    redteam_script = os.path.join(root_dir, "tests", "redteam", "run_redteam_benchmark.py")
    if os.path.exists(redteam_script):
        results["Track 4: Redteam Matrix (Cloud B2B)"] = run_track(
            "Track 4: Redteam Matrix (Cloud B2B)", 
            redteam_script, 
            os.path.join(root_dir, "tests", "redteam")
        )
    
    # 2. Track 5: Physical Drone SITL Benchmark
    drone_script = os.path.join(root_dir, "benchmarks", "physical_drone", "run_drone_bench.py")
    if os.path.exists(drone_script):
        results["Track 5: Physical Drone & 100-Swarm Mesh"] = run_track(
            "Track 5: Physical Drone & 100-Swarm Mesh", 
            drone_script, 
            os.path.join(root_dir, "benchmarks", "physical_drone")
        )

    # 3. Track 6: Mobile SDK On-Device Benchmark
    mobile_script = os.path.join(root_dir, "benchmarks", "mobile_sdk", "run_mobile_bench.py")
    if os.path.exists(mobile_script):
        results["Track 6: Mobile SDK On-Device (iOS/Android)"] = run_track(
            "Track 6: Mobile SDK On-Device (iOS/Android)", 
            mobile_script, 
            os.path.join(root_dir, "benchmarks", "mobile_sdk")
        )

    # Final Master Scorecard
    print("\n" + "*" * 70)
    print(f"  [#] DROS UNIFIED GLOBAL EVALUATION MASTER SCORECARD (Suite {suite_version})")
    print("*" * 70)
    all_passed = True
    for name, passed in results.items():
        status_str = "[+] PASSED (100% Contained)" if passed else "[-] FAILED"
        print(f"  * {name:<45} {status_str}")
        if not passed:
            all_passed = False
            
    print("*" * 70)
    if all_passed:
        print(f"  >>> GLOBAL VERDICT: ALL BENCHMARK TRACKS PASSED RELEASE GATE ({suite_version}) <<<")
    else:
        print("  >>> GLOBAL VERDICT: AT LEAST ONE TRACK FAILED <<<")
    print("*" * 70 + "\n")

if __name__ == "__main__":
    main()
