"""
Smart Student Guide - Main Entrypoint
Run interactive CLI or execute direct query modes.
Usage:
  python main.py             # Launches interactive terminal menu
  python main.py --demo      # Runs complete automated verification test suite
  python main.py --search "query"  # Direct IR search
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
from app_cli import SmartStudentApp
from sample_runs import run_all_tests


def main():
    parser = argparse.ArgumentParser(description="Smart Student Guide - Intelligent Academic Assistant")
    parser.add_argument("--demo", action="store_true", help="Run automated test suite and sample runs")
    parser.add_argument("--search", type=str, help="Run direct Information Retrieval search on academic bylaws")
    parser.add_argument("--check", type=str, help="Check eligibility for a specific course code (e.g. ML211)")
    args = parser.parse_args()

    if args.demo:
        run_all_tests()
    elif args.search:
        app = SmartStudentApp()
        print(f"\n🔎 Searching for: '{args.search}'")
        results = app.student_service.search_academic_information(args.search, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"[{i}] {r['title']} (Score: {r['score']})")
            print(f"    Source: {r['source_file']}")
            print(f"    Snippet: {r['snippet']}\n")
    elif args.check:
        app = SmartStudentApp()
        res = app.student_service.check_specific_course(args.check)
        print(f"\nCourse Check [{args.check}]:")
        print(f"Can Register: {res.get('can_register')}")
        print(f"Details: {res.get('reason')}\n")
    else:
        app = SmartStudentApp()
        app.main_menu()


if __name__ == "__main__":
    main()
