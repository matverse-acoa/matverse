import json
from typing import Any, Dict

from .config import LEDGER_PATH
from .utils import sha3_text, now_ts

def append_ledger(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    prev_hash = "GENESIS"
    if LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0:
        try:
            with LEDGER_PATH.open("r", encoding="utf-8") as f:
                # Read last non-empty line
                lines = f.readlines()
                last_line = None
                for line in reversed(lines):
                    if line.strip():
                        last_line = line
                        break
                if last_line:
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
