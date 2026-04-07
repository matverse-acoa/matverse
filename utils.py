import hashlib
import json
import math
import time
from typing import Any, Dict, List
from pathlib import Path

from .config import LEDGER_PATH

def sha3_text(text: str) -> str:
    return hashlib.sha3_256(text.encode("utf-8")).hexdigest()

def now_ts() -> float:
    return time.time()

def _hash_to_unit_interval(seed: str) -> float:
    h = hashlib.sha3_256(seed.encode("utf-8")).hexdigest()
    return int(h[:16], 16) / float(16**16 - 1)

def embed_text(text: str, dim: int = 24) -> List[float]:
    """
    Embedding local, determinístico e leve.
    """
    tokens = text.lower().split()
    if not tokens:
        return [0.0] * dim
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        for d in range(dim):
            seed = f"{tok}|{d}|{i}"
            val = _hash_to_unit_interval(seed)
            vec[d] += (2.0 * val - 1.0)
    norm = math.sqrt(sum(v * v for v in vec))
    if norm <= 1e-12:
        return [0.0] * dim
    return [v / norm for v in vec]

def vector_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vetores com dimensões diferentes.")
    na = vector_norm(a)
    nb = vector_norm(b)
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (na * nb)

def geometric_anchor_from_embedding(embedding: List[float]) -> Dict[str, float]:
    if not embedding:
        return {"x": 0.0, "y": 0.0, "z": 0.0, "curvature": 0.0}
    thirds = max(1, len(embedding) // 3)
    x = sum(embedding[:thirds]) / thirds
    y = sum(embedding[thirds:2 * thirds]) / max(1, len(embedding[thirds:2 * thirds]))
    z = sum(embedding[2 * thirds:]) / max(1, len(embedding[2 * thirds:]))
    curvature = abs(x) + abs(y) + abs(z)
    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "curvature": float(curvature),
    }

def estimate_psi(content: str, embedding: List[float]) -> float:
    if not content.strip():
        return 0.0
    lexical_density = min(1.0, len(set(content.lower().split())) / max(1, len(content.split())))
    stability = min(1.0, vector_norm(embedding))
    return round(0.6 * lexical_density + 0.4 * stability, 6)

def estimate_epsilon(content: str) -> float:
    n = len(content.strip())
    if n == 0:
        return 1.0
    return round(max(0.0, min(1.0, 1.0 / math.log2(n + 2))), 6)

def estimate_persistence(metadata: Dict[str, Any]) -> float:
    return round(0.9 if metadata else 0.75, 6)

def append_ledger(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    prev_hash = "GENESIS"
    if LEDGER_PATH.exists():
        try:
            lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
            if lines:
                last_line = lines[-1]
                prev_hash = json.loads(last_line)["hash"]
        except Exception:
            prev_hash = "GENESIS"
    event = {
        "ts": now_ts(),
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    event_raw = json.dumps(event, sort_keys=True, ensure_ascii=False)
    event_hash = sha3_text(event_raw)
    event["hash"] = event_hash
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
