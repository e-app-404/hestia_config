#!/usr/bin/env python3
import os, re, sys, json, fnmatch, argparse, pathlib, yaml

def load_rules(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("path_remap_rules", [])

def compile_rule(rule, env):
    pattern = re.compile(rule["find_regex"])
    replacement = rule["replace"]
    # Expand env vars in replacement
    replacement = os.path.expandvars(replacement)
    # Also apply defaults if not set
    for k, v in rule.get("env_defaults", {}).items():
        replacement = replacement.replace("${%s}" % k, os.environ.get(k, v))
    return pattern, replacement

def iter_files(root, globs):
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if any(fnmatch.fnmatch(rel, g) for g in globs):
                yield rel

def apply_rules(root, rules, dry_run=True):
    report = []
    for rule in rules:
        globs = rule.get("file_globs", ["**/*"])
        pat, repl = compile_rule(rule, os.environ)
        changed = []
        for rel in iter_files(root, globs):
            fp = os.path.join(root, rel)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                new = pat.sub(repl, text)
                if new != text:
                    changed.append(rel)
                    if not dry_run:
                        with open(fp, "w", encoding="utf-8") as f:
                            f.write(new)
            except Exception as e:
                # skip binaries or unreadable files
                continue
        report.append({
            "rule_id": rule["id"],
            "description": rule.get("description",""),
            "matches": len(changed),
            "files": changed[:100]  # preview cap
        })
    return report

def main():
    ap = argparse.ArgumentParser(description="Apply path remap rules across a repository")
    ap.add_argument("repo_root", help="Path to the repository root to rewrite")
    ap.add_argument("--rules", default="path_remap_rules.yaml", help="Rules YAML file")
    ap.add_argument("--write", action="store_true", help="Write changes (default is dry-run)")
    args = ap.parse_args()

    rules = load_rules(args.rules)
    report = apply_rules(args.repo_root, rules, dry_run=not args.write)
    print(json.dumps({"dry_run": not args.write, "report": report}, indent=2))

if __name__ == "__main__":
    main()
