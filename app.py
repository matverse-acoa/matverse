from __future__ import annotations
import hashlib
import json
import math
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import gradio as gr
import uvicorn
from enum import Enum


class Decision(str, Enum):
    PASS = "PASS"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"


@dataclass
class Metrics:
    psi: float
    theta: float
    omega: float
    cvar: float


@dataclass
class ProofState:
    merkle_root: str
    replay_ok: bool
    receipt_ok: bool
    publication_ok: bool
    anchor_ref: Optional[str] = None


@dataclass
class SGSIState:
    organism_state: Dict[str, Any]
    memory: List[Dict[str, Any]] = field(default_factory=list)

    def merkle_root(self) -> str:
        hashes = [hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest() for x in self.memory]
        if not hashes:
            return hashlib.sha256(b"").hexdigest()

        layer = hashes[:]
        while len(layer) > 1:
            nxt = []
            for i in range(0, len(layer), 2):
                a = layer[i]
                b = layer[i + 1] if i + 1 < len(layer) else a
                nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
            layer = nxt
        return layer[0]


class AlgorithmBody:
    """
    Corpo A: processa perdas e calcula métricas.
    """

    def shape_losses(self, losses: List[float], lam: float = 0.5, cap: float = 1.0) -> List[float]:
        shaped = []
        for x in losses:
            x = max(0.0, float(x))
            y = x / (1.0 + x / lam)
            shaped.append(min(y, cap))
        return shaped

    def compute_cvar(self, losses: List[float], alpha: float = 0.95) -> float:
        if not losses:
            return 1.0
        xs = sorted(losses)
        idx = max(0, math.ceil(alpha * len(xs)) - 1)
        var = xs[idx]
        tail = [x for x in xs if x >= var]
        return sum(tail) / len(tail)

    def compute_metrics(self, payload: Dict[str, Any]) -> Metrics:
        losses_raw = payload.get("losses", [])
        losses = self.shape_losses(losses_raw)

        psi = float(payload.get("psi", max(0.0, min(1.0, 1.0 - (sum(losses) / max(len(losses), 1))))))
        theta = float(payload.get("theta", 1.0 / (1.0 + float(payload.get("latency_ms", 0.0)) / 1000.0)))
        cvar = self.compute_cvar(losses)
        omega = 0.4 * psi + 0.3 * theta + 0.2 * (1.0 - cvar) + 0.1 * float(payload.get("pole", 1.0))

        return Metrics(psi=psi, theta=theta, omega=omega, cvar=cvar)


class GovernanceBody:
    """
    Corpo G: decide admissibilidade.
    """

    def decide(self, metrics: Metrics) -> Decision:
        if metrics.cvar > 0.05:
            return Decision.BLOCK
        if metrics.psi >= 0.85 and metrics.omega >= 0.85:
            return Decision.PASS
        return Decision.ESCALATE


class SkillBody:
    """
    Corpo S: executa mutações válidas do pipeline.
    """

    def execute(self, decision: Decision, payload: Dict[str, Any], state: SGSIState) -> Dict[str, Any]:
        event = {
            "timestamp": time.time(),
            "decision": decision.value,
            "payload_type": payload.get("type", "generic"),
            "stimulus": payload.get("stimulus"),
            "context": payload.get("context", {}),
        }
        state.memory.append(event)

        if decision == Decision.PASS:
            state.organism_state["mode"] = "active"
        elif decision == Decision.ESCALATE:
            state.organism_state["mode"] = "review"
        else:
            state.organism_state["mode"] = "containment"

        return event


@dataclass
class AgentBody:
    """
    Corpo persistente: identidade e continuidade.
    """
    name: str
    orcid: Optional[str] = None

    def identity(self) -> Dict[str, Any]:
        return {"agent": self.name, "orcid": self.orcid}


class SGSI:
    """
    Sistema de Governança Soberana Integrada.
    """

    def __init__(self, agent: AgentBody):
        self.agent = agent
        self.algorithm = AlgorithmBody()
        self.governance = GovernanceBody()
        self.skill = SkillBody()
        self.state = SGSIState(organism_state={"mode": "idle"})

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        metrics = self.algorithm.compute_metrics(payload)
        decision = self.governance.decide(metrics)
        event = self.skill.execute(decision, payload, self.state)

        proof = ProofState(
            merkle_root=self.state.merkle_root(),
            replay_ok=bool(payload.get("replay_ok", False)),
            receipt_ok=bool(payload.get("receipt_ok", False)),
            publication_ok=bool(payload.get("publication_ok", False)),
            anchor_ref=payload.get("anchor_ref"),
        )

        return {
            "identity": self.agent.identity(),
            "decision": decision.value,
            "metrics": asdict(metrics),
            "event": event,
            "proof": asdict(proof),
            "organism_state": self.state.organism_state,
            "closure_ready": (
                metrics.psi >= 0.85
                and metrics.cvar <= 0.05
                and metrics.omega >= 0.85
                and proof.replay_ok
                and proof.receipt_ok
                and proof.publication_ok
            ),
        }

# ============================================================
# 1. CONFIG
# ============================================================
APP_NAME = "MatVerse STACK_API + Geometric Memory + MNBs"
APP_VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_PATH = DATA_DIR / "ledger.jsonl"
MEMORY_PATH = DATA_DIR / "memory.json"

STACK_API_URL = os.getenv("STACK_API_URL", "").strip()
STACK_API_KEY = os.getenv("STACK_API_KEY", "").strip()
STACK_API_TIMEOUT_SEC = float(os.getenv("STACK_API_TIMEOUT_SEC", "20"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "7860"))

# ============================================================
# 2. MODELS
# ============================================================
@dataclass
class MNB:
    """
    Mem-Nano-Bit mínimo, auditável e geométrico.
    """
    mnb_id: str
    content: str
    source: str
    timestamp: float
    content_hash: str
    embedding: List[float]
    norm: float
    geometric_anchor: Dict[str, float]
    psi: float
    epsilon: float
    kappa: str
    persistence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProcessRequest(BaseModel):
    input: str = Field(..., description="Texto de entrada do usuário.")
    top_k: int = Field(3, ge=1, le=20)
    add_to_memory: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemoryAddRequest(BaseModel):
    content: str
    source: str = "user"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=50)

# ============================================================
# 3. UTILS
# ============================================================
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

# ============================================================
# 4. MEMORY STORE
# ============================================================
class GeometricMemory:
    def __init__(self, path: Path):
        self.path = path
        self.items: List[MNB] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.items = []
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.items = [MNB(**item) for item in raw]
        except Exception:
            self.items = []

    def save(self) -> None:
        self.path.write_text(
            json.dumps([asdict(item) for item in self.items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, content: str, source: str = "user", metadata: Optional[Dict[str, Any]] = None) -> MNB:
        metadata = metadata or {}
        embedding = embed_text(content)
        anchor = geometric_anchor_from_embedding(embedding)
        mnb = MNB(
            mnb_id=str(uuid.uuid4()),
            content=content,
            source=source,
            timestamp=now_ts(),
            content_hash=sha3_text(content),
            embedding=embedding,
            norm=vector_norm(embedding),
            geometric_anchor=anchor,
            psi=estimate_psi(content, embedding),
            epsilon=estimate_epsilon(content),
            kappa="llm_memory",
            persistence=estimate_persistence(metadata),
            metadata=metadata,
        )
        self.items.append(mnb)
        self.save()
        append_ledger("memory_add", {"mnb_id": mnb.mnb_id, "hash": mnb.content_hash, "source": source})
        return mnb

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        q_emb = embed_text(query)
        scored = []
        for item in self.items:
            sim = cosine_similarity(q_emb, item.embedding)
            scored.append({
                "mnb_id": item.mnb_id,
                "content": item.content,
                "source": item.source,
                "psi": item.psi,
                "epsilon": item.epsilon,
                "persistence": item.persistence,
                "anchor": item.geometric_anchor,
                "similarity": round(sim, 6),
                "metadata": item.metadata,
            })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

memory = GeometricMemory(MEMORY_PATH)

sgsi_agent = AgentBody(name="MatVerse-Agent", orcid=None)
sgsi = SGSI(agent=sgsi_agent)

# ============================================================
# 5. STACK API WRAPPER (WITH FALLBACK)
# ============================================================
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

# ============================================================
# 6. CORE PIPELINE
# ============================================================
def process_query(user_input: str, top_k: int = 3, add_to_memory: bool = True, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    metadata = metadata or {}
    
    # Prepare payload for SGSI
    sgsi_payload = {
        "type": "user_query",
        "stimulus": {"text_input": user_input},
        "context": {"source": "stack_api_pipeline", **metadata},
        "losses": [], # Placeholder for actual loss calculation if applicable
        "latency_ms": 0, # Placeholder
        "pole": 1.0, # Placeholder
        "replay_ok": True, # Assuming replay is OK for this local demo
        "receipt_ok": False, # Not yet implemented for public closure
        "publication_ok": False, # Not yet implemented for public closure
        "anchor_ref": None,
    }

    # Call STACK_API (with fallback)
    upstream_response = call_stack_api(user_input)
    sgsi_payload["losses"].append(1.0 if upstream_response["mode"] != "remote_ok" else 0.0)
    sgsi_payload["latency_ms"] = upstream_response["raw"].get("latency_ms", 0)

    # Process with SGSI
    sgsi_result = sgsi.process(sgsi_payload)

    # Retrieve context from geometric memory
    hits = memory.search(user_input, top_k=top_k)

    composed = {
        "input": user_input,
        "context": {"retrieved": hits, "memory_size": len(memory.items)},
        "upstream": upstream_response,
        "sgsi_analysis": sgsi_result,
        "answer": upstream_response["answer"],
    }

    if add_to_memory:
        memory.add(
            content=f"Q: {user_input}\nA: {upstream_response['answer']}\nSGSI Decision: {sgsi_result['decision']}",
            source="stack_api_pipeline",
            metadata={"kind": "dialogue_turn", **metadata, "sgsi_decision": sgsi_result['decision']},
        )
        ledger_event = append_ledger(
            "process_query",
            {
                "input_hash": sha3_text(user_input),
                "memory_size": len(memory.items),
                "mode": upstream_response["mode"],
                "sgsi_decision": sgsi_result['decision'],
                "sgsi_metrics": asdict(sgsi_result['metrics'])
            },
        )
        composed["ledger_hash"] = ledger_event["hash"]
    return composed

# ============================================================
# 7. API
# ============================================================
app = FastAPI(title=APP_NAME, version=APP_VERSION)

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "memory_items": len(memory.items), "stack_api": bool(STACK_API_URL), "sgsi_mode": sgsi.state.organism_state["mode"]}

@app.post("/process")
def process(req: ProcessRequest) -> Dict[str, Any]:
    return process_query(req.input, req.top_k, req.add_to_memory, req.metadata)

# ============================================================
# 8. GRADIO UI
# ============================================================
def ui_process(text: str, top_k: int):
    result = process_query(text, top_k=top_k)
    return json.dumps(result, ensure_ascii=False, indent=2)

@app.post("/memory/add")
def memory_add(req: MemoryAddRequest) -> Dict[str, Any]:
    mnb = memory.add(req.content, source=req.source, metadata=req.metadata)
    return asdict(mnb)

@app.post("/memory/search")
def memory_search(req: MemorySearchRequest) -> Dict[str, Any]:
    return {
        "query": req.query,
        "results": memory.search(req.query, req.top_k),
    }

@app.get("/mnb/{mnb_id}")
def get_mnb(mnb_id: str) -> Dict[str, Any]:
    item = memory.get(mnb_id)
    if not item:
        raise HTTPException(status_code=404, detail="MNB não encontrado.")
    return asdict(item)

@app.get("/ledger")
def get_ledger(limit: int = 50) -> Dict[str, Any]:
    if not LEDGER_PATH.exists():
        return {"items": []}
    lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    items = [json.loads(line) for line in lines[-limit:]]
    return {"items": items}

with gr.Blocks(title=APP_NAME) as demo:
    gr.Markdown("# MatVerse STACK_API Demo + Geometric Memory + MNBs")
    gr.Markdown(
        "Interface mínima para testar a STACK_API, registrar MNBs, "
        "ancorar memória geométrica e consultar o ledger."
    )
    with gr.Tab("Processar"):
        input_text = gr.Textbox(label="Input", lines=4, placeholder="Digite sua entrada...")
        top_k_slider = gr.Slider(1, 10, value=3, step=1, label="Top-K memória")
        process_btn = gr.Button("Processar")
        process_out = gr.Textbox(label="Resultado", lines=20)
        process_btn.click(ui_process, inputs=[input_text, top_k_slider], outputs=process_out)
    with gr.Tab("Adicionar MNB"):
        mem_text = gr.Textbox(label="Conteúdo", lines=6)
        mem_source = gr.Textbox(label="Source", value="manual")
        mem_btn = gr.Button("Adicionar")
        mem_out = gr.Textbox(label="MNB", lines=20)
        mem_btn.click(memory_add, inputs=[mem_text, mem_source], outputs=mem_out)
    with gr.Tab("Buscar Memória"):
        search_text = gr.Textbox(label="Query", lines=3)
        search_topk = gr.Slider(1, 20, value=5, step=1, label="Top-K")
        search_btn = gr.Button("Buscar")
        search_out = gr.Textbox(label="Resultados", lines=20)
        search_btn.click(memory_search, inputs=[search_text, search_topk], outputs=search_out)

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

    # Initial SGSI test
    # sgsi_test_payload = {
    #     "type": "initialization_event",
    #     "stimulus": {"system_start": True},
    #     "context": {"source": "system"},
    #     "losses": [0.0],
    #     "latency_ms": 0,
    #     "pole": 1.0,
    #     "replay_ok": True,
    #     "receipt_ok": False,
    #     "publication_ok": False,
    #     "anchor_ref": None,
    # }
    # initial_sgsi_result = sgsi.process(sgsi_test_payload)
    # print("Initial SGSI State:", json.dumps(initial_sgsi_result, indent=2, ensure_ascii=False))
