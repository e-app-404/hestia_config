import os, sys

ART = ".artifacts"
os.makedirs(ART, exist_ok=True)
graph = os.path.join(ART, "graph.json")
viol  = os.path.join(ART, "violations.json")
integ = os.path.join(ART, "integrity.json")
report= os.path.join(ART, "report")

os.system(f"python lineage_guardian/graph_scanner.py --template-dir /config/domain/templates/ --output {graph} --verbose")
os.system(f"python lineage_guardian/lineage_validator.py --graph-file {graph} --output {viol}")
os.system(f"python lineage_guardian/lineage_corrector.py --violations-file {viol} --plan-dir ./.artifacts/_plan")
os.system(f"python lineage_guardian/graph_integrity_checker.py --graph-file {graph} --output {integ}")
os.system(f"python lineage_guardian/lineage_report.py --graph {graph} --violations {viol} --integrity {integ} --outdir {report}")

print('[INFO] Pipeline complete. See ./.artifacts/')
