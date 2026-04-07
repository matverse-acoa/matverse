import json
import math
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib

from .models import Decision, Metrics, ProofState, SGSIState, AgentBody, PhiEncarnado


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
        return sum(tail) / len(tail) if len(tail) > 0 else 0.0

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

        phi_encarnado = PhiEncarnado(
            chain_receipt=bool(payload.get("chain_receipt", False)),
            replay=bool(payload.get("replay_ok", False)), # Renamed for consistency
            publication=bool(payload.get("publication_ok", False)),
            realtime=bool(payload.get("realtime", False)),
            metrics_consistency=bool(payload.get("metrics_consistency", False)),
        )

        proof = ProofState(
            merkle_root=self.state.merkle_root(),
            phi_encarnado=phi_encarnado,
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
                and proof.phi_encarnado.replay
                and proof.phi_encarnado.chain_receipt
                and proof.phi_encarnado.publication
                and proof.phi_encarnado.realtime
                and proof.phi_encarnado.metrics_consistency
            ),
        }
