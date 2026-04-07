import gradio as gr
import json
from typing import Any, Dict

from .config import APP_NAME
from .models import ProcessRequest, MemoryAddRequest, MemorySearchRequest
from .service import process_query, add_memory_item, search_memory_items

def ui_process(text: str, top_k: int) -> str:
    req = ProcessRequest(input=text, top_k=top_k)
    result = process_query(req)
    return json.dumps(result, ensure_ascii=False, indent=2)

def ui_add_memory(content: str, source: str) -> str:
    mnb = add_memory_item(content, source, metadata={"kind": "manual"})
    return json.dumps(mnb, ensure_ascii=False, indent=2)

def ui_search_memory(query: str, top_k: int) -> str:
    res = search_memory_items(query, top_k)
    return json.dumps(res, ensure_ascii=False, indent=2)

def create_ui() -> gr.Blocks:
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
            mem_btn.click(ui_add_memory, inputs=[mem_text, mem_source], outputs=mem_out)
        with gr.Tab("Buscar Memória"):
            search_text = gr.Textbox(label="Query", lines=3)
            search_topk = gr.Slider(1, 20, value=5, step=1, label="Top-K")
            search_btn = gr.Button("Buscar")
            search_out = gr.Textbox(label="Resultados", lines=20)
            search_btn.click(ui_search_memory, inputs=[search_text, search_topk], outputs=search_out)
    return demo
