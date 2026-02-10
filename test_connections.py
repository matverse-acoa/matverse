import requests
import os

ZENODO_TOKEN = os.getenv("ZENODO_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

def test_zenodo():
    print("Testando conexão com Zenodo...")
    url = f"https://zenodo.org/api/deposit/depositions?access_token={ZENODO_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Zenodo: Conexão bem-sucedida!")
            return True
        else:
            print(f"❌ Zenodo: Erro {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Zenodo: Exceção - {str(e)}")
        return False

def test_hf():
    print("\nTestando conexão com Hugging Face...")
    url = "https://huggingface.co/api/whoami-v2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Hugging Face: Conexão bem-sucedida! Usuário: {user_info.get('name')}")
            return True
        else:
            print(f"❌ Hugging Face: Erro {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Hugging Face: Exceção - {str(e)}")
        return False

if __name__ == "__main__":
    zenodo_ok = test_zenodo()
    hf_ok = test_hf()
    
    if zenodo_ok and hf_ok:
        print("\n🚀 Todos os sistemas prontos para o Observatório!")
    else:
        print("\n⚠️ Verifique as falhas acima antes de prosseguir.")
