import re, datetime, sys

VALID_DOMAINS = [
    "binary_sensor","sensor","light","switch",
    "automation","script","person","input_boolean","device_tracker"
]

RE_STATES      = re.compile(r"states\(['\"]([A-Za-z0-9_]+\.[A-Za-z0-9_]+)['\"]\)")
RE_STATE_ATTR  = re.compile(r"state_attr\(['\"]([A-Za-z0-9_]+\.[A-Za-z0-9_]+)['\"],\s*['\"][^'^\"]+['\"]\)")
RE_IS_STATE    = re.compile(r"is_state\(['\"]([A-Za-z0-9_]+\.[A-Za-z0-9_]+)['\"],\s*['\"][^'^\"]+['\"]\)")
RE_SOURCES     = re.compile(r"{\%[\s]*set\s+sources\s*=\s*\[(.*?)\][\s\%]*}", re.S)
RE_SOURCES_ENT = re.compile(r"'entity'\s*:\s*'([A-Za-z0-9_]+\.[A-Za-z0-9_]+)'")
RE_MACRO       = re.compile(r"{\%[\s]*from\s+'([^']+)'\s+import\s+[^\%]+\%}")

def is_valid_entity(eid: str) -> bool:
    try:
        d, _ = eid.split(".", 1)
        return d in VALID_DOMAINS
    except Exception:
        return False

def extract_entities_from_state_block(txt: str):
    if not isinstance(txt, str):
        return [], []
    ents=set(); macros=set()
    for rx in (RE_STATES, RE_STATE_ATTR, RE_IS_STATE):
        for m in rx.findall(txt):
            if is_valid_entity(m): ents.add(m)
    for blk in RE_SOURCES.findall(txt):
        for m in RE_SOURCES_ENT.findall(blk):
            if is_valid_entity(m): ents.add(m)
    for m in RE_MACRO.findall(txt):
        macros.add(m)
    return sorted(ents), sorted(macros)

def today_iso_date() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def dbg(msg: str):
    print(f"[DEBUG] {msg}", file=sys.stderr)
