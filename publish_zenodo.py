import requests
import json
import os
from pathlib import Path

ZENODO_TOKEN = os.getenv("ZENODO_TOKEN")
API_URL = "https://zenodo.org/api"

def create_deposition(metadata):
    url = f"{API_URL}/deposit/depositions?access_token={ZENODO_TOKEN}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(metadata), headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Erro ao criar deposição: {response.status_code} - {response.text}")
        return None

def upload_file(deposition_id, file_path):
    bucket_url = get_bucket_url(deposition_id)
    if not bucket_url:
        return False
    
    filename = os.path.basename(file_path)
    url = f"{bucket_url}/{filename}?access_token={ZENODO_TOKEN}"
    
    with open(file_path, "rb") as f:
        response = requests.put(url, data=f)
    
    if response.status_code in [200, 201]:
        print(f"✅ Arquivo {filename} enviado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao enviar arquivo {filename}: {response.status_code} - {response.text}")
        return False

def get_bucket_url(deposition_id):
    url = f"{API_URL}/deposit/depositions/{deposition_id}?access_token={ZENODO_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["links"]["bucket"]
    return None

def publish_deposition(deposition_id):
    url = f"{API_URL}/deposit/depositions/{deposition_id}/actions/publish?access_token={ZENODO_TOKEN}"
    response = requests.post(url)
    if response.status_code == 202:
        print(f"🚀 Deposição {deposition_id} publicada com sucesso!")
        return response.json()
    else:
        print(f"❌ Erro ao publicar deposição: {response.status_code} - {response.text}")
        return None

def prepare_paper_metadata(title, description, creators, keywords):
    return {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "preprint",
            "description": description,
            "creators": creators,
            "keywords": keywords,
            "access_right": "open",
            "license": "cc-by-4.0"
        }
    }

# Dados dos Papers baseados na análise dos arquivos LaTeX e PDFs
PAPERS = [
    {
        "id": 0,
        "title": "Foundations of Coherent Action Spaces: Mathematical Framework",
        "description": "This paper establishes the foundational mathematical framework for coherent action spaces (CAS), introducing manifold structures and coherence metrics essential for autonomous systems. Part of the MatVerse Scientific Constitution.",
        "file": "/home/ubuntu/matverse_project/paper-0-foundations-v1.tar.gz",
        "keywords": ["Coherent Action Spaces", "Mathematical Framework", "Manifold Structures", "Autonomous Systems", "MatVerse"]
    },
    {
        "id": 1,
        "title": "Paper 1 — Ω-GATE / ACOA Kernel — A Reference Implementation for Invariant-Based Governance",
        "description": "This paper presents a minimal, executable reference implementation of invariant-based governance via the Ω-GATE / ACOA kernel. The kernel evaluates the admissibility of actions, states, or claims using externally observable invariants. Part of the MatVerse Scientific Constitution.",
        "file": "/home/ubuntu/matverse_project/paper-1-coherent-action-spaces-v1.tar.gz",
        "keywords": ["Ω-GATE", "ACOA", "Invariant-Based Governance", "Sovereign Systems", "MatVerse"]
    },
    {
        "id": 2,
        "title": "Autopoietic Coherent Action Orchestration (ACOA): Self-Organizing Autonomous Systems",
        "description": "This paper introduces ACOA (Autopoietic Coherent Action Orchestration), a self-organizing framework where autonomous agents dynamically maintain coherence through adaptive manifold learning. Part of the MatVerse Scientific Constitution.",
        "file": "/home/ubuntu/matverse_project/paper-2-acoa-v1.tar.gz",
        "keywords": ["ACOA", "Autopoiesis", "Self-Organization", "Autonomous Systems", "MatVerse"]
    },
    {
        "id": 3,
        "title": "The Omega-Gate Kernel: Quantum-Inspired Coherence Amplification",
        "description": "We introduce the Omega-Gate Kernel (Ω-GK), a quantum-inspired mechanism for exponential coherence amplification in ACOA systems. The kernel enables superposition-like states in classical autonomous systems. Part of the MatVerse Scientific Constitution.",
        "file": "/home/ubuntu/matverse_project/paper-3-omega-gate-v1.tar.gz",
        "keywords": ["Omega-Gate Kernel", "Quantum-Inspired", "Coherence Amplification", "Autonomous Systems", "MatVerse"]
    }
]

CREATORS = [{"name": "Arêas, Mateus", "orcid": "0009-0008-2973-4047", "affiliation": "MatVerse Institute"}]

if __name__ == "__main__":
    # Exemplo de execução para o Paper 0
    paper = PAPERS[0]
    metadata = prepare_paper_metadata(paper["title"], paper["description"], CREATORS, paper["keywords"])
    
    print(f"Iniciando processo para: {paper['title']}")
    results = []
    for paper in PAPERS:
        print(f"\n--- Processando: {paper['title']} ---")
        metadata = prepare_paper_metadata(paper["title"], paper["description"], CREATORS, paper["keywords"])
        deposition = create_deposition(metadata)
        if deposition:
            dep_id = deposition["id"]
            if upload_file(dep_id, paper["file"]):
                published = publish_deposition(dep_id)
                if published:
                    doi = published.get("doi")
                    results.append({"title": paper["title"], "id": dep_id, "doi": doi})
                    print(f"✅ DOI gerado: {doi}")
    
    print("\n=== RESUMO DA PUBLICAÇÃO ===")
    for res in results:
        print(f"- {res['title']}: DOI {res['doi']} (ID: {res['id']})")
