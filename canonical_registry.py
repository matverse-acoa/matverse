import os
import json
import hashlib
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class RegistryConfig:
    project_dir: Path
    artifact_name: str
    version: str
    zenodo_token: Optional[str] = os.getenv("ZENODO_ACCESS_TOKEN")
    hf_token: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    sepolia_key: Optional[str] = os.getenv("SEPOLIA_PRIVATE_KEY")

@dataclass
class RegistryReceipt:
    artifact: str
    version: str
    canonical_hash: str
    zenodo_doi: Optional[str] = None
    sepolia_tx: Optional[str] = None
    hf_dataset: Optional[str] = None
    hf_space: Optional[str] = None
    status: str = "PARTIAL"
    timestamp_utc: str = datetime.now(timezone.utc).isoformat()
    parent_hash: str = "GENESIS"

class CanonicalRegistry:
    def __init__(self, cfg: RegistryConfig):
        self.cfg = cfg
        self.project_dir = cfg.project_dir
        self.receipt_path = self.project_dir / "canonical_registry_receipt.json"

    def compute_sha256(self, file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_parent_hash(self) -> str:
        if self.receipt_path.exists():
            try:
                data = json.loads(self.receipt_path.read_text())
                return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            except:
                pass
        return "GENESIS"

    def run_script(self, script_name: str, env: Dict[str, str] = None) -> str:
        script_path = self.project_dir / script_name
        if not script_path.exists():
            return f"Error: {script_name} not found"
        
        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                env={**os.environ, **(env or {})}
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Exception: {str(e)}"

    def execute(self) -> RegistryReceipt:
        artifact_path = self.project_dir / self.cfg.artifact_name
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact {self.cfg.artifact_name} not found")

        canonical_hash = self.compute_sha256(artifact_path)
        (self.project_dir / "canonical_hash.txt").write_text(canonical_hash)

        receipt = RegistryReceipt(
            artifact=self.cfg.artifact_name,
            version=self.cfg.version,
            canonical_hash=canonical_hash,
            parent_hash=self.get_parent_hash()
        )

        # 1. Zenodo
        print("Registering on Zenodo...")
        zenodo_out = self.run_script("zenodo_upload.py", {"ZENODO_ACESS_TOKEN": self.cfg.zenodo_token or ""})
        doi_file = self.project_dir / "zenodo_doi.txt"
        if doi_file.exists():
            receipt.zenodo_doi = doi_file.read_text().strip()

        # 2. Hugging Face
        print("Registering on Hugging Face...")
        hf_out = self.run_script("hf_upload.py")
        hf_links_file = self.project_dir / "hf_links.txt"
        if hf_links_file.exists():
            links = hf_links_file.read_text().strip().split("\n")
            receipt.hf_dataset = links[0] if len(links) > 0 else None
            receipt.hf_space = links[1] if len(links) > 1 else None

        # 3. Sepolia
        print("Registering on Sepolia...")
        sepolia_out = self.run_script("sepolia_register.py")
        tx_file = self.project_dir / "sepolia_tx.txt"
        if tx_file.exists():
            receipt.sepolia_tx = tx_file.read_text().strip()

        # Final Status
        if receipt.zenodo_doi and receipt.sepolia_tx and (receipt.hf_dataset or receipt.hf_space):
            receipt.status = "PASS"
        else:
            receipt.status = "PARTIAL"

        # Save Receipt
        receipt_data = asdict(receipt)
        self.receipt_path.write_text(json.dumps(receipt_data, indent=2))
        
        # Emit Merkle Root (Simplified for this receipt)
        receipt_root = hashlib.sha256(json.dumps(receipt_data, sort_keys=True).encode()).hexdigest()
        (self.project_dir / "receipt_root.txt").write_text(receipt_root)
        
        return receipt

if __name__ == "__main__":
    # Mock tokens for demonstration if not set
    cfg = RegistryConfig(
        project_dir=Path("/home/ubuntu/matverse_stack"),
        artifact_name="symbios-core-v1.tar.gz",
        version="1.0.0"
    )
    
    # Ensure artifact exists for mock test
    (cfg.project_dir / cfg.artifact_name).touch()
    
    registry = CanonicalRegistry(cfg)
    try:
        receipt = registry.execute()
        print(f"Registry Status: {receipt.status}")
        print(f"Canonical Hash: {receipt.canonical_hash}")
        print(f"Receipt saved to {registry.receipt_path}")
    except Exception as e:
        print(f"Registry failed: {e}")
