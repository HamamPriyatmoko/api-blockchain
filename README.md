# Implementasi Sistem Verifikasi Sertifikat Menggunakan Teknologi Blockchain (Back-end Flask Api)

**Disusun oleh:**
* **Hamam Priyatmoko** (NIM: 20210140077)

**Dosen Pembimbing:**
* **Ir. Eko Prasetyo, M.Eng., Ph.D.** (NIDN: 0522046701)
* **Cahya Damarjati, S.T. M. Eng., Ph.D.** (NIDN: 0515038702)  
* **Prayitno, S.ST., M.T., Ph.D.** (NIDN: 0010048506)

## Deskripsi Proyek
Proyek ini merupakan API berbasis **Flask** yang digunakan untuk sistem **verifikasi sertifikat akademik menggunakan teknologi blockchain**.  
Sertifikat digital diterbitkan, disimpan hash-nya di blockchain, serta dapat diverifikasi keasliannya.  
Selain itu, sistem mendukung penyimpanan file di **IPFS PINATA**, autentikasi pengguna dengan **JWT**, serta integrasi **MySQL** untuk penyimpanan data yang tidak terlalu krusial.

## Fitur Utama
- **Autentikasi & Autorisasi**: Login berbasis JWT.
- **Penerbitan Sertifikat**: Generate sertifikat dalam bentuk **PDF** dengan **QR Code**.
- **Mengambil Data Blockchain**: Mengambil data yang disimpan diblockchain **Web3.py**.
- **Penyimpanan IPFS**: File disimpan secara terdistribusi di IPFS.
- **Manajemen User & Role**: Admin.
- **Verifikasi Sertifikat**: Validasi sertifikat melalui hash blockchain.
- **Email Notifikasi**: Menggunakan **SendGrid API**.

## Teknologi yang Digunakan
- **Backend**: Flask (Python 3.x)
- **Database**: MySQL
- **Blockchain**: Web3.py (Ethereum-compatible)
- **File Storage**: IPFS, Pinata
- **PDF & QR Code**: fpdf2, PyMuPDF, qrcode
- **Authentication**: JWT (Flask-JWT-Extended)
- **Email Service**: SendGrid
- **ORM**: SQLAlchemy + Flask-Migrate
- **Env Management**: python-dotenv

## Persyaratan Sistem
- Python 3.10 atau lebih baru
- MySQL 8.x
- Node / Ganache / Blockchain environment (Ethereum-compatible)
- IPFS daemon (opsional, jika ingin pakai IPFS lokal)
- Paket dependensi dari `requirements.txt`

## Panduan Instalasi dan Menjalankan Proyek

1. **Clone Repository**
   ```bash
   git clone https://github.com/username/api-blockchain.git
   cd api-blockchain
   ```
2. Buat Virtual Environment & Install Dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```
3. Atur Konfigurasi
   ```bash
   DATABASE_URL=mysql+pymysql://username:password@localhost/nama_db
   SECRET_KEY=secret_key_flask
   JWT_SECRET_KEY=secret_key_jwt
   WEB3_PROVIDER_URI=http://127.0.0.1:7545
   IPFS_API_URI=http://127.0.0.1:5001
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```
5. Jalankan Aplikasi
   ```bash
   python app.py
   ```
    
