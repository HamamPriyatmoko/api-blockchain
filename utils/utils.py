# Fungsi untuk hash data sertifikat
import hashlib
import json

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