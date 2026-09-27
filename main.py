"""
main.py
-------
Command-line entry point for the Policy Impact Analysis multi-agent system.

Usage:
    python main.py                          # runs the built-in sample policy
    python main.py --file my_policy.txt      # runs on your own policy text
    python main.py --text "..."              # pass policy text directly
    python main.py --out report.md           # choose the output file (default: output_report.md)
"""

import argparse
import sys
from pathlib import Path

from graph import run_pipeline

SAMPLE_POLICY = Path(__file__).parent / "sample_run" / "sample_policy.txt"


def get_policy_text(args) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return SAMPLE_POLICY.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Policy Impact Analysis multi-agent system")
    parser.add_argument("--file", help="Path to a .txt file containing the policy proposal")
    parser.add_argument("--text", help="Policy proposal text, passed directly")
    parser.add_argument(
        "--out", default="output_report.md", help="Where to save the final report"
    )
    args = parser.parse_args()

    policy_text = get_policy_text(args)

    result = run_pipeline(policy_text)

    if result.get("error"):
        print(f"Pipeline stopped: {result['error']}", file=sys.stderr)
        sys.exit(1)

    report = result["final_report"]
    Path(args.out).write_text(report, encoding="utf-8")

    print("\n" + "=" * 70)
    print(report)
    print("=" * 70)
    print(f"\nFull report saved to: {args.out}")


if __name__ == "__main__":
    main()
