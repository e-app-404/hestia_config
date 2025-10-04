# workspace remediation plan

To fix the BB-8 add-on repo without guesswork, I need two kinds of input:
	1.	a few quick policy answers (what you want),
	2.	a small, read-only snapshot of the repo state (what you have).

Below is a minimal, step-by-step checklist you can run exactly as single commands (one at a time). Paste the outputs back and I’ll turn them into a surgical cleanup plan that won’t nuke anything important.

⸻

A) 6 quick policy answers

Reply in bullets, short is fine:
	1.	Retention windows you want by class
	•	backups (e.g., .bk.<UTC>): keep ? days
	•	editor temp/swap (~, .swp, .perlbak): keep ? days (often 0)
	•	bundles/archives (.tar.gz, .tgz, .zip): keep ? days
	•	logs/reports (generated): keep ? days
	2.	Canonical backup style you prefer (pick one)
	•	*.bk.<UTC> (recommended & consistent), or keep legacy suffixes?
	3.	What must remain tracked in git (besides real source):
e.g., hestia/vault/<…> snapshots, ADRs, etc.
	4.	Are there any generators (scripts/IDE add-ons) that should keep making backups? List paths if yes.
	5.	Any paths that are “runtime only” (must be ignored by git):
e.g., artifacts/, .trash/, .quarantine/, hestia/reports/, __pycache__/, etc.
	6.	Comfort level with auto-moves
	•	OK to normalize file names to *.bk.<UTC>?
	•	OK to corral junk into .trash/DATE/?
	•	OK to add/update .gitignore?

⸻

B) Tiny read-only repo snapshot (safe)

Run these from the BB-8 add-on repo root. Each is a single command. Paste each output as you go.

B0. Where am I / which branch?

git rev-parse --show-toplevel; git branch --show-current

B1. Porcelain summary (how much churn)

git status --porcelain=1 -uall | awk '{c[$1]++} END{for(k in c) printf "%-3s %d\n", k, c[k]}' | sort

B2. Snapshot of ignore rules (tail)

test -f .gitignore && tail -n 80 .gitignore || echo "(no .gitignore)"

B3. Count & size by “messy” patterns
(Reads files only; no writes.)

python3 - <<'PY'
import os,re,json
root='.'; skip=('/.git/','/node_modules/','/.venv','/deps/','/__pycache__/')
classes=[
  ('backupCanonical', r'\.bk\.\d{8}T\d{6}Z(\.__\d+)?$'),
  ('backupLegacy',    r'\.bak(\.|-|$)|\.perlbak$|_backup(\.|$)|_restore(\.|$)'),
  ('editorTemp',      r'(~$)|\.swp$|\.tmp$|\.temp$'),
  ('bundles',         r'\.(tar\.gz|tgz|zip)$'),
  ('logsReports',     r'\.(log|tsv|csv|jsonl)$'),
]
def classify(name):
  for k,rx in classes:
    if re.search(rx,name,flags=re.I): return k
  return None
from collections import Counter,defaultdict
counts=Counter(); sizes=Counter(); samples=defaultdict(list)
for d,_,fs in os.walk(root):
  p=d.replace('\\','/')
  if any(s in p for s in skip): continue
  for f in fs:
    rel=os.path.join(d,f).lstrip('./')
    k=classify(f)
    if not k: continue
    try: sz=os.path.getsize(rel)
    except: sz=0
    counts[k]+=1; sizes[k]+=sz
    if len(samples[k])<8: samples[k].append(rel)
print("COUNTS:", dict(counts))
print("SIZES:", {k: sizes[k] for k in sizes})
for k in counts:
  print(f"SAMPLE[{k}]:"); [print("  ", s) for s in samples[k]]
PY

B4. Top 30 biggest non-source artifacts
(Helps spot time sinks in diffs and slow clones.)

python3 - <<'PY'
import os,heapq
root='.'; skip=('/.git/','/node_modules/','/.venv','/deps/','/__pycache__/')
rows=[]
for d,_,fs in os.walk(root):
  p=d.replace('\\','/')
  if any(s in p for s in skip): continue
  for f in fs:
    rel=os.path.join(d,f).lstrip('./')
    try: sz=os.path.getsize(rel)
    except: continue
    # treat “likely source” as small files or known extensions
    if os.path.splitext(f)[1] in ('.py','.yaml','.yml','.json','.md','.jinja','.sh','.txt','.ts','.js','.vue','.env'):
      continue
    rows.append((sz,rel))
for sz,rel in heapq.nlargest(30, rows):
  print(f"{sz}\t{rel}")
PY

B5. Are any junk files actually tracked by git?

python3 - <<'PY'
import subprocess,os,re,sys
p=subprocess.check_output(['git','status','--porcelain=1','-z','-uall'])
tracked=set()
for e in p.split(b'\x00'):
  if not e: continue
  s=e.decode(errors='ignore')
  if len(s)>=4:
    tracked.add(s[3:].split(' -> ')[-1])
bad=re.compile(r'\.bak(\.|-|$)|\.perlbak$|_backup(\.|$)|_restore(\.|$)|(~$)|\.swp$|\.tmp$|\.bk\.\d{8}T\d{6}Z')
hit=[t for t in tracked if bad.search(t)]
print("TRACKED_JUNK_COUNT", len(hit))
for h in sorted(hit)[:60]:
  print("TRACKED", h)
PY

B6. Generator fingerprints (who is creating these?)
(Helps distinguish editor/IDE vs scripts.)

grep -RniE 'backup|restore|\.bak|\.perlbak|mktemp|tempfile|Retention|reportkit' -- . \
  | sed -n '1,120p' || true

B7. Add-on specifics (optional, if you have a running container shell)
Run inside the BB-8 add-on container:

echo "SHELL: $(readlink -f /proc/$$/exe 2>/dev/null || echo ash)"; uname -a

…and if the repo is mounted inside HA OS, print where it is:

mount | grep -Ei 'home-assistant|addons|config' || true


⸻

What I’ll do with this
	•	Map which patterns are prevalent, where, and how big.
	•	Identify any junk that is tracked in git (highest priority to fix).
	•	Propose a tight .gitignore, a single canonical backup naming (*.bk.<UTC>), and a simple retention sweep that you can run safely in small steps (preview → normalize → corral → git untrack → verify).
	•	If needed, add guardrails (pre-commit include-scan and a tiny “retention sweep” that’s BusyBox-friendly).