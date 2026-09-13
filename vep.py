#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VEP Unified CLI: Multi-Substrate Post-Compromise Benchmark Framework.
Usage:
  python vep.py substrate list
  python vep.py benchmark post-compromise [--scenario PC-001] [--substrate dros,wasi,tla]
  python vep.py compare [--experiment EXP_ID]
  python vep.py replay [--experiment EXP_ID] [--request REQ_ID]
"""

import os
import sys
import argparse
import json

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup Python path to include src and substrates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
SUBSTRATES_DIR = os.path.join(BASE_DIR, "substrates")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if SUBSTRATES_DIR not in sys.path:
    sys.path.insert(0, SUBSTRATES_DIR)

from vep.schema import SubstrateAvailability
from vep.scenario import load_all_scenarios, load_scenario
from vep.benchmark.runner import VepBenchmarkRunner
from vep.benchmark.replay import VepReplayEngine

from dros.adapter import DrosAdapter
from wasi.adapter import WasiAdapter
from tla.adapter import TlaAssuranceAdapter
from sel4.adapter import Sel4Adapter
from cheri.adapter import CheriAdapter


def get_available_adapters():
    return {
        "dros": DrosAdapter(deployment_mode="runtime"),
        "dros-kernel": DrosAdapter(deployment_mode="kernel"),
        "wasi": WasiAdapter(),
        "tla": TlaAssuranceAdapter(),
        "sel4": Sel4Adapter(),
        "cheri": CheriAdapter(),
    }


def cmd_substrate_list(args):
    adapters = get_available_adapters()
    print("=" * 75)
    print("🔬 VEP Registered Security & Assurance Substrates")
    print("=" * 75)
    print(f"{'Substrate':<14} | {'Type':<10} | {'Enforcement':<20} | {'Availability':<12}")
    print("-" * 75)
    for name, adapter in adapters.items():
        avail = adapter.check_availability().value
        layer = adapter.enforcement_layer.value
        sub_type = adapter.substrate_type.value
        print(f"{name:<14} | {sub_type:<10} | {layer:<20} | {avail:<12}")
    print("=" * 75 + "\n")


def cmd_benchmark_post_comp(args):
    all_adapters = get_available_adapters()
    chosen_sub_names = [s.strip() for s in args.substrate.split(",") if s.strip()]
    active_adapters = []
    for s in chosen_sub_names:
        if s in all_adapters:
            active_adapters.append(all_adapters[s])
        else:
            print(f"[!] Unknown substrate: '{s}'. Ignoring.")

    if not active_adapters:
        print("[-] No valid substrates specified.")
        sys.exit(1)

    scenarios_dir = os.path.join(BASE_DIR, "scenarios", "post_compromise")
    if args.scenario:
        # Load single scenario
        target_path = os.path.join(scenarios_dir, f"{args.scenario}.yaml")
        if not os.path.exists(target_path):
            target_path = os.path.join(scenarios_dir, f"{args.scenario}")
        if not os.path.exists(target_path):
            print(f"[-] Scenario file not found: {target_path}")
            sys.exit(1)
        scenarios = [load_scenario(target_path)]
    else:
        scenarios = load_all_scenarios(scenarios_dir)

    print("\n" + "=" * 80)
    print(f"🚀 Running VEP Post-Compromise Benchmark: {len(scenarios)} Scenarios x {len(active_adapters)} Substrates")
    print("=" * 80)

    runner = VepBenchmarkRunner(output_base_dir=os.path.join(BASE_DIR, "reports", "benchmarks", "post_compromise"))
    summary = runner.run_suite(scenarios, active_adapters)

    print(f"\n[+] Experiment ID: {summary['experiment_id']}")
    print(f"[+] Total Executions Evaluated: {summary['total_executions']} (50 scenario evaluations + 5 replay-phase evaluations = 55 execution records)")
    print("-" * 80)
    print(f"{'Substrate':<14} | {'Total':<6} | {'UER (%)':<8} | {'Unsupported (%)':<15} | {'P50 (ns)':<10}")
    print("-" * 80)
    for sub, m in summary["metrics"].items():
        uer = f"{m['unauthorized_execution_rate_pct']:.1f}%"
        unsupp = f"{m['unsupported_rate_pct']:.1f}%"
        print(f"{sub:<14} | {m['total_attempts']:<6} | {uer:<8} | {unsupp:<15} | {m['latency_p50_ns']:<10}")
    print("=" * 80 + "\n")


def cmd_compare(args):
    reports_dir = os.path.join(BASE_DIR, "reports", "benchmarks", "post_compromise")
    exp_id = args.experiment
    if not exp_id:
        latest_ptr = os.path.join(reports_dir, "latest.json")
        if os.path.exists(latest_ptr):
            with open(latest_ptr, "r", encoding="utf-8") as f:
                exp_id = json.load(f).get("latest_experiment_id")

    if not exp_id:
        print("[-] No experiment ID provided and no latest experiment found.")
        sys.exit(1)

    res_file = os.path.join(reports_dir, exp_id, "result.json")
    if not os.path.exists(res_file):
        print(f"[-] Result file not found: {res_file}")
        sys.exit(1)

    with open(res_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "=" * 90)
    print(f"📊 VEP Cross-Substrate Comparison Report: {exp_id}")
    print(f"Host OS: {data['environment']['os']} | Commit: {data['environment']['vep_commit'][:8]}")
    print("=" * 90)
    print(f"{'Substrate':<12} | {'Unauth Att':<10} | {'UER (%)':<8} | {'Unsupported':<12} | {'Replay Blk':<10} | {'P50 (ns)':<10}")
    print("-" * 90)
    for sub, m in data["metrics"].items():
        uer_str = f"{m['unauthorized_execution_rate_pct']}%"
        unsupp_str = f"{m['unsupported_rate_pct']}%"
        rep_str = f"{m.get('replay_rejection_rate_pct', 0.0)}%"
        print(f"{sub:<12} | {m['unauthorized_attempts']:<10} | {uer_str:<8} | {unsupp_str:<12} | {rep_str:<10} | {m['latency_p50_ns']:<10}")
    print("=" * 90)

    # Display Property Semantic Scope Matrix
    prop_matrix = data.get("property_matrix", {})
    if prop_matrix:
        print("\n" + "=" * 90)
        print("🔬 Post-Compromise Property Semantic Scope Matrix (M3)")
        print("=" * 90)
        subs = list(data["metrics"].keys())
        header = f"{'Security Property':<24} | " + " | ".join([f"{s[:8]:<8}" for s in subs])
        print(header)
        print("-" * 90)
        for prop, sub_map in prop_matrix.items():
            row_items = []
            for s in subs:
                outcome = sub_map.get(s, {})
                dec = outcome.get("decision", "N/A")
                scope = outcome.get("semantic_scope", "")
                if dec == "UNSUPPORTED":
                    display = "UNSUPP"
                elif dec == "DENY":
                    display = "ENFORCE"
                elif dec == "ALLOW":
                    display = "ALLOW"
                else:
                    display = dec[:7]
                row_items.append(f"{display:<8}")
            print(f"{prop[:24]:<24} | " + " | ".join(row_items))
        print("=" * 90 + "\n")


def cmd_replay(args):
    reports_dir = os.path.join(BASE_DIR, "reports", "benchmarks", "post_compromise")
    exp_id = args.experiment
    if not exp_id:
        latest_ptr = os.path.join(reports_dir, "latest.json")
        if os.path.exists(latest_ptr):
            with open(latest_ptr, "r", encoding="utf-8") as f:
                exp_id = json.load(f).get("latest_experiment_id")

    if not exp_id:
        print("[-] No experiment ID provided and no latest experiment found.")
        sys.exit(1)

    adapters = get_available_adapters()
    engine = VepReplayEngine(reports_base_dir=reports_dir)
    res = engine.replay_experiment(exp_id, adapters, target_request_id=args.request)

    print("\n" + "=" * 80)
    print(f"🔄 VEP Deterministic Replay: {exp_id}")
    print("=" * 80)
    print(f"Total Replayed Requests: {res['total_replayed']}")
    print(f"All Deterministic Matches: {'✅ PASS (100% Match)' if res['deterministic_match_all'] else '❌ MISMATCH'}")
    print("-" * 80)
    for r in res["replays"]:
        status = "MATCH" if r["deterministic_match"] else "DRIFT"
        print(f"[{status}] Req: {r['request_id']} | Substrate: {r['substrate']:<8} | Dec: {r['recorded_decision']} -> {r['replayed_decision']}")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="VEP Multi-Substrate Post-Compromise Benchmark CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # vep substrate list
    p_sub = subparsers.add_parser("substrate", help="Manage security substrates")
    p_sub_action = p_sub.add_subparsers(dest="action", required=True)
    p_sub_action.add_parser("list", help="List registered substrates and availability")

    # vep benchmark post-compromise
    p_bench = subparsers.add_parser("benchmark", help="Run benchmarks")
    p_bench_type = p_bench.add_subparsers(dest="suite", required=True)
    p_pc = p_bench_type.add_parser("post-compromise", help="Run post-compromise scenarios")
    p_pc.add_argument("--scenario", type=str, help="Specific scenario ID (e.g. PC-001)")
    p_pc.add_argument("--substrate", type=str, default="dros,wasi,tla", help="Comma-separated substrates")

    # vep compare
    p_cmp = subparsers.add_parser("compare", help="Compare benchmark results across substrates")
    p_cmp.add_argument("--experiment", type=str, help="Experiment ID to compare")

    # vep replay
    p_rep = subparsers.add_parser("replay", help="Replay experiment requests deterministically")
    p_rep.add_argument("--experiment", type=str, help="Experiment ID to replay")
    p_rep.add_argument("--request", type=str, help="Target request ID")

    args = parser.parse_args()

    if args.command == "substrate" and args.action == "list":
        cmd_substrate_list(args)
    elif args.command == "benchmark" and args.suite == "post-compromise":
        cmd_benchmark_post_comp(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "replay":
        cmd_replay(args)


if __name__ == "__main__":
    main()
