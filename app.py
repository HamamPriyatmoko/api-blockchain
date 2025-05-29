from flask import Flask, request, jsonify
from web3 import Web3
import qrcode
import base64
from io import BytesIO
import json
from utils.utils import hash_cert_data
from sqlalchemy.orm.exc import NoResultFound
from utils.contract_data import contract_abi, contract_address
from service.sertifikat_service import SertifikatService
from service.transaction_service import TransactionService
from flask_cors import CORS


# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Service
service = SertifikatService()
transaction_service = TransactionService()

# Setup Web3 untuk koneksi ke Ganache (Ethereum Local Network)
infura_url = 'http://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Verifikasi koneksi Web3
if w3.is_connected():
    print("Connected to Ethereum Network")
else:
    print("Connection failed")

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def get_sertifikat_from_blockchain(id_blockchain):
    cert = contract.functions.daftarSertifikat(id_blockchain).call()
    return {
        "id": cert[0],
        "penerima": cert[1],
        "nama": cert[2],
        "universitas": cert[3],
        "jurusan": cert[4],
        "sertifikatToefl": cert[5],
        "sertifikatBTA": cert[6],
        "sertifikatSKP": cert[7],
        "tanggal": cert[8],
        "valid": cert[9],
    }

@app.route('/simpan_sertifikat', methods=['POST'])
def simpan_sertifikat():
    try:
        data = request.get_json()

        # Validasi wajib ada semua field sesuai struktur lengkap
        required_fields = ['penerima', 'nama', 'universitas', 'jurusan',
                           'sertifikatToefl', 'sertifikatBTA', 'sertifikatSKP', 'tanggal']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Gunakan service untuk create sertifikat
        sertifikat = service.create_sertifikat(data)

        return jsonify({
            "message": "Data sertifikat berhasil disimpan di database",
            "id": str(sertifikat.id),
            "status_publish": sertifikat.status_publish
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/terbitkan_sertifikat_blockchain', methods=['POST'])
def terbitkan_sertifikat_blockchain():
    try:
        data = request.get_json()
        sertifikat_id = data.get('sertifikat_id')
        if not sertifikat_id:
            return jsonify({"error": "Missing sertifikat_id"}), 400

        # Gunakan service untuk ambil data sertifikat
        try:
            sertifikat = service.get_sertifikat_by_id(sertifikat_id)
        except NoResultFound:
            return jsonify({"error": "Sertifikat tidak ditemukan di database"}), 404

        # Ambil data lengkap sesuai struktur service/model
        penerima = sertifikat.penerima
        nama = sertifikat.nama
        universitas = sertifikat.universitas
        jurusan = sertifikat.jurusan
        sertifikatToefl = sertifikat.sertifikatToefl
        sertifikatBTA = sertifikat.sertifikatBTA
        sertifikatSKP = sertifikat.sertifikatSKP
        tanggal = sertifikat.tanggal
        tanggal_str = tanggal.isoformat() if hasattr(tanggal, 'isoformat') else str(tanggal)

        # Siapkan data sertifikat untuk hashing
        cert_data = {
            "penerima": penerima,
            "nama": nama,
            "universitas": universitas,
            "jurusan": jurusan,
            "sertifikatToefl": sertifikatToefl,
            "sertifikatBTA": sertifikatBTA,
            "sertifikatSKP": sertifikatSKP,
            "tanggal": tanggal_str
        }

        # Hash data sertifikat
        cert_hash = hash_cert_data(cert_data)

        private_key = '0x6ddbba11daa3db69e2b60eb888d6e51428b19c8b42b387c8cd5982a438e6c321'
        account = w3.eth.account.from_key(private_key)
        address = account.address
        nonce = w3.eth.get_transaction_count(address)

        # Build transaction sesuai ABI terbaru
        tx = contract.functions.terbitkanSertifikat(
            penerima,
            nama,
            universitas,
            jurusan,
            sertifikatToefl,
            sertifikatBTA,
            sertifikatSKP,
            tanggal_str,
            cert_hash
        ).build_transaction({
            'nonce': nonce,
            'maxFeePerGas': 3000000000,
            'maxPriorityFeePerGas': 2000000000,
            'gas': 1000000,
            'value': 0,
            'type': 2,
            'chainId': 1337
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Mengubah status_publish di database
        service.update_status(sertifikat)

        # Simpan transaksi ke DB lewat service
        tx_data = {
            "transaction_hash": tx_hash.hex(),
            "sender_address": address,
            "receiver_address": penerima,
            "amount": 0
        }
        transaction_service.create_transaction(tx_data)

        # Generate QR Code dari DATA sertifikat
        qr = qrcode.make(json.dumps(cert_data, separators=(',', ':'), sort_keys=True))
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return jsonify({
            "transaction_hash": tx_hash.hex(),
            "data_hash": cert_hash,
            "qr_code_base64": img_base64,
            "sertifikat_data": cert_data
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/verifikasi_sertifikat', methods=['POST'])
def verifikasi_sertifikat():
    try:
        data = request.get_json()

        # Daftar field lengkap yang wajib ada
        required_fields = ['penerima', 'nama', 'universitas', 'jurusan',
                           'sertifikatToefl', 'sertifikatBTA', 'sertifikatSKP', 'tanggal']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Data sertifikat tidak lengkap"}), 400

        # Siapkan data untuk hashing sesuai struktur kontrak
        structured_data = {
            "penerima": data["penerima"],
            "nama": data["nama"],
            "universitas": data["universitas"],
            "jurusan": data["jurusan"],
            "sertifikatToefl": data["sertifikatToefl"],
            "sertifikatBTA": data["sertifikatBTA"],
            "sertifikatSKP": data["sertifikatSKP"],
            "tanggal": data["tanggal"],
        }

        # Hash data sertifikat (untuk verifikasi di blockchain)
        cert_hash = hash_cert_data(structured_data)

        # Ambil hash tersimpan di blockchain berdasarkan alamat penerima
        blockchain_hash = contract.functions.getHashByPenerima(data['penerima']).call()

        # Cek apakah hash yang dihitung sama dengan yang ada di blockchain
        if cert_hash != blockchain_hash:
            return jsonify({
                "status": "invalid",
                "message": "❗ Maaf, sertifikat tidak ditemukan di dalam sistem.",
                "note": "Kemungkinan palsu atau tidak diterbitkan melalui sistem ini"
            }), 404

        # Ambil tx_hash terbaru dari penerima (menggunakan service)
        tx_hash = transaction_service.get_latest_tx_hash_by_receiver(data["penerima"])
        if not tx_hash:
            # Jika tidak ditemukan tx_hash di DB, tetap kirim valid tapi tanpa info block
            return jsonify({
                "status": "valid",
                "message": "✅ Sertifikat Terdaftar di Blockchain",
                "data": structured_data,
                "hashBlockchain": blockchain_hash,
                "blockchain_block": None
            }), 200

        # Ambil transaksi dan blok dari tx_hash
        tx = w3.eth.get_transaction(tx_hash)
        block = w3.eth.get_block(tx.blockHash)

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
            "data": structured_data,
            "hashBlockchain": blockchain_hash,
            "blockchain_block": block_info
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/verifikasi_sertifikat_by_hash', methods=['POST'])
def verifikasi_sertifikat_by_hash():
    try:
        data = request.get_json()
        penerima = data.get('penerima')
        data_hash = data.get('data_hash')

        if not penerima or not data_hash:
            return jsonify({"error": "Missing penerima or data_hash"}), 400

        # Ambil tx_hash terbaru berdasarkan penerima
        tx_hash = transaction_service.get_latest_tx_hash_by_receiver(penerima)
        if not tx_hash:
            return jsonify({"error": "Transaction hash for this recipient not found"}), 404

        # Ambil hash yang tersimpan di blockchain berdasarkan penerima
        blockchain_hash = contract.functions.getHashByPenerima(penerima).call()

        if blockchain_hash != data_hash:
            return jsonify({
                "status": "invalid",
                "message": "❗ Hash tidak cocok, sertifikat tidak ditemukan di blockchain"
            }), 404

        # Ambil ID sertifikat penerima
        cert_id = contract.functions.cekSertifikatByPenerima(penerima).call()
        if cert_id == 0:
            return jsonify({
                "status": "not_found",
                "message": "Sertifikat untuk penerima ini tidak ditemukan"
            }), 404

        # Ambil data sertifikat lengkap berdasarkan ID
        cert = contract.functions.daftarSertifikat(cert_id).call()

        # Ambil transaksi dan blok dari tx_hash
        tx = w3.eth.get_transaction(tx_hash)
        block = w3.eth.get_block(tx.blockHash)

        block_info = {
            'number': block.number,
            'hash': block.hash.hex(),
            'parentHash': block.parentHash.hex(),
            'timestamp': block.timestamp,
            'transactions_count': len(block.transactions)
        }

        sertifikat_data = {
            "id": cert[0],
            "penerima": cert[1],
            "nama": cert[2],
            "universitas": cert[3],
            "jurusan": cert[4],
            "sertifikatToefl": cert[5],
            "sertifikatBTA": cert[6],
            "sertifikatSKP": cert[7],
            "tanggal": cert[8],
            "valid": cert[9]
        }

        return jsonify({
            "status": "valid",
            "message": "✅ Sertifikat terverifikasi dan data sesuai dengan yang diblockchain",
            "sertifikat": sertifikat_data,
            "blockchain_block": block_info
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/blockchain/sertifikat/by_address', methods=['POST'])
def get_sertifikat_by_address():
    try:
        data = request.get_json()
        address = data.get('address')
        if not address:
            return jsonify({"error": "Address Tidak Ada"}), 400
        
        # 1. Ambil id_blockchain dari smart contract pakai address
        id_blockchain = contract.functions.cekSertifikatByPenerima(address).call()
        if id_blockchain == 0:
            return jsonify({"error": "Sertifikat tidak ditemukan di blockchain"}), 404
        
        # 2. Ambil data sertifikat dari smart contract pakai id_blockchain
        sertifikat = get_sertifikat_from_blockchain(id_blockchain)
        return jsonify(sertifikat), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint untuk melihat semua transaksi yang disimpan di MySQL
@app.route('/sertifikat', methods=['GET'])
def get_all_sertifikat():
    try:
        sertifikat_list = service.get_all_sertifikat()
        data = []
        for s in sertifikat_list:
            data.append({
                "id": str(s.id),
                "penerima": s.penerima,
                "nama": s.nama,
                "universitas": s.universitas,
                "jurusan": s.jurusan,
                "sertifikatToefl": s.sertifikatToefl,
                "sertifikatBTA": s.sertifikatBTA,
                "sertifikatSKP": s.sertifikatSKP,
                "status_publish": s.status_publish,
                "tanggal": s.tanggal.isoformat() if hasattr(s.tanggal, 'isoformat') else str(s.tanggal),
            })
        return jsonify({"sertifikat": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
