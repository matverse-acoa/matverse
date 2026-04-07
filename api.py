from fastapi import FastAPI, HTTPException
from typing import Any, Dict

from .config import APP_NAME, APP_VERSION
from .models import ProcessRequest, MemoryAddRequest, MemorySearchRequest
from .service import (
    process_query,
    get_health,
    add_memory_item,
    search_memory_items,
    get_mnb_item,
    get_ledger_events,
)

app = FastAPI(title=APP_NAME, version=APP_VERSION)


@app.get("/health")
def health_endpoint() -> Dict[str, Any]:
    return get_health()


@app.post("/process")
def process_endpoint(req: ProcessRequest) -> Dict[str, Any]:
    return process_query(req)


@app.post("/memory/add")
def memory_add_endpoint(req: MemoryAddRequest) -> Dict[str, Any]:
    return add_memory_item(req.content, req.source, req.metadata)


@app.post("/memory/search")
def memory_search_endpoint(req: MemorySearchRequest) -> Dict[str, Any]:
    return search_memory_items(req.query, req.top_k)


@app.get("/mnb/{mnb_id}")
def get_mnb_endpoint(mnb_id: str) -> Dict[str, Any]:
    item = get_mnb_item(mnb_id)
    if not item:
        raise HTTPException(status_code=404, detail="MNB não encontrado.")
    return item


@app.get("/ledger")
def get_ledger_endpoint(limit: int = 50) -> Dict[str, Any]:
    return get_ledger_events(limit)
