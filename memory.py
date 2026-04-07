import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import MEMORY_PATH
from .models import MNB
from .utils import embed_text, vector_norm, cosine_similarity, geometric_anchor_from_embedding, estimate_psi, estimate_epsilon, estimate_persistence, now_ts, sha3_text
from .ledger import append_ledger


class LongTermMemory:
    def __init__(self, path: Path = MEMORY_PATH):
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
            json.dumps([item.__dict__ for item in self.items], ensure_ascii=False, indent=2),
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
        append_ledger("ltm_add", {"mnb_id": mnb.mnb_id, "hash": mnb.content_hash, "source": source})
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


class ShortTermMemory:
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.items: List[MNB] = []

    def add(self, mnb: MNB) -> None:
        self.items.append(mnb)
        if len(self.items) > self.capacity:
            self.items.pop(0)  # Remove the oldest item
        append_ledger("stm_add", {"mnb_id": mnb.mnb_id, "hash": mnb.content_hash, "source": mnb.source})

    def get_recent(self, count: int = 5) -> List[Dict[str, Any]]:
        return [item.__dict__ for item in self.items[-count:]]


class ContextBuffer:
    def __init__(self, ltm: LongTermMemory, stm: ShortTermMemory):
        self.ltm = ltm
        self.stm = stm

    def retrieve_context(self, query: str, ltm_top_k: int = 3, stm_recent_count: int = 3) -> Dict[str, Any]:
        ltm_hits = self.ltm.search(query, top_k=ltm_top_k)
        stm_hits = self.stm.get_recent(count=stm_recent_count)
        
        # Combine and deduplicate context, prioritizing STM if overlap
        combined_context = {mnb['mnb_id']: mnb for mnb in ltm_hits}
        for mnb in stm_hits:
            combined_context[mnb['mnb_id']] = mnb

        append_ledger("context_retrieve", {"query_hash": sha3_text(query), "ltm_hits": len(ltm_hits), "stm_hits": len(stm_hits)})
        return {
            "query": query,
            "ltm_retrieved": ltm_hits,
            "stm_retrieved": stm_hits,
            "combined_context": list(combined_context.values()),
            "ltm_size": len(self.ltm.items),
            "stm_size": len(self.stm.items),
        }


# Instantiate memory components
ltm = LongTermMemory()
stm = ShortTermMemory()
context_buffer = ContextBuffer(ltm, stm)
