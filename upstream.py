import requests
from typing import Any, Dict

from .config import STACK_API_URL, STACK_API_KEY, STACK_API_TIMEOUT_SEC
from .utils import now_ts

def call_stack_api(user_input: str) -> Dict[str, Any]:
    if not STACK_API_URL:
        return {
            "mode": "local_fallback",
            "answer": f"Fallback local MatVerse para: {user_input}",
            "raw": {"input": user_input},
        }
    headers = {"Content-Type": "application/json"}
    if STACK_API_KEY:
        headers["Authorization"] = f"Bearer {STACK_API_KEY}"
    payload = {"input": user_input, "timestamp": now_ts()}
    try:
        resp = requests.post(
            STACK_API_URL, json=payload, headers=headers, timeout=STACK_API_TIMEOUT_SEC,
        )
        try:
            raw = resp.json()
        except Exception:
            raw = {"text": resp.text}
        if resp.status_code >= 400:
            return {
                "mode": "remote_error",
                "status_code": resp.status_code,
                "answer": f"Erro remoto HTTP {resp.status_code}",
                "raw": raw,
            }
        return {
            "mode": "remote_ok",
            "status_code": resp.status_code,
            "answer": raw.get("answer") or raw.get("output") or raw.get("result") or resp.text,
            "raw": raw,
        }
    except Exception as e:
        return {
            "mode": "exception_fallback",
            "answer": f"Falha ao chamar STACK_API: {e}",
            "raw": {"exception": str(e)},
        }
