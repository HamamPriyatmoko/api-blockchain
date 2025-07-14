# Fungsi untuk hash data sertifikat
import hashlib
import json
import re
import os
from cachetools import cached, TTLCache
import requests

cache = TTLCache(maxsize=1024, ttl=3600)


IPFS_GATEWAY = os.getenv('IPFS_GATEWAY')

def hash_cert_data(cert_data):
    
    cert_json = json.dumps(cert_data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(cert_json.encode('utf-8')).hexdigest()

def format_sertifikat_data(cert_tuple):
    """Mengubah tuple hasil panggilan kontrak menjadi dictionary JSON yang rapi."""
    
    return {
        "id": cert_tuple[0].hex(),
        "nim": cert_tuple[1],
        "universitas": cert_tuple[2],
        "cidDetail": cert_tuple[3],
        "hashMetadata": cert_tuple[4],
        "nomerSertifikat": cert_tuple[5],
        "blockNumber": cert_tuple[6],
        "timestamp": cert_tuple[7],
    }


def parse_certificate_text(text):
    data = {
        "nim": None,
        "universitas": None,
        "nomerSertifikat": None,
    }

    first_line = text.split('\n')[0].strip()
    if first_line:
        data["universitas"] = first_line.title()

    nim_match = re.search(r'Nomor Induk Mahasiswa\s*[:\-]\s*(\d+)', text)
    if nim_match:
        data["nim"] = nim_match.group(1)

    cert_match = re.search(r'Nomor Sertifikat\s*[:\-]\s*([^\n]+)', text, re.IGNORECASE)
    if cert_match:
        data["nomerSertifikat"] = cert_match.group(1).strip()

    return data


@cached(cache)
def fetch_ipfs_data(cid,nim):
    """
    Mencoba mengambil data HANYA dari gateway publik Pinata.
    Mengembalikan data JSON sebagai dict jika berhasil, atau None jika gagal.
    """
    print(f"INFO: {cid} not in cache or expired. Fetching from Pinata Gateway...")
    
    url = f"{IPFS_GATEWAY.rstrip('/')}/{cid}/sertifikat-{nim}/metadata.json"

    
    try:
    
        print(f"Trying gateway: {url}")
        response = requests.get(url, timeout=10) 
        response.raise_for_status()
        
        print(f"SUCCESS: Fetched {cid} from {IPFS_GATEWAY}")
        return response.json()
    except requests.exceptions.RequestException as e:
    
        print(f"ERROR: Pinata gateway failed for CID {cid}: {e}")
        return None