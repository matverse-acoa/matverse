from __future__ import annotations
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


@dataclass
class MNB:
    """
    Mem-Nano-Bit canônico (v2).
    Unidade mínima de memória soberana e verificável.
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
    
    # Campo para o hash canônico v2 (h)
    h: str = ""

    def __post_init__(self):
        if not self.h:
            # Hash canônico v2: e (embedding) | psi | C (epsilon) | tau (persistence) | ts
            e_str = json.dumps(self.embedding, sort_keys=True)
            raw = f"{e_str}|{self.psi}|{self.epsilon}|{self.persistence}|{self.timestamp}"
            self.h = hashlib.sha256(raw.encode()).hexdigest()


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


class Decision(str, Enum):
    PASS = "PASS"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"
    CONDITIONAL = "CONDITIONAL"


@dataclass
class Metrics:
    psi: float
    theta: float
    omega: float
    cvar: float


@dataclass
class PhiEncarnado:
    chain_receipt: bool = False
    replay: bool = False
    publication: bool = False
    realtime: bool = False
    metrics_consistency: bool = False

@dataclass
class ProofState:
    merkle_root: str
    phi_encarnado: PhiEncarnado
    anchor_ref: Optional[str] = None


@dataclass
class SGSIState:
    organism_state: Dict[str, Any]
    memory: List[Dict[str, Any]] = field(default_factory=list)

    def merkle_root(self) -> str:
        import hashlib
        import json
        
        # No v2, usamos o campo 'h' se disponível, senão o hash do registro completo
        hashes = []
        for x in self.memory:
            if isinstance(x, dict) and "h" in x:
                hashes.append(x["h"])
            elif hasattr(x, "h"):
                hashes.append(getattr(x, "h"))
            else:
                hashes.append(hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest())
                
        if not hashes:
            return hashlib.sha256(b"").hexdigest()

        layer = hashes[:]
        while len(layer) > 1:
            if len(layer) % 2 != 0:
                layer.append(layer[-1])
            nxt = []
            for i in range(0, len(layer), 2):
                a = layer[i]
                b = layer[i + 1]
                nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
            layer = nxt
        return layer[0]


@dataclass
class AgentBody:
    """
    Corpo persistente: identidade e continuidade.
    """
    name: str
    orcid: Optional[str] = None

    def identity(self) -> Dict[str, Any]:
        return {"agent": self.name, "orcid": self.orcid}
