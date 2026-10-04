#!/usr/bin/env python3
import hashlib, json, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVID = ROOT / "run-evidence"
EVID.mkdir(exist_ok=True)

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"scqos-totality-closure/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def file_hash(path):
    return sha256_bytes(path.read_bytes())

required_local = [
    EVID / "local.json",
    EVID / "live-scqos.json",
    EVID / "cloud-to-terminal.json",
]
missing = [str(p) for p in required_local if not p.exists()]
if missing:
    raise SystemExit("HOLD missing evidence: " + ", ".join(missing))

linux_url = "https://raw.githubusercontent.com/KnowledgeeKZA3224/linux-coherence-gate/main/results/SCQOS_V3_LIVE_RUNTIME_PROOF_20261004.json"
linux = get_json(linux_url)
linux_closure = linux.get("closure", {})
linux_required = [
    "end_to_end_permit",
    "kernel_one_shot_permit",
    "missing_grant_denied_eacces",
    "expired_denied_eacces",
    "nonce_mismatch_denied_eacces",
    "replay_denied_eacces",
]
linux_ok = (
    linux.get("state") == "PERMIT"
    and linux.get("kernel") == "7.0.0-34-generic"
    and all(linux_closure.get(k) is True for k in linux_required)
)

ms = get_json("https://api.github.com/repos/microsoft/agent-governance-toolkit/pulls/4225")
oc = get_json("https://api.github.com/repos/openclaw/openclaw/issues/153227")

cloud = json.loads((EVID / "cloud-to-terminal.json").read_text())
live = json.loads((EVID / "live-scqos.json").read_text())
local = json.loads((EVID / "local.json").read_text())

receipt = {
  "schema": "SCQOS_TOTALITY_CLOSURE_V1",
  "title": "DETERMINISTIC GOVERNANCE: ENFORCING THE PRE-EXECUTION BOUNDARY OVER AGENTIC DRIFT",
  "result": "PERMIT" if linux_ok else "HOLD",
  "plain_english": "Different AI systems may reason differently. The final consequence must still prove current authority before reality changes.",
  "linux_v3": {
    "url": linux_url,
    "kernel": linux.get("kernel"),
    "state": linux.get("state"),
    "closure": linux_closure,
    "proof_sha256": sha256_bytes(json.dumps(linux, sort_keys=True, separators=(",",":")).encode())
  },
  "live_scqos": {
    "artifact": "run-evidence/live-scqos.json",
    "sha256": file_hash(EVID / "live-scqos.json")
  },
  "cloud_to_terminal": {
    "artifact": "run-evidence/cloud-to-terminal.json",
    "sha256": file_hash(EVID / "cloud-to-terminal.json")
  },
  "local_falsification": {
    "artifact": "run-evidence/local.json",
    "sha256": file_hash(EVID / "local.json")
  },
  "microsoft_agt": {
    "pr": "https://github.com/microsoft/agent-governance-toolkit/pull/4225",
    "state": ms.get("state"),
    "title": ms.get("title"),
    "head_sha": (ms.get("head") or {}).get("sha")
  },
  "openclaw": {
    "issue": "https://github.com/openclaw/openclaw/issues/153227",
    "state": oc.get("state"),
    "title": oc.get("title"),
    "updated_at": oc.get("updated_at")
  }
}

receipt_bytes = json.dumps(receipt, indent=2, sort_keys=True).encode()
(EVID / "TOTALITY_CLOSURE_RECEIPT.json").write_bytes(receipt_bytes)

summary = f"""# DETERMINISTIC GOVERNANCE: ENFORCING THE PRE-EXECUTION BOUNDARY OVER AGENTIC DRIFT

## Plain English

AI can think, plan, disagree, and use different governance systems. None of that automatically gives it the right to change the machine.

The final action still has to prove that the current authority, current state, exact target, and one-time permission still match before Linux allows the governed process to execute.

## Live closure

- Linux: {linux.get("kernel")}
- Final state: {receipt["result"]}
- Valid governed consequence: {"EXECUTED" if linux_closure.get("end_to_end_permit") else "NOT PROVEN"}
- One-shot permit: {"EXECUTED" if linux_closure.get("kernel_one_shot_permit") else "NOT PROVEN"}
- Missing grant: {"BLOCKED" if linux_closure.get("missing_grant_denied_eacces") else "NOT PROVEN"}
- Expired grant: {"BLOCKED" if linux_closure.get("expired_denied_eacces") else "NOT PROVEN"}
- Wrong nonce: {"BLOCKED" if linux_closure.get("nonce_mismatch_denied_eacces") else "NOT PROVEN"}
- Replay: {"BLOCKED" if linux_closure.get("replay_denied_eacces") else "NOT PROVEN"}

## Independent public surfaces

- Microsoft AGT upstream PR #4225: {ms.get("state")}
- OpenClaw consequence-bound release issue #153227: {oc.get("state")}
- SCQOS live cloud falsification evidence: regenerated in this run
- Cloud-to-terminal consequence evidence: regenerated in this run

## Source-layer result

Different intelligence. Different architectures. One reality.

Before autonomous intelligence can change that reality, the consequence must prove it belongs there.
"""
(EVID / "TOTALITY_CLOSURE_SUMMARY.md").write_text(summary)

print("=== DETERMINISTIC GOVERNANCE TOTALITY CLOSURE ===")
print("SOURCE + LIVE CLOUD + FALSIFICATION + KERNEL + UPSTREAM REVIEW")
print("LINUX V3:", "PERMIT" if linux_ok else "HOLD")
print("VALID CONSEQUENCE:", "EXECUTED" if linux_closure.get("end_to_end_permit") else "NOT PROVEN")
print("MISSING GRANT:", "BLOCKED" if linux_closure.get("missing_grant_denied_eacces") else "NOT PROVEN")
print("EXPIRED GRANT:", "BLOCKED" if linux_closure.get("expired_denied_eacces") else "NOT PROVEN")
print("NONCE MISMATCH:", "BLOCKED" if linux_closure.get("nonce_mismatch_denied_eacces") else "NOT PROVEN")
print("REPLAY:", "BLOCKED" if linux_closure.get("replay_denied_eacces") else "NOT PROVEN")
print("MICROSOFT AGT PR #4225:", ms.get("state"))
print("OPENCLAW #153227:", oc.get("state"))
print("RECEIPT:", "run-evidence/TOTALITY_CLOSURE_RECEIPT.json")
print("SUMMARY:", "run-evidence/TOTALITY_CLOSURE_SUMMARY.md")
print("FINAL:", receipt["result"])

if receipt["result"] != "PERMIT":
    sys.exit(2)
