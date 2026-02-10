#!/usr/bin/env bash
set -e

echo "⚙️ BLACKSTART MATVERSE..."

ROOT=matverse_organism
mkdir -p $ROOT
cd $ROOT

########################################
# ATLAS — Constituição
########################################

mkdir -p Atlas/evidence-map/textual

cat > Atlas/invariants.json <<EOF
{
 "PSI_MIN":0.72,
 "ALPHA_MIN":1.0,
 "CVAR_MAX":0.35
}
EOF

########################################
# SEAL ATLAS (Merkle)
########################################

cat > seal_atlas.py <<'EOF'
import hashlib
from pathlib import Path

def merkle(files):
    if not files:
        return "0"
    hashes=[hashlib.sha3_256(Path(f).read_bytes()).digest() for f in files]
    hashes.sort() # Garantir determinismo

    while len(hashes)>1:
        new_hashes = []
        for i in range(0, len(hashes), 2):
            if i + 1 < len(hashes):
                new_hashes.append(hashlib.sha3_256(hashes[i] + hashes[i+1]).digest())
            else:
                new_hashes.append(hashes[i])
        hashes = new_hashes
    return hashes[0].hex()

files=list(Path("Atlas").rglob("*.*"))
if files:
    print("MERKLE_ROOT:",merkle(files))
else:
    print("No files found in Atlas/")
EOF

########################################
# RUNTIME
########################################

mkdir -p runtime

cat > runtime/ledger.py <<'EOF'
import sqlite3,hashlib,json

def get_conn():
    conn=sqlite3.connect("ledger.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS artifacts(
    id TEXT PRIMARY KEY,
    payload TEXT
    )
    """)
    return conn

def register(payload):
    conn = get_conn()
    raw=json.dumps(payload,sort_keys=True).encode()
    h=hashlib.sha3_256(raw).hexdigest()

    conn.execute("INSERT OR REPLACE INTO artifacts VALUES (?,?)",(h,raw))
    conn.commit()
    conn.close()
    return h
EOF

cat > runtime/app.py <<'EOF'
from fastapi import FastAPI,HTTPException
from ledger import register
import numpy as np

app=FastAPI(title="MatVerse Runtime")

def coherence(signal):
    s=np.array(signal)
    return float(1-(s.std()/(abs(s.mean())+1e-9)))

@app.post("/submit")
def submit(size:int=128):

    signal=np.random.normal(10,1,size)

    psi=coherence(signal)

    if psi<0.72:
        raise HTTPException(403,"BLOCKED_BY_INVARIANT")

    payload={
        "psi":psi,
        "size":size
    }

    h=register(payload)

    return {
        "artifact_id":h,
        "psi":psi,
        "decision":"PASS"
    }

@app.get("/metrics")
def metrics():
    return {"psi_global":0.91,"regime":"STABLE"}
EOF

########################################
# TWIN ESPelhado
########################################

mkdir -p twin

cp runtime/app.py twin/app.py
cp runtime/ledger.py twin/ledger.py

########################################
# DATASET LOGGER
########################################

cat > trajectory_logger.py <<'EOF'
import pandas as pd
import os

FILE="trajectories.parquet"

def log(state):

    df=pd.DataFrame([state])

    if os.path.exists(FILE):
        old=pd.read_parquet(FILE)
        df=pd.concat([old,df])

    df.to_parquet(FILE)
EOF

########################################
# PUBLISHER (DOI READY)
########################################

cat > publisher.py <<'EOF'
import zipfile,datetime,os

name="matverse_bundle_"+datetime.datetime.utcnow().isoformat().replace(":", "-")+".zip"

with zipfile.ZipFile(name,'w') as z:
    for root,_,files in os.walk("."):
        for f in files:
            if "bundle" not in f and not f.endswith(".zip"):
                z.write(os.path.join(root,f))

print("Bundle DOI-ready:",name)
EOF

########################################
# DOCKER COMPOSE — organismo vivo
########################################

cat > docker-compose.yml <<EOF
version: '3'

services:

 runtime:
   image: python:3.11
   working_dir: /app
   volumes:
     - ./runtime:/app
   command: bash -c "pip install fastapi uvicorn numpy pandas pyarrow && uvicorn app:app --host 0.0.0.0 --port 8000"
   ports:
     - "8000:8000"

 twin:
   image: python:3.11
   working_dir: /app
   volumes:
     - ./twin:/app
   command: bash -c "pip install fastapi uvicorn numpy && uvicorn app:app --host 0.0.0.0 --port 8001"
   ports:
     - "8001:8001"
EOF

########################################
# MAKEFILE — controle do organismo
########################################

cat > Makefile <<EOF
blackstart:
	docker compose up -d

seal:
	python3 seal_atlas.py

publish:
	python3 publisher.py
EOF

echo "✅ MATVERSE BOOTSTRAPPED"
echo "Execute:"
echo "cd $ROOT && make seal && make publish"
