# -*- coding: utf-8 -*-
import sys
import time
import json
import os
import concurrent.futures
import urllib.request
import urllib.error

# Console encoding fix
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

GUARD_URL = os.environ.get("DROS_GUARD_URL", "http://localhost:8082/api/erp/finance")
TOTAL_REQUESTS = 5000
CONCURRENCY = 50

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
STRESS_REPORT = os.path.join(REPORTS_DIR, "stress_summary.json")

def send_request(req_id):
    headers = {
        "X-Agent-Role": "support-agent",
        "X-Scenario-ID": "ATS-001-STRESS",
        "Content-Type": "application/json"
    }
    start = time.perf_counter_ns()
    try:
        req = urllib.request.Request(GUARD_URL, headers=headers)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        status = 500

    end = time.perf_counter_ns()
    latency_us = (end - start) / 1000.0
    return status, latency_us

def run_stress_test():
    print("==================================================================")
    print(f"⚡ DROS-VEP High-Concurrency Stress Benchmark ({TOTAL_REQUESTS} Tool Calls)")
    print(f"⚡ Simulating 72-Hour Load in Accelerated Burst Mode (Workers: {CONCURRENCY})")
    print("==================================================================")

    start_total = time.time()
    latencies = []
    status_counts = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        for f in concurrent.futures.as_completed(futures):
            st, lat = f.result()
            latencies.append(lat)
            status_counts[st] = status_counts.get(st, 0) + 1

    total_time = time.time() - start_total
    qps = TOTAL_REQUESTS / total_time
    avg_lat_us = sum(latencies) / len(latencies)
    min_lat_us = min(latencies)
    max_lat_us = max(latencies)
    
    # Sorting for percentiles
    latencies.sort()
    p95_lat_us = latencies[int(len(latencies) * 0.95)]
    p99_lat_us = latencies[int(len(latencies) * 0.99)]

    summary = {
        "total_requests": TOTAL_REQUESTS,
        "concurrency": CONCURRENCY,
        "total_duration_sec": round(total_time, 3),
        "qps_throughput": round(qps, 2),
        "status_distribution": status_counts,
        "blocked_403_rate": f"{(status_counts.get(403, 0) / TOTAL_REQUESTS) * 100:.2f}%",
        "latency_metrics_us": {
            "avg_latency_us": round(avg_lat_us, 2),
            "min_latency_us": round(min_lat_us, 2),
            "max_latency_us": round(max_lat_us, 2),
            "p95_latency_us": round(p95_lat_us, 2),
            "p99_latency_us": round(p99_lat_us, 2)
        }
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(STRESS_REPORT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Stress Test Complete in {total_time:.2f} seconds!")
    print(f"📊 Throughput (QPS): {qps:.2f} req/sec")
    print(f"🛡️  Defense Block Rate (403 DENY): {summary['blocked_403_rate']}")
    print(f"⏱️  Average Guard Latency: {avg_lat_us:.2f} μs")
    print(f"⏱️  P95 Latency: {p95_lat_us:.2f} μs | P99 Latency: {p99_lat_us:.2f} μs")
    print("==================================================================\n")

if __name__ == "__main__":
    run_stress_test()
