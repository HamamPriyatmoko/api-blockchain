# Fungsi untuk hash data sertifikat
import hashlib
import json

def hash_cert_data(cert_data):
    
    cert_json = json.dumps(cert_data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(cert_json.encode()).hexdigest()