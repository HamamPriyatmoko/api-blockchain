from flask import Flask, request, jsonify
from web3 import Web3
from utils.utils import hash_cert_data, format_sertifikat_data, parse_certificate_text, fetch_ipfs_data
from utils.contract_data import contract_abi
from flask_cors import CORS
from ipfs_client.ipfs_client import upload_directory_to_pinata
import fitz
from functools import lru_cache
import os
import io
import json
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token
)
from utils.db import get_db
from datetime import datetime, timedelta, timezone
import secrets
from utils.email_sender import send_reset_email

load_dotenv()

# Configuration from Environment Variables
GANACHE_URL = os.getenv('GANACHE_URL')
print(GANACHE_URL)
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
IPFS_GATEWAY = os.getenv('IPFS_GATEWAY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
URL_FRONTEND = os.getenv('URL_FRONTEND')

# Validation for Environment Variables
if not all([GANACHE_URL, PRIVATE_KEY, IPFS_GATEWAY, CONTRACT_ADDRESS]):
    raise ValueError("One or more environment variables are missing. Please check your .env file.")

# Setup Flask
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)


# Setup Web3 for connection
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
print(w3)

# Verify Web3 connection
if w3.is_connected():
    print("Connected to Ethereum Network")
else:
    print("Connection failed")
    exit()

# Global Variables
ADMIN_ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not password or not email:
        return jsonify({"error": "Username, email, & password wajib diisi"}), 400

    db = get_db()
    with db.cursor() as cur:

        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            return jsonify({"error": "Username sudah terdaftar"}), 400
        
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            return jsonify({"error": "Email sudah terdaftar"}), 400

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, pw_hash)
        )
    return jsonify({"message": "Registrasi berhasil"}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "Username & password wajib diisi"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if not user or not bcrypt.check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Login gagal"}), 401

    access_token = create_access_token(identity=user["id"])
    return jsonify({"access_token": access_token}), 200

@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "Email wajib diisi"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, username FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"message": "Jika email Anda terdaftar, instruksi reset akan dikirim."}), 200

        token = secrets.token_urlsafe(32)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        cur.execute(
            "UPDATE users SET reset_token=%s, reset_token_expiry=%s WHERE id=%s",
            (token, expiry_time, user["id"])
        )

    reset_link = f"{URL_FRONTEND}/reset-password/{token}"
    print(reset_link)
    
    # PANGGIL FUNGSI PENGIRIM EMAIL DI SINI
    email_sent = send_reset_email(email, reset_link)

    if not email_sent:
        app.logger.error(f"Gagal mengirim email reset password ke {email}")
    
    return jsonify({"message": "Jika email Anda terdaftar, instruksi reset password telah dikirim."}), 200

@app.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"error": "Token dan password baru wajib diisi"}), 400

    db = get_db()
    with db.cursor() as cur:
        # Cari user berdasarkan token dan pastikan token belum kedaluwarsa
        current_time = datetime.now(timezone.utc)
        cur.execute(
            "SELECT id FROM users WHERE reset_token=%s AND reset_token_expiry > %s",
            (token, current_time)
        )
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Token tidak valid atau sudah kedaluwarsa"}), 400
        
        # Hash password baru
        pw_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")

        # Update password dan hapus token reset
        cur.execute(
            "UPDATE users SET password_hash=%s, reset_token=NULL, reset_token_expiry=NULL WHERE id=%s",
            (pw_hash, user["id"])
        )

    return jsonify({"message": "Password berhasil direset. Silakan login."}), 200

@app.route("/api/universitas", methods=["GET"])
def get_universitas():
    """Mengembalikan daftar semua universitas."""
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT id, nama_universitas FROM universitas ORDER BY nama_universitas ASC")
            all_universitas = cursor.fetchall()
        return jsonify(all_universitas), 200
    except Exception as e:
        app.logger.error(f"Error fetching universitas: {e}")
        return jsonify({"error": "Gagal mengambil data universitas"}), 500

@app.route("/api/universitas/<int:id_universitas>/fakultas", methods=["GET"])
def get_fakultas_by_universitas(id_universitas):
    """Mengembalikan daftar fakultas untuk satu universitas tertentu."""
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, nama_fakultas FROM fakultas WHERE id_universitas = %s ORDER BY nama_fakultas ASC", 
                (id_universitas,)
            )
            fakultas_list = cursor.fetchall()
        return jsonify(fakultas_list), 200
    except Exception as e:
        app.logger.error(f"Error fetching fakultas for university {id_universitas}: {e}")
        return jsonify({"error": "Gagal mengambil data fakultas"}), 500

@app.route("/api/fakultas/<int:id_fakultas>/jurusan", methods=["GET"])
def get_jurusan_by_fakultas(id_fakultas):
    """Mengembalikan daftar jurusan untuk satu fakultas tertentu."""
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, nama_jurusan FROM jurusan WHERE id_fakultas = %s ORDER BY nama_jurusan ASC",
                (id_fakultas,)
            )
            jurusan_list = cursor.fetchall()
        return jsonify(jurusan_list), 200
    except Exception as e:
        app.logger.error(f"Error fetching jurusan for faculty {id_fakultas}: {e}")
        return jsonify({"error": "Gagal mengambil data jurusan"}), 500

@app.route('/api/certificate/metadata', methods=['GET'])
def get_certificate_metadata():
    cid = request.args.get('cid')
    nim = request.args.get('nim')
    if not cid:
        return jsonify({"error": "CID is required"}), 400

    try:
        data = fetch_ipfs_data(cid, nim)

        if data is not None:
            return jsonify(data)
        else:
            error_message = f"Failed to fetch metadata for CID {cid} from Pinata gateway."
            return jsonify({"error": error_message}), 502

    except Exception as e:
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500

# # Endpoint untuk melihat semua transaksi yang disimpan di Blockchain
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

        print(sertifikat_list)
        return jsonify({"sertifikat": sertifikat_list}), 200

    except Exception as e:
        app.logger.error("Fatal di get_all_sertifikat", exc_info=e)
        return jsonify({"error": f"Kesalahan server: {str(e)}"}), 500


@app.route("/api/sertifikat", methods=["POST"])
def api_sertifikat():
    data = {
        "nim": request.form.get("nim", ""), "universitas": request.form.get("universitas", ""),
        "nomerSertifikat": request.form.get("nomerSertifikat", ""), "nama": request.form.get("nama", ""),
        "jurusan": request.form.get("jurusan", ""), "fakultas": request.form.get("fakultas", ""),
        "tahunLulus": request.form.get("tahunLulus", ""),
    }
    files = {"ijazah": request.files.get("file_ijazah"), "skpi": request.files.get("file_skpi"),}
    missing = [k for k in ["nim","universitas","nomerSertifikat"] if not data[k]] + [k for k,v in files.items() if v is None]
    if missing:
        return jsonify({"error": f"Wajib diisi/file: {', '.join(missing)}"}), 400

    metadata_to_hash = {"nim": data["nim"], "universitas": data["universitas"], "nomerSertifikat": data["nomerSertifikat"],}
    hashMetadata = hash_cert_data(metadata_to_hash)

    ijazah_filename = f"ijazah_{data['nim']}.pdf"
    skpi_filename = f"skpi_{data['nim']}.pdf"

    full_metadata_for_ipfs = {
        "nama": data["nama"], 
        "jurusan": data["jurusan"], 
        "fakultas": data["fakultas"], 
        "tahunLulus": data["tahunLulus"],
        "path_ijazah": ijazah_filename,
        "path_skpi": skpi_filename
    }
    
    metadata_json_string = json.dumps(full_metadata_for_ipfs, indent=2)
    metadata_stream = io.BytesIO(metadata_json_string.encode('utf-8'))
    metadata_stream.seek(0)
    
    # Siapkan file untuk diunggah (tidak ada perubahan di sini)
    directory_name = f"sertifikat-{data['nim']}"
    files_for_pin = [
        (ijazah_filename, files["ijazah"].stream),
        (skpi_filename,   files["skpi"].stream),
        ("metadata.json", metadata_stream)
    ]

    # Upload ke IPFS (tidak ada perubahan)
    try:
        cidDetail = upload_directory_to_pinata(files_for_pin, directory_name=directory_name)
    except Exception as e:
        app.logger.error(f"Gagal saat upload ke Pinata: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    # Kembalikan response (tidak ada perubahan)
    return jsonify({"cidDetail": cidDetail, "hashMetadata": hashMetadata}), 200

@app.route("/api/verify-pdf", methods=["POST"])
def api_verify_pdf():
    pdf = request.files.get("file_sertifikat")
    print(pdf)
    if not pdf:
        return jsonify({"error":"PDF tidak ditemukan"}), 400

    # buka PDF dengan fitz
    pdf_bytes = pdf.stream.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # extract teks
    raw_text = ""
    for page in doc:
        raw_text += page.get_text("text")

    # parse fields minimal
    extracted = parse_certificate_text(raw_text)
    if not extracted.get("nim") or not extracted.get("nomerSertifikat"):
        return jsonify({"error":"Gagal ekstrak NIM atau No Sertifikat"}), 400

    # hash hanya nim, universitas, nomerSertifikat
    metadata_to_hash = {
        "nim":             extracted["nim"],
        "universitas":     extracted.get("universitas",""),
        "nomerSertifikat": extracted["nomerSertifikat"],
    }
    hashMetadata = hash_cert_data(metadata_to_hash)

    return jsonify({
        "extracted":    extracted,
        "hashMetadata": hashMetadata
    }), 200


if __name__ == '__main__':
    # The debug flag will be set based on an environment variable, e.g., FLASK_DEBUG
    # app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't'])
    host = os.getenv('FLASK_RUN_HOST')
    # port = int(os.getenv('FLASK_RUN_PORT'))
    # debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(host=host, port=5000, debug=True)