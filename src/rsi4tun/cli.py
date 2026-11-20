import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path

from rsi4tun.contracts import read_json, save_once


def main() -> int:
    parser = argparse.ArgumentParser(prog="rsi4tun")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo")
    demo.add_argument("--output", required=True, type=Path)
    fixture = commands.add_parser("fixture-run")
    fixture.add_argument("--case", required=True, type=Path)
    fixture.add_argument("--config", required=True, type=Path)
    fixture.add_argument("--output", required=True, type=Path)
    compare = commands.add_parser("compare")
    compare.add_argument("--reference", required=True, type=Path)
    compare.add_argument("--observed", required=True, type=Path)
    compare.add_argument("--policy", required=True, type=Path)
    compare.add_argument("--output", required=True, type=Path)
    audit = commands.add_parser("audit-code")
    audit.add_argument("--root", type=Path, default=Path.cwd())
    commands.add_parser("run-real")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            from rsi4tun.demo import run_demo
            result = run_demo(args.output)
        elif args.command == "fixture-run":
            from rsi4tun.adapters import run_synthetic
            commit, tree = os.environ.get("RSI_CODE_COMMIT"), os.environ.get("RSI_CODE_TREE")
            if not commit or not tree:
                raise ValueError("versioned_executor_required")
            result = asdict(run_synthetic(read_json(args.case), read_json(args.config), args.output, commit, tree))
        elif args.command == "compare":
            from rsi4tun.evidence import bundle_from_dict, compare_reference, policy_from_dict
            result = asdict(compare_reference(bundle_from_dict(read_json(args.reference)),
                                              bundle_from_dict(read_json(args.observed)), policy_from_dict(read_json(args.policy))))
            save_once(args.output, result)
        elif args.command == "audit-code":
            from rsi4tun.quality import audit_code
            result = audit_code(args.root)
            print(json.dumps(result, sort_keys=True))
            return 0 if result["passed"] else 1
        else:
            raise NotImplementedError("real_sam4tun_integration_not_configured")
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, KeyError, NotImplementedError, FileExistsError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}))
        return 2
