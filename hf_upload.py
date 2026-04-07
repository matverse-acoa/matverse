import os
from huggingface_hub import HfApi, create_repo

token = os.environ.get('HUGGINGFACE_TOKEN')
api = HfApi(token=token)

def upload_dataset():
    user = api.whoami()['name']
    repo_id = f"{user}/symbios-core-dataset"
    try:
        create_repo(repo_id, repo_type="dataset", exist_ok=True)
        print(f"Dataset repo created/exists: {repo_id}")
        
        # Upload files
        api.upload_file(
            path_or_fileobj="/home/ubuntu/symbios_project/mnb_samples.json",
            path_in_repo="mnb_samples.json",
            repo_id=repo_id,
            repo_type="dataset"
        )
        api.upload_file(
            path_or_fileobj="/home/ubuntu/symbios_project/psi_metrics.json",
            path_in_repo="psi_metrics.json",
            repo_id=repo_id,
            repo_type="dataset"
        )
        print(f"Files uploaded to dataset repo: {repo_id}")
        return repo_id
    except Exception as e:
        print(f"Error in dataset upload: {e}")
        return None

def create_proof_space(dataset_repo_id, zenodo_doi, canonical_hash):
    user = api.whoami()['name']
    repo_id = f"{user}/symbios-proof"
    try:
        create_repo(repo_id, repo_type="space", space_sdk="streamlit", exist_ok=True)
        print(f"Space repo created/exists: {repo_id}")
        
        app_content = f"""
import streamlit as st

st.set_page_config(page_title="symbiOS Canonical Proof", page_icon="🔷")

st.title("🔷 symbiOS Canonical Proof")
st.markdown("---")

st.subheader("Core Information")
st.write("**Canonical Hash (SHA-256):**")
st.code("{canonical_hash}")

st.write("**Scientific DOI (Zenodo):**")
st.markdown(f"[https://doi.org/{{'{zenodo_doi}'}}](https://doi.org/{{'{zenodo_doi}'}})")

st.write("**Public Dataset (Hugging Face):**")
st.markdown(f"[https://huggingface.co/datasets/{{'{dataset_repo_id}'}}](https://huggingface.co/datasets/{{'{dataset_repo_id}'}})")

st.markdown("---")
st.subheader("Architecture")
st.markdown(\"\"\"
- **MNB**: Mem-Nano-Bit (Minimal Unit of Memory)
- **COER**: Coherence Engine
- **S²**: Security² (Meta-Security)
\"\"\")

st.info("This space serves as a public proof of the existence and integrity of the symbiOS kernel.")
"""
        with open("/home/ubuntu/symbios_project/app.py", "w") as f:
            f.write(app_content)
            
        api.upload_file(
            path_or_fileobj="/home/ubuntu/symbios_project/app.py",
            path_in_repo="app.py",
            repo_id=repo_id,
            repo_type="space"
        )
        print(f"App uploaded to space repo: {repo_id}")
        return repo_id
    except Exception as e:
        print(f"Error in space creation: {e}")
        return None

if __name__ == "__main__":
    if not token:
        print("Hugging Face token not found.")
    else:
        # Get hash and DOI
        with open("/home/ubuntu/symbios_project/canonical_hash.txt", "r") as f:
            canonical_hash = f.read().strip()
        with open("/home/ubuntu/symbios_project/zenodo_doi.txt", "r") as f:
            zenodo_doi = f.read().strip()
            
        dataset_repo = upload_dataset()
        if dataset_repo:
            space_repo = create_proof_space(dataset_repo, zenodo_doi, canonical_hash)
            if space_repo:
                print(f"Hugging Face setup complete.")
                with open("/home/ubuntu/symbios_project/hf_links.txt", "w") as f:
                    f.write(f"Dataset: https://huggingface.co/datasets/{dataset_repo}\n")
                    f.write(f"Space: https://huggingface.co/spaces/{space_repo}\n")
