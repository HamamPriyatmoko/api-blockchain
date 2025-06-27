# Fungsi untuk hash data sertifikat
import hashlib
import json
import re
import os

IPFS_GATEWAY = os.getenv('IPFS_GATEWAY')

def hash_cert_data(cert_data):
    
    cert_json = json.dumps(cert_data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(cert_json.encode('utf-8')).hexdigest()

def format_sertifikat_data(cert_tuple):
    """Mengubah tuple hasil panggilan kontrak menjadi dictionary JSON yang rapi."""
    # Urutan ini HARUS SAMA PERSIS dengan urutan field di struct Sertifikat Anda
    return {
        "id": cert_tuple[0].hex(),
        "nim": cert_tuple[1],
        "universitas": cert_tuple[2],
        "cidDetail": cert_tuple[3],
        "hashMetadata": cert_tuple[4],
        "nomerSertifikat": cert_tuple[5],
        "blockNumber": cert_tuple[6],
    }


def parse_certificate_text(text):
    data = {
        "nim": None,
        "universitas": None,
        "nomerSertifikat": None,
    }

    # ambil universitas dari baris pertama
    first_line = text.split('\n')[0].strip()
    if first_line:
        data["universitas"] = first_line.title()

    # ambil NIM
    nim_match = re.search(r'Nomor Induk Mahasiswa\s*[:\-]\s*(\d+)', text)
    if nim_match:
        data["nim"] = nim_match.group(1)

    # ambil nomer sertifikat
    cert_match = re.search(r'Nomor Sertifikat\s*[:\-]\s*([^\n]+)', text, re.IGNORECASE)
    if cert_match:
        data["nomerSertifikat"] = cert_match.group(1).strip()

    return data
