---
name: canonical-registry
description: "Automates the triple canonical registration process (SHA-256 hash on Sepolia blockchain, paper/archive on Zenodo DOI, and dataset/proof space on Hugging Face). Use for anchoring project integrity, scientific publication, and public proof of existence."
---

# Canonical Registry

This skill automates the anchoring of digital artifacts across three sovereign layers: Blockchain (Immutability), Science (Persistence), and Public Data (Accessibility).

## Workflow

### 1. Artifact Preparation
- Collect all project files into a directory.
- Generate a PDF of the paper/documentation.
- Create a `.tar.gz` archive of the core files.
- Calculate the SHA-256 hash of the archive.

### 2. Zenodo Registration (Scientific Anchor)
- Use `scripts/zenodo_upload.py` to upload the PDF and archive.
- Requires `ZENODO_ACCESS_TOKEN`.
- Output: DOI (Digital Object Identifier).

### 3. Hugging Face Publication (Public Proof)
- Use `scripts/hf_upload.py` to create a dataset and a Gradio proof space.
- Requires `HUGGINGFACE_TOKEN` and `HF_USER`.
- Includes the Zenodo DOI and Sepolia Hash in the public space.

### 4. Sepolia Registration (On-chain Anchor)
- Use `scripts/sepolia_register.py` to anchor the hash in the blockchain.
- Requires `SEPOLIA_PRIVATE_KEY`.
- Output: Transaction ID (TX).

## Bundled Scripts

- `scripts/zenodo_upload.py`: Handles deposition creation, file upload, and publication.
- `scripts/hf_upload.py`: Automates dataset creation and space deployment.
- `scripts/sepolia_register.py`: Signs and sends a transaction with the hash in the data field.

## Requirements

- **Zenodo**: API Token (Write permission).
- **Hugging Face**: Access Token (Write permission).
- **Sepolia**: Private Key with small amount of Sepolia ETH for gas.

## Best Practices
- Always calculate the hash *before* any upload to ensure the version is locked.
- Use the Gradio SDK for proof spaces for maximum compatibility.
- Store all registration links (DOI, TX, HF URL) in a final consolidated report.
