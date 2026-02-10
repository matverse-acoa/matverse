import os
import requests
from huggingface_hub import HfApi, create_repo, upload_file, upload_folder

HF_TOKEN = os.getenv("HF_TOKEN")
ORG_NAME = "MatverseHub"

def setup_hf_observatory():
    api = HfApi(token=HF_TOKEN)
    
    # 1. Criar ou verificar repositório para o Observatório (Dataset)
    repo_id = f"{ORG_NAME}/observatorio-cientifico-publico"
    try:
        create_repo(repo_id, repo_type="dataset", token=HF_TOKEN, exist_ok=True)
        print(f"✅ Repositório {repo_id} pronto.")
    except Exception as e:
        print(f"❌ Erro ao criar repositório: {e}")
        return

    # 2. Preparar arquivos para upload
    files_to_upload = [
        ("/home/ubuntu/MATVERSE_INSTITUTIONAL_MASTER.md", "MATVERSE_INSTITUTIONAL_MASTER.md"),
        ("/home/ubuntu/MATVERSE_PREREQUISITES.md", "MATVERSE_PREREQUISITES.md"),
        ("/home/ubuntu/zenodo_dois_publicados.md", "MANIFESTO_DOIS.md"),
        ("/home/ubuntu/MATVERSE_GENERAL_THEORY.md", "TEORIA_GERAL_UNIFICADA.md"),
        ("/home/ubuntu/sovereign-bootstrap-kit/matverse_organism/matverse_bundle_2026-02-10T20-00-28.821902.zip", "MATVERSE_ORGANISM_BUNDLE.zip"),
        ("/home/ubuntu/scientific_runtime_app.py", "SCIENTIFIC_RUNTIME_CORE.py"),
        ("/home/ubuntu/matverse_project/matverse_publication_strategy_consolidated.md", "ESTRATEGIA_PUBLICACAO.md"),
        ("/home/ubuntu/matverse_project/matverse_acoa_complete_architecture_analysis.md", "ANALISE_ARQUITETURA.md"),
        ("/home/ubuntu/perfil_orcid_resumo.md", "PERFIL_PESQUISADOR.md")
    ]

    for local_path, repo_path in files_to_upload:
        if os.path.exists(local_path):
            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=repo_path,
                    repo_id=repo_id,
                    repo_type="dataset"
                )
                print(f"✅ Arquivo {repo_path} enviado.")
            except Exception as e:
                print(f"❌ Erro ao enviar {repo_path}: {e}")

    # 3. Criar um README.md para o dataset no HF
    readme_content = f"""---
language: pt
license: cc-by-4.0
tags:
- science
- matverse
- autopoiesis
- quantum-semantic
pretty_name: Observatório Público Científico MatVerse
---

# Observatório Público Científico MatVerse

Este repositório centraliza a institucionalização epistemológica do MatVerse, contendo manifestos de DOIs, análises de arquitetura e estratégias de publicação.

## Teoria Geral Unificada
O documento central que amarra toda a arquitetura é o [TEORIA_GERAL_UNIFICADA.md](./TEORIA_GERAL_UNIFICADA.md).

## Papers Institucionalizados (Zenodo)
Consulte o arquivo [MANIFESTO_DOIS.md](./MANIFESTO_DOIS.md) para a lista completa de DOIs permanentes.

## Documentação Institucional Master
O arquivo [MATVERSE_INSTITUTIONAL_MASTER.md](./MATVERSE_INSTITUTIONAL_MASTER.md) é o blueprint oficial da infraestrutura de pesquisa do MatVerse.

## Guia de Pré-requisitos Científicos
O arquivo [MATVERSE_PREREQUISITES.md](./MATVERSE_PREREQUISITES.md) deve ser lido antes de qualquer paper para evitar fragmentação do conhecimento.

## MatVerse Organism Bundle (DOI-Ready)
O arquivo [MATVERSE_ORGANISM_BUNDLE.zip](./MATVERSE_ORGANISM_BUNDLE.zip) é o pacote completo do organismo vivo, contendo Atlas, Runtime, Twin e Ledger, selado com Merkle Root.

## Scientific Runtime
O código [SCIENTIFIC_RUNTIME_CORE.py](./SCIENTIFIC_RUNTIME_CORE.py) define as métricas de observabilidade (Ψ, Ω, α) para o Space.

---
**Status**: Operacional - Fase de Institucionalização Pública.
"""
    with open("/home/ubuntu/HF_README.md", "w") as f:
        f.write(readme_content)
    
    api.upload_file(
        path_or_fileobj="/home/ubuntu/HF_README.md",
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset"
    )
    print("✅ README.md do Hugging Face atualizado.")

if __name__ == "__main__":
    setup_hf_observatory()
