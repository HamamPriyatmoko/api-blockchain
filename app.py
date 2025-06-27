from flask import Flask, request, jsonify
import json
from web3 import Web3
import requests
from utils.utils import hash_cert_data, format_sertifikat_data, parse_certificate_text
from utils.contract_data import contract_abi # Assuming contract_address is now in .env
from flask_cors import CORS
from ipfs_client.ipfs_client import upload_directory_to_pinata
import fitz
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration from Environment Variables ---
GANACHE_URL = os.getenv('GANACHE_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
IPFS_GATEWAY = os.getenv('IPFS_GATEWAY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

# --- Validation for Environment Variables ---
if not all([GANACHE_URL, PRIVATE_KEY, IPFS_GATEWAY, CONTRACT_ADDRESS]):
    raise ValueError("One or more environment variables are missing. Please check your .env file.")

# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Web3 for connection
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Verify Web3 connection
if w3.is_connected():
    print("Connected to Ethereum Network")
else:
    print("Connection failed")
    exit() # Exit if connection fails

# --- Global Variables ---
ADMIN_ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)
# Use the contract address from the .env file
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


@app.route('/api/sertifikat', methods=['POST'])
def terbitkan_sertifikat():
    try:
        # 1. Ambil data dari form-data
        data = request.form
        files = request.files

        # Validasi input
        required_data = ['nim', 'universitas', 'nomerSertifikat', 'nama', 'jurusan', 'fakultas', 'tahunLulus']
        required_files = ['file_ijazah', 'file_skpi']

        if not all(field in data for field in required_data):
            return jsonify({"error": "Data form tidak lengkap"}), 400
        if not all(key in files for key in required_files):
            return jsonify({"error": "File ijazah dan skpi wajib diunggah"}), 400

        # 2. Siapkan file metadata.json
        metadata_json = {
            "nama": data['nama'],
            "jurusan": data['jurusan'],
            "fakultas": data['fakultas'],
            "tahunLulus": data['tahunLulus'],
            # Path ini bersifat relatif terhadap direktori utama di IPFS
            "pathIjazah": f"./file_ijazah_" + data["nim"] + ".pdf",
            "pathSkpi": f"./file_skpi_" + data["nim"] + ".pdf"
        }
        json_stream = BytesIO(json.dumps(metadata_json, indent=4).encode('utf-8'))

        # 3. Siapkan semua file untuk diunggah sebagai satu direktori
        # Nama folder di IPFS akan dibuat unik berdasarkan NIM
        root_folder_name = f"sertifikat-{data['nim']}"
        
        files_for_upload = [
            ("file_ijazah_" + data["nim"] + ".pdf", files['file_ijazah'].stream),
            ("file_skpi_" + data["nim"] + ".pdf", files['file_skpi'].stream),
            ('metadata.json', json_stream)
        ]
        
        # 4. Unggah seluruh direktori ke IPFS dalam satu panggilan
        cid_detail = upload_directory_to_pinata(files_for_upload, root_folder_name)
        print(f"Direktori berhasil diunggah ke IPFS. CID: {cid_detail}")

        # 5. Buat hashMetadata dari data inti on-chain
        metadata_to_hash = {
            "nim": data['nim'],
            "universitas": data['universitas'],
            "nomerSertifikat": data['nomerSertifikat']
        }
        hash_metadata = hash_cert_data(metadata_to_hash)

        # 6. Siapkan input untuk smart contract
        sertifikat_input_struct = [
            data['nim'],
            data['universitas'],
            cid_detail, # Ini adalah CID dari seluruh direktori
            hash_metadata,
            data['nomerSertifikat']
        ]

        # 7. Bangun, Tandatangani, dan Kirim Transaksi
        nonce = w3.eth.get_transaction_count(ADMIN_ACCOUNT.address)
        tx_build = contract.functions.terbitkanSertifikat(sertifikat_input_struct).build_transaction({
            'from': ADMIN_ACCOUNT.address,
            'nonce': nonce,
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('2', 'gwei'),
            'gas': 1000000,
            'chainId': w3.eth.chain_id
        })

        signed_tx = w3.eth.account.sign_transaction(tx_build, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"Transaksi dikirim, hash: {tx_hash.hex()}")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 0:
             return jsonify({"error": "Transaksi ke blockchain gagal."}), 500

        print("Transaksi berhasil dikonfirmasi.")

        return jsonify({
            "message": "Sertifikat berhasil diterbitkan dan diunggah!",
            "status": "Success",
            "transactionHash": tx_receipt.transactionHash.hex(),
            "blockNumber": tx_receipt.blockNumber,
            "gasUsed": tx_receipt.gasUsed,
            "cidDirektori": cid_detail, 
            "hashMetadata": hash_metadata,
            "ipfsGatewayUrl": f"{IPFS_GATEWAY}{cid_detail}/"
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Terjadi kesalahan fatal: {str(e)}"}), 500

# Endpoint untuk melihat semua transaksi yang disimpan di Blockchain
@lru_cache(maxsize=512)
def format_tuple_cached(raw_tuple):
    return format_sertifikat_data(raw_tuple)

@app.route('/api/sertifikat', methods=['GET'])
def get_all_sertifikat():
    try:
        all_ids = contract.functions.getAllId().call()
        sertifikat_list = []

        for cert_id in all_ids:
            try:
                raw = contract.functions.daftarSertifikat(cert_id).call()
                fmt = format_sertifikat_data(tuple(raw))
                sertifikat_list.append({
                    "id":         fmt["id"],
                    "nim":        fmt["nim"],
                    "universitas": fmt["universitas"] or 'N/A',
                })
            except Exception as loop_err:
                app.logger.warning(f"[{cert_id.hex()}] gagal diproses: {loop_err}")
                continue

        return jsonify({"sertifikat": sertifikat_list}), 200

    except Exception as e:
        app.logger.error("Fatal di get_all_sertifikat", exc_info=e)
        return jsonify({"error": f"Kesalahan server: {str(e)}"}), 500

# Mencari detail sertifikat menggunakan id
@app.route('/api/sertifikat/nim/<string:nim>', methods=['GET'])
def get_data_sertifikat(nim):
    try:
        # 2. Panggil smart contract untuk data lengkap on-chain
        id_hex = w3.to_hex(contract.functions.idByNIM(nim).call())

        if not id_hex.startswith('0x'):
            id_hex = '0x' + id_hex
        id_bytes32 = w3.to_bytes(hexstr=id_hex)

        on_chain_data_raw = contract.functions.getSertifikatById(id_bytes32).call()

        # Cek jika data tidak ditemukan
        if on_chain_data_raw[0] == b'\x00' * 32:
            return jsonify({"error": "Sertifikat dengan ID tersebut tidak ditemukan."}), 404

        # 3. Format data on-chain menjadi dictionary
        
        on_chain_data = format_sertifikat_data(on_chain_data_raw)
        # 4. Ambil data off-chain dari IPFS
        cid_detail = on_chain_data['cidDetail']
        off_chain_data = None
        if cid_detail:
            metadata_url = f"{IPFS_GATEWAY}{cid_detail}/metadata.json"
            try:
                response = requests.get(metadata_url, timeout=10)
                response.raise_for_status()
                off_chain_data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Gagal mengambil data dari IPFS untuk ID {id_hex}: {e}")
                pass # Tetap lanjutkan walau IPFS gagal, data on-chain tetap penting

        # 5. Gabungkan dan kembalikan semua data
        return jsonify({
            "status": "success",
            "sertifikat": on_chain_data,
            "dataOffChain": off_chain_data,
            "ipfsGatewayUrl": f"{IPFS_GATEWAY}{cid_detail}/" if cid_detail else None
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Terjadi kesalahan fatal: {str(e)}"}), 500

# Ganti fungsi verifikasi_sertifikat Anda yang lama dengan ini.
@app.route('/api/admin/verifikasi', methods=['POST'])
def verifikasi_sertifikat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body harus berisi JSON"}), 400

        core_fields = ['nim', 'universitas', 'nomerSertifikat']
        if not all(f in data for f in core_fields):
            return jsonify({"status": "invalid",
                            "message": "Data untuk verifikasi tidak lengkap.",
                            "note": f"Field wajib: {core_fields}" }), 400

        # 1. Hitung ulang hash
        recalculated_hash = hash_cert_data(data)

        # 2. Ambil tuple on-chain
        cert_tuple = contract.functions.getSertifikatByHash(recalculated_hash).call()
        # cek existence
        if cert_tuple[0] == b'\x00' * 32:
            return jsonify({
                "status": "invalid",
                "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
                "note": "Data yang dimasukkan mungkin tidak cocok."
            }), 404

        # 3. Format on-chain
        onchain = format_sertifikat_data(cert_tuple)
        # 4. Ambil info blok
        blk = w3.eth.get_block(onchain.pop("blockNumber"))
        info_blok = {
            "nomorBlok": blk.number,
            "hashBlok": blk.hash.hex(),
            "parentHash": blk.parentHash.hex(),
            "timestamp": blk.timestamp,
            "transactions_count": len(blk.transactions),
        }

        # 5. Ambil metadata off-chain
        offchain = {}
        cid = onchain.get("cidDetail")
        if cid:
            try:
                resp = requests.get(f"{IPFS_GATEWAY}{cid}/metadata.json", timeout=10)
                resp.raise_for_status()
                offchain = resp.json()
            except Exception:
                pass

        # 6. Gabungkan on-chain + off-chain
        combined = { **onchain, **offchain }

        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat ditemukan dan terverifikasi.",
            "data": combined,
            "info_blok": info_blok
        }), 200

    except Exception as e:
        app.logger.error(f"Error admin verifikasi: {e}", exc_info=True)
        return jsonify({
            "status": "invalid",
            "message": "❗ Terjadi kesalahan saat verifikasi admin."
        }), 500
    

@app.route('/api/verifikasi', methods=['POST'])
def verifikasi_sertifikat_public():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "invalid", "message": "Request body harus berisi JSON"}), 400

        core_fields = ['nim', 'universitas', 'nomerSertifikat']
        if not all(f in data for f in core_fields):
            return jsonify({"status": "invalid",
                            "message": "Data sertifikat tidak lengkap."}), 400

        # 1. Hitung ulang hash
        h = hash_cert_data(data)

        # 2. Panggil contract
        cert_tuple = contract.functions.getSertifikatByHash(h).call()
        if cert_tuple[0] == b'\x00' * 32:
            return jsonify({
                "status": "invalid",
                "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
                "note": "Data yang dimasukkan mungkin tidak cocok."
            }), 404

        # 3. Format on-chain & ambil block info
        onchain = format_sertifikat_data(cert_tuple)
        blk = w3.eth.get_block(onchain.pop("blockNumber"))
        info_blok = {
            "nomorBlok": blk.number,
            "hashBlok": blk.hash.hex(),
            "parentHash": blk.parentHash.hex(),
            "timestamp": blk.timestamp,
            "transactions_count": len(blk.transactions),
        }

        # 4. Fetch off-chain metadata
        offchain = {}
        cid = onchain.get("cidDetail")
        if cid:
            try:
                resp = requests.get(f"{IPFS_GATEWAY}{cid}/metadata.json", timeout=10)
                resp.raise_for_status()
                offchain = resp.json()
            except Exception:
                pass

        # 5. Gabungkan
        combined = { **onchain, **offchain }

        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat ditemukan dan terverifikasi.",
            "data": combined,
            "info_blok": info_blok
        }), 200

    except Exception as e:
        app.logger.error(f"Error publik verifikasi: {e}", exc_info=True)
        return jsonify({
            "status": "invalid",
            "message": "❗ Terjadi kesalahan saat verifikasi."
        }), 500


@app.route('/api/verifikasi/hash', methods=['POST'])
def verify_by_hash():
    try:
        # 1. Ambil data_hash dari request JSON
        payload = request.get_json()
        if not payload or 'data_hash' not in payload:
            return jsonify({"error": "Data Hash Tidak Ada"}), 400
        data_hash = payload['data_hash']

        # 2. Panggil smart contract → tuple on-chain
        cert_tuple = contract.functions.getSertifikatByHash(data_hash).call()

        # 3. Cek eksistensi
        if cert_tuple[0] == b'\x00' * 32:
            return jsonify({
                "status": "invalid",
                "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
                "note": "Data yang dimasukkan mungkin tidak cocok dengan data yang terdaftar di blockchain."
            }), 404

        # 4. Format tuple on-chain jadi dict
        data_onchain = format_sertifikat_data(cert_tuple)

        # 5. Ambil info blok
        block_number = data_onchain.get("blockNumber")
        blk = w3.eth.get_block(block_number)
        info_blok = {
            "nomorBlok": blk.number,
            "hashBlok": blk.hash.hex(),
            "parentHash": blk.parentHash.hex(),
            "timestamp": blk.timestamp,
            "transactions_count": len(blk.transactions),
        }

        # 6. Fetch metadata.json dari IPFS (off-chain)
        offchain = {}
        cid = data_onchain.get("cidDetail")
        if cid:
            try:
                url = f"{IPFS_GATEWAY}{cid}/metadata.json"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                offchain = resp.json()
            except Exception as e:
                app.logger.warning(f"Gagal fetch IPFS metadata ({cid}): {e}")

        # 7. Buang blockNumber agar tidak duplikat
        data_onchain.pop("blockNumber", None)

        # 8. Merge on-chain + off-chain saja
        combined_data = {
            **data_onchain,
            **offchain
        }

        print(combined_data)

        # 9. Kembalikan response dengan data + info_blok terpisah
        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat Ditemukan dan Terverifikasi di Blockchain",
            "data": combined_data,
            "info_blok": info_blok
        }), 200

    except Exception as e:
        app.logger.error(f"Error saat verifikasi by hash: {e}", exc_info=True)
        return jsonify({
            "status": "invalid",
            "message": "❗ Terjadi kesalahan saat verifikasi.",
        }), 500


@app.route('/api/extract-pdf', methods=['POST'])
def extract_text_from_pdf():
    if 'pdfFile' not in request.files:
        return jsonify({"error": "Tidak ada file PDF yang dikirim"}), 400
    
    file = request.files['pdfFile']
    
    if file.filename == '':
        return jsonify({"error": "File tidak dipilih"}), 400

    try:
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        full_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            full_text += page.get_text()
        pdf_document.close()
        
        # Sekarang: Panggil fungsi parsing dan kembalikan hasilnya
        structured_data = parse_certificate_text(full_text)
        
        return jsonify(structured_data)

    except Exception as e:
        return jsonify({"error": f"Gagal memproses file PDF: {str(e)}"}), 500


if __name__ == '__main__':
    # The debug flag will be set based on an environment variable, e.g., FLASK_DEBUG
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't'])
