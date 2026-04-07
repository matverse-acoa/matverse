from typing import Any, Dict, Optional
from dataclasses import asdict

from .config import SGSI_AGENT_NAME, SGSI_AGENT_ORCID
from .models import AgentBody, ProcessRequest, PhiEncarnado
from .memory import ltm, stm, context_buffer
from .upstream import call_stack_api
from .sgsi import SGSI
from .utils import sha3_text, append_ledger


sgsi_agent = AgentBody(name=SGSI_AGENT_NAME, orcid=SGSI_AGENT_ORCID)
sgsi = SGSI(agent=sgsi_agent)

def process_query(req: ProcessRequest) -> Dict[str, Any]:
    # 1. Retrieve context from geometric memory
    context_retrieved = context_buffer.retrieve_context(req.input, ltm_top_k=req.top_k)
    
    # 2. Call STACK_API (with fallback)
    upstream_response = call_stack_api(req.input)
    
    # 3. Prepare initial metrics based on upstream performance
    latency = upstream_response.get("raw", {}).get("latency_ms", 0)
    remote_ok = upstream_response["mode"] == "remote_ok"
    losses = [0.0 if remote_ok else 1.0]
    
    # 4. Prepare payload for SGSI
    sgsi_payload = {
        "type": "user_query",
        "stimulus": {"text_input": req.input},
        "context": {"source": "matverse_stack_pipeline", **req.metadata},
        "losses": losses,
        "latency_ms": latency,
        "pole": 1.0,
        "replay_ok": True, 
        "receipt_ok": False,
        "publication_ok": False, 
        "chain_receipt": False,
        "realtime": remote_ok,
        "metrics_consistency": True,
    }

    # 5. Process with SGSI
    sgsi_result = sgsi.process(sgsi_payload)

    composed = {
        "input": req.input,
        "context": context_retrieved,
        "upstream": upstream_response,
        "sgsi_analysis": sgsi_result,
        "answer": upstream_response["answer"],
    }

    if req.add_to_memory:
        mnb_content = f"Q: {req.input}\nA: {upstream_response['answer']}\nSGSI Decision: {sgsi_result['decision']}"
        new_mnb = ltm.add(
            content=mnb_content,
            source="matverse_stack_pipeline",
            metadata={"kind": "dialogue_turn", **req.metadata, "sgsi_decision": sgsi_result["decision"]},
        )
        stm.add(new_mnb) # Add to short-term memory as well

        ledger_event = append_ledger(
            "process_query",
            {
                "input_hash": sha3_text(req.input),
                "ltm_size": len(ltm.items),
                "stm_size": len(stm.items),
                "mode": upstream_response["mode"],
                "sgsi_decision": sgsi_result["decision"],
                "sgsi_metrics": sgsi_result["metrics"]
            },
        )
        composed["ledger_hash"] = ledger_event["hash"]
    return composed

def get_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "ltm_items": len(ltm.items),
        "stm_items": len(stm.items),
        "stack_api_configured": bool(STACK_API_URL),
        "sgsi_mode": sgsi.state.organism_state["mode"],
    }

def add_memory_item(content: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    mnb = ltm.add(content, source, metadata)
    stm.add(mnb)
    return asdict(mnb)

def search_memory_items(query: str, top_k: int) -> Dict[str, Any]:
    return {
        "query": query,
        "results": ltm.search(query, top_k),
    }

def get_mnb_item(mnb_id: str) -> Optional[Dict[str, Any]]:
    item = ltm.get(mnb_id)
    return asdict(item) if item else None

def get_ledger_events(limit: int = 50) -> Dict[str, Any]:
    from .config import LEDGER_PATH
    if not LEDGER_PATH.exists():
        return {"items": []}
    lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
    items = [json.loads(line) for line in lines[-limit:]]
    return {"items": items}
