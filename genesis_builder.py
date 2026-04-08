import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# Mock Dataset based on user attachment
DATASET = [
    {"name": "MAVK", "psi": 0.99, "cvar": 0.02, "theta_hat": 0.9, "pole": 1},
    {"name": "DAQ", "psi": 0.95, "cvar": 0.08, "theta_hat": 0.8, "pole": 1},
    {"name": "CSR4", "psi": 0.92, "cvar": 0.03, "theta_hat": 0.85, "pole": 1}
]

def omega_score(psi, theta_hat, cvar, pole):
    return 0.4 * psi + 0.3 * theta_hat + 0.2 * (1.0 - cvar) + 0.1 * pole

def get_decision(psi, omega, cvar):
    if psi < 0.85 or cvar > 0.05:
        return "BLOCK"
    if omega >= 0.85:
        return "PASS"
    return "CONDITIONAL"

def hash_record(record: Dict[str, Any]) -> str:
    # Deterministic JSON hash
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def compute_merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    
    layer = hashes[:]
    while len(layer) > 1:
        if len(layer) % 2 != 0:
            layer.append(layer[-1])
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i+1]
            nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
        layer = nxt
    return layer[0]

def build_genesis():
    print("Building MatVerse Genesis Manifest...")
    records = []
    for entry in DATASET:
        score = omega_score(entry["psi"], entry["theta_hat"], entry["cvar"], entry["pole"])
        decision = get_decision(entry["psi"], score, entry["cvar"])
        
        record = {
            "name": entry["name"],
            "psi": entry["psi"],
            "cvar": entry["cvar"],
            "theta_hat": entry["theta_hat"],
            "pole": entry["pole"],
            "omega": round(score, 4),
            "decision": decision
        }
        record["h"] = hash_record(record)
        records.append(record)
        print(f"Record: {record['name']} | Omega: {record['omega']} | Decision: {record['decision']}")

    root = compute_merkle_root([r["h"] for r in records])
    
    genesis = {
        "version": "2.0.0-institutional",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "merkle_root": root,
        "records": records
    }
    
    manifest_path = Path("/home/ubuntu/matverse_stack/data/genesis_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(genesis, indent=2, ensure_ascii=False))
    
    print(f"\nGenesis Root: {root}")
    print(f"Manifest saved to: {manifest_path}")
    return genesis

def validate_replay(manifest_path: str):
    print("\nValidating Replay Determinism...")
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    
    records = data["records"]
    hashes = []
    for r in records:
        r_copy = dict(r)
        original_h = r_copy.pop("h")
        recomputed_h = hash_record(r_copy)
        if original_h != recomputed_h:
            print(f"FAILED: Record {r['name']} hash mismatch!")
            return False
        hashes.append(original_h)
    
    recomputed_root = compute_merkle_root(hashes)
    if recomputed_root != data["merkle_root"]:
        print(f"FAILED: Merkle Root mismatch!")
        return False
    
    print("SUCCESS: Genesis Manifest is valid and deterministic.")
    return True

if __name__ == "__main__":
    genesis = build_genesis()
    validate_replay("/home/ubuntu/matverse_stack/data/genesis_manifest.json")
