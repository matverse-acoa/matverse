from __future__ import annotations
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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


@dataclass
class AgentBody:
    """
    Corpo persistente: identidade e continuidade.
    """
    name: str
    orcid: Optional[str] = None

    def identity(self) -> Dict[str, Any]:
        return {"agent": self.name, "orcid": self.orcid}
