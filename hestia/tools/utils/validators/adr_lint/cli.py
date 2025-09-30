import argparse
import sys

from . import report, rules


def parse_args():
    p = argparse.ArgumentParser(prog="adr-lint", description="Simple ADR linter prototype")
    p.add_argument("paths", nargs="+", help="Files or directories to check")
    p.add_argument("--json", action="store_true", help="Emit JSON report")
    return p.parse_args()


def collect_files(paths):
    import os

    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, fnames in os.walk(p):
                for f in fnames:
                    if f.lower().endswith('.md'):
                        files.append(os.path.join(root, f))
        else:
            files.append(p)
    return files


def main():
    args = parse_args()
    files = collect_files(args.paths)
    results = []
    for f in files:
        res = rules.check_file(f)
        results.append(res)

    if args.json:
        print(report.to_json(results))
    else:
        print(report.format(results))

    exit_code = 1 if any(r['violations'] for r in results) else 0
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
