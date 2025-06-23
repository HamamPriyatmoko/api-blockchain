# Fungsi untuk hash data sertifikat
import hashlib
import json
import re

def hash_cert_data(cert_data):
    
    cert_json = json.dumps(cert_data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(cert_json.encode()).hexdigest()

def format_sertifikat_data(cert_tuple):
    """Mengubah tuple hasil panggilan kontrak menjadi dictionary JSON yang rapi."""
    # Urutan ini HARUS SAMA PERSIS dengan urutan field di struct Sertifikat Anda
    return {
        "id": cert_tuple[0].hex(),
        "nim": cert_tuple[1],
        "nama": cert_tuple[2],
        "universitas": cert_tuple[3],
        "jurusan": cert_tuple[4],
        "tanggalTerbit": cert_tuple[5],
        "hashMetadata": cert_tuple[6],
        "cidSuratBebasPerpustakaan": cert_tuple[7],
        "cidSuratBebasLaboratorium": cert_tuple[8],
        "cidSuratBebasKeuangan": cert_tuple[9],
        "cidBuktiPenyerahanSkripsi": cert_tuple[10],
        "cidSertifikatToefl": cert_tuple[11],
        "blockNumber": cert_tuple[12],
        "valid": cert_tuple[13]
    }

def parse_certificate_text(text):
    """
    Fungsi ini menerima string teks mentah dari sertifikat dan 
    mengembalikannya sebagai dictionary Python yang terstruktur.
    """
    data = {
        "universitas": None,
        "nama": None,
        "nim": None,
        "jurusan": None,
        "tanggalTerbit": None,
    }

    # 1. Ekstrak Universitas dan ubah ke Title Case
    if text.split('\n')[0]:
        data["universitas"] = text.split('\n')[0].strip().title()

    # 2. Ekstrak Nama dan ubah ke Title Case
    nama_match = re.search(r'[a-f0-9]{64}\n(.*?)\ntelah memenuhi', text, re.DOTALL)
    if nama_match:
        data["nama"] = nama_match.group(1).strip().title()

    # 3. Ekstrak NIM (tidak ada perubahan)
    nim_match = re.search(r'Nomor Induk Mahasiswa\s*:\s*\n(\d+)', text)
    if nim_match:
        data["nim"] = nim_match.group(1).strip()

    # 4. Ekstrak Jurusan (tidak ada perubahan)
    jurusan_match = re.search(r'Program Studi\s*:\s*\n(.*?)\n', text)
    if jurusan_match:
        data["jurusan"] = jurusan_match.group(1).strip()

    # 5. Ekstrak Tanggal Lulus (tidak ada perubahan)
    tanggal_match = re.search(r'Tanggal Lulus\s*:\s*\n([\d-]+)', text)
    if tanggal_match:
        data["tanggalTerbit"] = tanggal_match.group(1).strip()
        
    return data
