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

@app.route('/sertifikat', methods=['POST'])
def prepare_sertifikat():
    try:
        # 1. Ambil metadata dari form-data
        data = request.form.to_dict()
        required_fields = [
            'nama', 'universitas', 'jurusan',
            'sertifikatToefl', 'sertifikatBTA',
            'sertifikatSKP', 'tanggal'
        ]
        if not all(f in data and data[f] for f in required_fields):
            return jsonify({"error": "Data sertifikat yang wajib diisi tidak lengkap"}), 400

        # 2. Ambil dan unggah tiga file PDF ke IPFS
        pdf_toefl = request.files.get('pdf_toefl')
        pdf_bta   = request.files.get('pdf_bta')
        pdf_skp   = request.files.get('pdf_skp')
        if not (pdf_toefl and pdf_bta and pdf_skp):
            return jsonify({
                "error": "Ketiga file PDF wajib diunggah: pdf_toefl, pdf_bta, pdf_skp"
            }), 400

        cid_toefl = upload_file_to_pinata(pdf_toefl.stream, pdf_toefl.filename)
        cid_bta   = upload_file_to_pinata(pdf_bta.stream,   pdf_bta.filename)
        cid_skp   = upload_file_to_pinata(pdf_skp.stream,   pdf_skp.filename)

        # 3. Buat manifest JSON, lalu unggah ke IPFS
        manifest = {
            "pdfToefl": cid_toefl,
            "pdfBta":   cid_bta,
            "pdfSkp":   cid_skp
        }
        url_cid = upload_json_to_pinata(manifest)
        
        cert_meta = { k: data[k] for k in required_fields }
        
        data_to_hash = cert_meta.copy()
        data_to_hash['manifest_cid'] = url_cid
        
        #    Generate hash dari data gabungan (metadata + manifest_cid)
        cert_hash = hash_cert_data(data_to_hash)
        print(url_cid)

        # 5. Kembalikan hash, CID mentah, dan metadata bersih ke frontend.
        return jsonify({
            "message": "Data berhasil dipersiapkan",
            "cert_hash": cert_hash,
            "url_cid": url_cid,
            "sertifikat_meta": cert_meta
        }), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/verifikasi_admin', methods=['POST'])
def verifikasi_sertifikat():
    try:
        data = request.get_json()
        print(data)
        required_fields = ['id', 'nama', 'universitas', 'jurusan',
                           'sertifikatToefl', 'sertifikatBTA', 'sertifikatSKP', 'tanggal', 'urlCid']

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
            "manifest_cid" : data["urlCid"],
        }

        cert_hash = '' + hash_cert_data(structured_data)
        print(type(cert_hash))
        # cert_id_bytes = '0x' + data['id']
        get_id_sertifikkat = contract.functions.verifyHash(cert_hash).call()
        print('dapatkan id', get_id_sertifikkat)

        if not get_id_sertifikkat:
            return jsonify({
                "status": "invalid",
                "message": "❗ Maaf, sertifikat tidak ditemukan di dalam sistem.",
                "note": "Kemungkinan palsu atau tidak diterbitkan melalui sistem ini"
            }), 404

        # Ambil data sertifikat lengkap termasuk blockNumber dari smart contract
        cert_data = contract.functions.getSertifikat(get_id_sertifikkat).call()
        blockchain_hash = contract.functions.getHashById(get_id_sertifikkat).call()
        
        block_number = cert_data[8]

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
    

@app.route('/verifikasi_public', methods=['POST'])
def verifikasi_sertifikat_public():
    try:
        data = request.get_json()
        required_fields = ['id', 'nama', 'universitas', 'jurusan',
                           'sertifikatToefl', 'sertifikatBTA', 'sertifikatSKP', 'tanggal', 'urlCid']

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
            "manifest_cid": data["urlCid"],
        }

        cert_hash = hash_cert_data(structured_data)
        get_id_sertifikat = contract.functions.verifyHash(cert_hash).call()

        if not get_id_sertifikat:
            return jsonify({
                "status": "invalid",
                "message": "❗ Maaf, sertifikat tidak ditemukan di dalam sistem.",
                "note": "Kemungkinan palsu atau tidak diterbitkan melalui sistem ini"
            }), 404

        # Ambil data sertifikat lengkap termasuk blockNumber dari smart contract
        cert_data = contract.functions.getSertifikat(get_id_sertifikat).call()
        
        block_number = cert_data[8]

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
            "blockchain_block": block_info
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify_by_hash', methods=['POST'])
def verify_by_hash():
    try:
        # 1. Ambil data_hash dari request JSON
        data = request.get_json()
        if not data or 'data_hash' not in data:
            return jsonify({"error": "Missing field 'data_hash'"}), 400
        
        data_hash = data['data_hash']

        # 2. Panggil smart contract verifyHash untuk dapatkan cert_id (bytes32)
        cert_id = contract.functions.verifyHash(data_hash).call()

        if not cert_id:
            return jsonify({
                "status": "invalid",
                "message": "❗ Data sertifikat tidak ditemukan."
            }), 404

        cert = contract.functions.getSertifikat(cert_id).call()
        hash_blockchain = contract.functions.getHashById(cert_id).call()

        block_number = cert[8]
        block = w3.eth.get_block(block_number)
        print(block)
        block_info = {
            'number': block.number,
            'hash': block.hash.hex(),
            'parentHash': block.parentHash.hex(),
            'timestamp': block.timestamp,
            'transactions_count': len(block.transactions)
        }

        structured_data = {
            "nama": cert[0],
            "universitas": cert[1],
            "jurusan": cert[2],
            "sertifikatToefl": cert[3],
            "sertifikatBTA": cert[4],
            "sertifikatSKP": cert[5],
            "tanggal": cert[6],
            "urlCid": cert[7],
        }

        # 5. Susun response JSON
        response = {
            "status": "valid",
            "message": "✅ Sertifikat Terdaftar di Blockchain",
            "data": structured_data,
            "hashBlockchain": hash_blockchain,
            "blockchain_block": block_info,
        }
        return jsonify(response), 200

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

@app.route('/ipfs/data/<cid>', methods=['GET'])
def get_ipfs_data(cid):
    try:
        data = get_json_from_ipfs(cid)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
