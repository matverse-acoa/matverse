import os
import requests

ACCESS_TOKEN = os.environ.get('ZENODO_ACESS_TOKEN')
BASE_URL = 'https://zenodo.org/api/deposit/depositions'

def create_deposition():
    metadata = {
        'metadata': {
            'title': 'symbiOS v1.2: Cognitive Phase & Genesis Foundation',
            'upload_type': 'software',
            'description': 'Integration of Cognitive Memory (LTM/STM/Buffer) and Utility-based Decision Scoring.',
            'creators': [{'name': 'Mateus Areas'}]
        }
    }
    r = requests.post(BASE_URL, params={'access_token': ACCESS_TOKEN}, json=metadata)
    if r.status_code != 201:
        print(f"Error creating deposition: {r.text}")
        return None
    return r.json()

def upload_file(deposition_id, bucket_url, file_path):
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        r = requests.put(f"{bucket_url}/{file_name}", data=f, params={'access_token': ACCESS_TOKEN})
    if r.status_code != 201:
        print(f"Error uploading file {file_name}: {r.text}")
        return False
    print(f"Successfully uploaded {file_name}")
    return True

def publish_deposition(deposition_id):
    r = requests.post(f"{BASE_URL}/{deposition_id}/actions/publish", params={'access_token': ACCESS_TOKEN})
    if r.status_code != 202:
        print(f"Error publishing deposition: {r.text}")
        return None
    return r.json()

if __name__ == "__main__":
    if not ACCESS_TOKEN:
        print("Zenodo API token not found.")
    else:
        deposition = create_deposition()
        if deposition:
            dep_id = deposition['id']
            bucket_url = deposition['links']['bucket']
            upload_file(dep_id, bucket_url, '/home/ubuntu/symbios_project/symbios-core-v1.2.pdf')
            upload_file(dep_id, bucket_url, '/home/ubuntu/symbios_project/symbios-core-v1.2.tar.gz')
            published = publish_deposition(dep_id)
            if published:
                print(f"Published successfully. DOI: {published['doi']}")
                with open('/home/ubuntu/symbios_project/zenodo_doi_v1.2.txt', 'w') as f:
                    f.write(published['doi'])
