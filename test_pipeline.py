import sys
from pathlib import Path

# Add current dir to path to allow relative imports in service.py
sys.path.append(str(Path(__file__).parent.parent))

from matverse_stack.service import process_query
from matverse_stack.models import ProcessRequest

def test_basic_flow():
    print("Testing MatVerse Pipeline...")
    req = ProcessRequest(input="O que é o SGSI?", add_to_memory=True)
    result = process_query(req)
    
    print(f"Input: {result['input']}")
    print(f"Answer: {result['answer']}")
    print(f"SGSI Decision: {result['sgsi_analysis']['decision']}")
    print(f"Closure Ready: {result['sgsi_analysis']['closure_ready']}")
    if "ledger_hash" in result:
        print(f"Ledger Hash: {result['ledger_hash']}")
    print("Pipeline test completed successfully.")

if __name__ == "__main__":
    try:
        test_basic_flow()
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
