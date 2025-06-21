from flask import Flask, request, jsonify
from web3 import Web3
from utils.utils import hash_cert_data, format_sertifikat_data
from utils.contract_data import contract_abi, contract_address
from flask_cors import CORS
from ipfs_client.ipfs_client import upload_json_to_pinata, get_json_from_ipfs, upload_file_to_pinata
from config import PRIVATE_KEY


# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Web3 untuk koneksi ke Ganache (Ethereum Local Network)
infura_url = 'http://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Verifikasi koneksi Web3
if w3.is_connected():
    print("Connected to Ethereum Network")
else:
    print("Connection failed")

ADMIN_ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/sertifikat', methods=['POST'])
def terbitkan_sertifikat():
    try:
        # 1. Ambil data teks dari form-data
        data = request.form.to_dict()
        core_data_fields = ['nim', 'nama', 'universitas', 'jurusan', 'tanggalTerbit']
        if not all(field in data for field in core_data_fields):
            return jsonify({"error": "Data inti (NIM, nama, dll.) tidak lengkap"}), 400

        # 2. Ambil semua file PDF yang dibutuhkan
        files = request.files
        required_files = {
            'pdf_perpustakaan': 'cidSuratBebasPerpustakaan',
            'pdf_laboratorium': 'cidSuratBebasLaboratorium',
            'pdf_keuangan': 'cidSuratBebasKeuangan',
            'pdf_skripsi': 'cidBuktiPenyerahanSkripsi',
            'pdf_toefl': 'cidSertifikatToefl'
        }
        if not all(key in files for key in required_files.keys()):
            return jsonify({"error": f"Semua 5 file PDF wajib diunggah: {list(required_files.keys())}"}), 400
        
        # 3. Unggah setiap file ke IPFS menggunakan fungsi Anda dan kumpulkan CID
        cids = {}
        for key, field_name in required_files.items():
            file = files[key]
            cid = upload_file_to_pinata(file.stream, file.filename)
            cids[field_name] = cid

        # 4. Buat hashMetadata dari data inti
        metadata_to_hash = {key: data[key] for key in core_data_fields}
        hash_metadata = hash_cert_data(metadata_to_hash)
        
        # 5. Siapkan input untuk smart contract sesuai struct SertifikatInput
        sertifikat_input_struct = [
            data['nim'], data['nama'], data['universitas'], data['jurusan'],
            data['tanggalTerbit'], hash_metadata, cids['cidSuratBebasPerpustakaan'],
            cids['cidSuratBebasLaboratorium'], cids['cidSuratBebasKeuangan'],
            cids['cidBuktiPenyerahanSkripsi'], cids['cidSertifikatToefl']
        ]

        # 6. Bangun, Tandatangani, dan Kirim Transaksi
        nonce = w3.eth.get_transaction_count(ADMIN_ACCOUNT.address)
        tx_build = contract.functions.terbitkanSertifikat(sertifikat_input_struct).build_transaction({
            'from': ADMIN_ACCOUNT.address,
            'nonce': nonce,
            'maxFeePerGas': 3_000_000_000,
            'maxPriorityFeePerGas': 2_000_000_000,
            'gas': 1_000_000,
            'value': 0,
            'type': 2,
            'chainId': 1337
        })

        signed_tx = w3.eth.account.sign_transaction(tx_build, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"Transaksi dikirim, hash: {tx_hash.hex()}")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaksi berhasil dikonfirmasi.")

        return jsonify({
            "message": "Sertifikat berhasil diterbitkan di blockchain!",
            "status": tx_receipt.status,
            "transactionHash": tx_receipt.transactionHash.hex(),
            "blockNumber": tx_receipt.blockNumber,
            "gasUsed": tx_receipt.gasUsed,
            "cids": cids
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Terjadi kesalahan fatal: {str(e)}"}), 500

# Ganti fungsi verifikasi_sertifikat Anda yang lama dengan ini.

@app.route('/verifikasi_admin', methods=['POST'])
def verifikasi_sertifikat():
    """
    Endpoint verifikasi yang menerima data mentah, membuat hash di backend,
    dan memanggil smart contract untuk verifikasi.
    """
    try:
        # 1. Ambil data JSON dari body request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body harus berisi JSON"}), 400
        print(data)
        # Tentukan field yang dibutuhkan untuk membuat ulang hash
        core_data_fields = ['nim', 'nama', 'universitas', 'jurusan', 'tanggalTerbit']
        if not all(field in data for field in core_data_fields):
            return jsonify({"error": f"Data untuk verifikasi tidak lengkap. Field yang wajib ada: {core_data_fields}"}), 400

        # 2. Buat ulang hash metadata dari data yang diterima
        metadata_to_hash = {key: data[key] for key in core_data_fields}
        hash_bytes = hash_cert_data(metadata_to_hash) # Fungsi ini harus mengembalikan 'bytes'

        # print(f"Mencoba verifikasi dengan hash yang dibuat: {hash_bytes.hex()}")

        # 3. Lakukan SATU PANGGILAN ke smart contract menggunakan hash yang baru dibuat
        cert_data_tuple = contract.functions.getSertifikatByHash(hash_bytes).call()
        print(cert_data_tuple)

        # 4. Ubah hasil (tuple) menjadi dictionary JSON yang rapi
        formatted_data = format_sertifikat_data(cert_data_tuple)
        print(formatted_data)
        
        # 5. Ambil informasi blok dari blockchain
        block_number = formatted_data['blockNumber']
        block = w3.eth.get_block(block_number)

        # 6. Kembalikan response yang sukses dan terstruktur
        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat Ditemukan dan Terverifikasi di Blockchain",
            "data_sertifikat": formatted_data, # Mengembalikan semua data sertifikat yang terverifikasi
            "info_blok": {
                'nomorBlok': block.number,
                'hashBlok': block.hash.hex(),
                'parentHash': block.parentHash.hex(),
                'timestamp': block.timestamp,
                'transactions_count': len(block.transactions)
            }
        }), 200

    except Exception as e:
        # Jika 'require' di smart contract gagal (hash tidak ditemukan), akan masuk ke sini
        print(f"Error saat verifikasi admin: {e}")
        return jsonify({
            "status": "invalid",
            "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
            "note": "Data yang dimasukkan mungkin tidak cocok dengan data yang terdaftar di blockchain."
        }), 404
    

@app.route('/verifikasi_public', methods=['POST'])
def verifikasi_sertifikat_public():
    try:
        data = request.get_json()
        required_fields = ['nim', 'nama', 'universitas', 'jurusan', 'tanggalTerbit']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Data sertifikat tidak lengkap"}), 400

        metadata_to_hash = {key: data[key] for key in required_fields}
        hash_bytes = hash_cert_data(metadata_to_hash)

        cert_data_tuple = contract.functions.getSertifikatByHash(hash_bytes).call()

        # 4. Ubah hasil (tuple) menjadi dictionary JSON yang rapi
        formatted_data = format_sertifikat_data(cert_data_tuple)
        print(formatted_data)
        
        # 5. Ambil informasi blok dari blockchain
        block_number = formatted_data['blockNumber']
        block = w3.eth.get_block(block_number)

        # 6. Kembalikan response yang sukses dan terstruktur
        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat Ditemukan dan Terverifikasi di Blockchain",
            "data_sertifikat": formatted_data, # Mengembalikan semua data sertifikat yang terverifikasi
            "info_blok": {
                'nomorBlok': block.number,
                'hashBlok': block.hash.hex(),
                'parentHash': block.parentHash.hex(),
                'timestamp': block.timestamp,
                'transactions_count': len(block.transactions)
            }
        }), 200

    except Exception as e:
        # Jika 'require' di smart contract gagal (hash tidak ditemukan), akan masuk ke sini
        print(f"Error saat verifikasi admin: {e}")
        return jsonify({
            "status": "invalid",
            "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
            "note": "Data yang dimasukkan mungkin tidak cocok dengan data yang terdaftar di blockchain."
        }), 404

@app.route('/verify_by_hash', methods=['POST'])
def verify_by_hash():
    try:
        # 1. Ambil data_hash dari request JSON
        data = request.get_json()
        if not data or 'data_hash' not in data:
            return jsonify({"error": "Data Hash Tidak Ada"}), 400
        
        data_hash = data['data_hash']

        # 2. Panggil smart contract verifyHash untuk dapatkan cert_id (bytes32)
        cert_data_tuple = contract.functions.getSertifikatByHash(data_hash).call()

        # 4. Ubah hasil (tuple) menjadi dictionary JSON yang rapi
        formatted_data = format_sertifikat_data(cert_data_tuple)
        print(formatted_data)
        
        # 5. Ambil informasi blok dari blockchain
        block_number = formatted_data['blockNumber']
        block = w3.eth.get_block(block_number)

        # 6. Kembalikan response yang sukses dan terstruktur
        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat Ditemukan dan Terverifikasi di Blockchain",
            "data_sertifikat": formatted_data, # Mengembalikan semua data sertifikat yang terverifikasi
            "info_blok": {
                'nomorBlok': block.number,
                'hashBlok': block.hash.hex(),
                'parentHash': block.parentHash.hex(),
                'timestamp': block.timestamp,
                'transactions_count': len(block.transactions)
            }
        }), 200

    except Exception as e:
        # Jika 'require' di smart contract gagal (hash tidak ditemukan), akan masuk ke sini
        print(f"Error saat verifikasi admin: {e}")
        return jsonify({
            "status": "invalid",
            "message": "❗ Sertifikat tidak ditemukan di dalam sistem.",
            "note": "Data yang dimasukkan mungkin tidak cocok dengan data yang terdaftar di blockchain."
        }), 404

# Endpoint untuk melihat semua transaksi yang disimpan di Blockchain
@app.route('/sertifikat', methods=['GET'])
def get_all_sertifikat():
    try:
        all_ids = contract.functions.getSertifikatCount().call()
        print(all_ids)

        sertifikat_list = []
        for id in all_ids:
            data = contract.functions.getSertifikat(id).call()
            sertifikat_list.append({
                "id": id.hex(),
                "nama": data[0],
                "universitas": data[1],
                "jurusan": data[2]
            })
        return jsonify({"sertifikat": sertifikat_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_data_sertifikat/<string:id_hex>', methods=['GET'])
def get_data_sertifikat(id_hex):
    try:
        # Pastikan id dalam format hex string dengan prefix 0x
        print(id_hex)
        if not id_hex.startswith('0x'):
            id_hex = '0x' + id_hex
        id_bytes32 = Web3.to_bytes(hexstr=id_hex)

        # Panggil smart contract untuk data lengkap sertifikat
        cert = contract.functions.getSertifikat(id_bytes32).call()

        data = {
            "id": id_hex,
            "nama": cert[0],
            "universitas": cert[1],
            "jurusan": cert[2],
            "sertifikatToefl": cert[3],
            "sertifikatBTA": cert[4],
            "sertifikatSKP": cert[5],
            "tanggal": cert[6],
            "urlCid": cert[7],
            "blockNumber": cert[8],
            "valid": cert[9]
        }

        return jsonify({
            "status": "success",
            "sertifikat": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ipfs/data/<cid>', methods=['GET'])
def get_ipfs_data(cid):
    try:
        data = get_json_from_ipfs(cid)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
