import requests
import json
import os

PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY')

def upload_directory_to_pinata(files_data, root_folder_name):
    """
    Mengunggah beberapa file sebagai satu direktori ke Pinata.
    - files_data: list dari tuple (nama_file_di_folder, stream_file)
    - root_folder_name: nama folder utama di IPFS.
    Mengembalikan CID dari direktori tersebut.
    """
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    # Siapkan file untuk permintaan multipart/form-data
    multipart_files = []
    for filename, stream in files_data:
        # Path file di dalam direktori IPFS
        filepath_in_ipfs = f"{root_folder_name}/{filename}"
        multipart_files.append(('file', (filepath_in_ipfs, stream.read())))

    try:
        response = requests.post(url, files=multipart_files, headers=headers)
        response.raise_for_status()
        return response.json()['IpfsHash']
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengunggah direktori ke Pinata: {e}")
        print(f"Response body: {e.response.text if e.response else 'No response'}")
        raise
