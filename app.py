from flask import Flask, request, jsonify
from web3 import Web3
from utils.utils import hash_cert_data
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

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
@app.route('/terbitkan_sertifikat_blockchain', methods=['POST'])
def terbitkan_sertifikat_blockchain():
    try:
        # 1. Ambil metadata dari form-data
        data = request.form.to_dict()
        required_fields = [
            'nama', 'universitas', 'jurusan',
            'sertifikatToefl', 'sertifikatBTA',
            'sertifikatSKP', 'tanggal'
        ]
        if not all(f in data and data[f] for f in required_fields):
            return jsonify({"error": "Missing required certificate fields"}), 400

        # 2. Ambil dan upload tiga file PDF
        pdf_toefl = request.files.get('pdf_toefl')
        pdf_bta   = request.files.get('pdf_bta')
        pdf_skp   = request.files.get('pdf_skp')
        if not (pdf_toefl and pdf_bta and pdf_skp):
            return jsonify({
                "error": "All three PDF files are required: pdf_toefl, pdf_bta, pdf_skp"
            }), 400

        cid_toefl = upload_file_to_pinata(pdf_toefl.stream, pdf_toefl.filename)
        cid_bta   = upload_file_to_pinata(pdf_bta.stream,   pdf_bta.filename)
        cid_skp   = upload_file_to_pinata(pdf_skp.stream,   pdf_skp.filename)

        # 3. Buat manifest JSON dan upload ke Pinata → satu CID manifest
        manifest = {
            "pdfToefl": cid_toefl,
            "pdfBta":   cid_bta,
            "pdfSkp":   cid_skp
        }
        manifest_cid = upload_json_to_pinata(manifest)
        url_cid = f"https://ipfs.io/ipfs/{manifest_cid}"

        # 4. Hash metadata (tanpa file)
        cert_meta = { k: data[k] for k in required_fields }
        cert_hash = hash_cert_data(cert_meta)

        # 5. Build & kirim transaksi on-chain
        acct  = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.terbitkanSertifikat(
            data['nama'],
            data['universitas'],
            data['jurusan'],
            data['sertifikatToefl'],
            data['sertifikatBTA'],
            data['sertifikatSKP'],
            data['tanggal'],
            cert_hash,
            url_cid
        ).build_transaction({
            'nonce': nonce,
            'maxFeePerGas': 3_000_000_000,
            'maxPriorityFeePerGas': 2_000_000_000,
            'gas': 1_000_000,
            'value': 0,
            'type': 2,
            'chainId': 1337
        })

        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        return jsonify({
            "transaction_hash": tx_hash.hex(),
            "file_cids": {
                "toefl": cid_toefl,
                "bta":   cid_bta,
                "skp":   cid_skp
            },
            "manifest_cid": manifest_cid,
            "url_cid": url_cid,
            "data_hash": cert_hash,
            "sertifikat_meta": cert_meta
        }), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/verifikasi_sertifikat', methods=['POST'])
def verifikasi_sertifikat():
    try:
        data = request.get_json()
        required_fields = ['id', 'nama', 'universitas', 'jurusan',
                           'sertifikatToefl', 'sertifikatBTA', 'sertifikatSKP', 'tanggal']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Data sertifikat tidak lengkap"}), 400

        structured_data = {
            "nama": data["nama"],
            "universitas": data["universitas"],
            "jurusan": data["jurusan"],
            "sertifikatToefl": data["sertifikatToefl"],
            "sertifikatBTA": data["sertifikatBTA"],
            "sertifikatSKP": data["sertifikatSKP"],
            "tanggal": data["tanggal"],
        }

        cert_hash = hash_cert_data(structured_data)
        blockchain_hash = contract.functions.getHashById(data['id']).call()

        if cert_hash != blockchain_hash:
            return jsonify({
                "status": "invalid",
                "message": "❗ Maaf, sertifikat tidak ditemukan di dalam sistem.",
                "note": "Kemungkinan palsu atau tidak diterbitkan melalui sistem ini"
            }), 404

        # Ambil data sertifikat lengkap termasuk blockNumber dari smart contract
        cert_data = contract.functions.getSertifikat(data['id']).call()
        # Struktur pengembalian: (nama, universitas, jurusan, toefl, bta, skp, tanggal, urlCid, blockNumber, valid)

        block_number = cert_data[8]  # blockNumber pada posisi ke-9 (index 8)

        # Ambil blok berdasarkan blockNumber
        block = w3.eth.get_block(block_number)
        block_info = {
            'number': block.number,
            'hash': block.hash.hex(),
            'parentHash': block.parentHash.hex(),
            'timestamp': block.timestamp,
            'transactions_count': len(block.transactions)
        }

        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat Terdaftar di Blockchain",
            "hash_data": structured_data,
            "hashBlockchain": blockchain_hash,
            "blockchain_block": block_info
        }), 200

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

# Endpoint untuk melihat semua transaksi yang disimpan di Blockchain
@app.route('/sertifikat', methods=['GET'])
def get_all_sertifikat():
    try:
        all_ids = contract.functions.getAllIds().call()

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

@app.route('/ipfs/data/<cid>', methods=['GET'])
def get_ipfs_data(cid):
    try:
        data = get_json_from_ipfs(cid)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
