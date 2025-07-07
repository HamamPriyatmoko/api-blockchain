import requests
import json
import os
from dotenv import load_dotenv

# Memuat environment variables dari file .env
load_dotenv()

PINATA_JWT = os.getenv('PINATA_JWT')
# PINNING_PINATA = os.getenv('PINNING_PINATA')

if not PINATA_JWT:
    raise ValueError("Variabel lingkungan PINATA_JWT tidak ditemukan. Harap periksa file .env Anda.")

def upload_directory_to_pinata(files_data, directory_name="my-dir"):
    """
    PERINGATAN: Versi ini akan membuat struktur direktori bersarang
    (contoh: /ipfs/CID/sertifikat-nim/namafile.pdf)
    """
    url = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    data = {
        "pinataOptions": json.dumps({
            "cidVersion": 1,
            "wrapWithDirectory": True 
        }),
        "pinataMetadata": json.dumps({
            "name": directory_name 
        })
    }

    files = []
    for fname, stream in files_data:
    
        full_path = f"{directory_name}/{fname}" 
        
        files.append(
            ("file", (full_path, stream.read(), "application/octet-stream"))
        )

    try:
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=60) 
        resp.raise_for_status()
        return resp.json()["IpfsHash"]

    except requests.exceptions.HTTPError as err:
        error_message = f"Error dari Pinata API: {err.response.status_code} - {err.response.text}"
        print(f"[Pinata] HTTP Error: {error_message}")
        raise Exception(error_message) from err
    except Exception as e:
        print(f"[Pinata] Terjadi error tak terduga: {e}")
        raise e