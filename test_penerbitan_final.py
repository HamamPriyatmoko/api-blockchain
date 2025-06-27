import os
import requests
import random
from faker import Faker
from fpdf import FPDF
import traceback

# ==============================================================================
# KONFIGURASI
# ==============================================================================
# Pastikan URL ini sesuai dengan alamat server API Anda
API_URL = "http://127.0.0.1:5000/api/sertifikat"

# Inisialisasi Faker untuk data Indonesia
fake = Faker('id_ID')

# Daftar data untuk digenerate secara acak
DAFTAR_UNIVERSITAS = ["Universitas Muhammadiyah Yogyakarta", "Universitas Gadjah Mada", "Universitas Negeri Yogyakarta"]
DAFTAR_FAKULTAS_TEKNIK = {
    "Fakultas Teknik": ["Teknik Informatika", "Teknik Sipil", "Teknik Elektro", "Teknik Mesin"],
    "Fakultas Ekonomi": ["Akuntansi", "Manajemen", "Ilmu Ekonomi"],
    "Fakultas Hukum": ["Ilmu Hukum"]
}

# ==============================================================================
# FUNGSI-FUNGSI PEMBANTU
# ==============================================================================

def create_dummy_pdf(filename, title, data):
    """
    Membuat file PDF sederhana dengan data sertifikat.
    """
    pdf = FPDF(format='A4', unit='mm')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set margin
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # Judul Dokumen
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, title, ln=1, align='C')
    pdf.ln(10)

    # Isi Dokumen
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 8, f"Dokumen ini menyatakan bahwa:", ln=1)
    pdf.ln(5)

    # Tabel data mahasiswa
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(50, 8, "Nama", border=1)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 8, f": {data['nama']}", border=1, ln=1)
    
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(50, 8, "NIM", border=1)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 8, f": {data['nim']}", border=1, ln=1)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(50, 8, "Universitas", border=1)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 8, f": {data['universitas']}", border=1, ln=1)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(50, 8, "Program Studi", border=1)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 8, f": {data['jurusan']}", border=1, ln=1)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(50, 8, "Nomor Sertifikat", border=1)
    pdf.set_font("helvetica", '', 12)
    pdf.cell(0, 8, f": {data['nomerSertifikat']}", border=1, ln=1)
    pdf.ln(10)

    pdf.set_font("helvetica", '', 12)
    pdf.multi_cell(0, 8, f"Telah dinyatakan LULUS pada tahun {data['tahunLulus']} dan berhak menggunakan sertifikat ini sebagaimana mestinya.")

    # Simpan file
    pdf.output(filename)
    print(f"  -> File PDF dummy '{filename}' berhasil dibuat.")


def generate_dummy_sertifikat_data():
    """
    Menghasilkan satu set data sertifikat yang realistis.
    """
    fakultas = random.choice(list(DAFTAR_FAKULTAS_TEKNIK.keys()))
    jurusan = random.choice(DAFTAR_FAKULTAS_TEKNIK[fakultas])
    
    first_name = fake.first_name_male()
    last_name = fake.last_name_male()

    nama_mahasiswa = first_name + ' ' + last_name
    tahun_masuk = random.choice(["2019", "2020", "2021"])
    kode_jurusan = f"{fake.random_int(min=10, max=99):02d}"
    nomor_urut_nim = f"{fake.random_int(min=1, max=999):03d}"
    nim = f"{tahun_masuk}{kode_jurusan}{nomor_urut_nim}"

    # Membuat nomor sertifikat yang logis
    nomor_urut_sertifikat = f"{fake.random_int(min=1, max=500):03d}"
    kode_prodi = "".join([word[0] for word in jurusan.split()]).upper()
    bulan_romawi = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][fake.date_object().month - 1]
    tahun_lulus = int(tahun_masuk) + 4
    nomer_sertifikat = f"{nomor_urut_sertifikat}/IJZ/{kode_prodi}/{bulan_romawi}/{tahun_lulus}"
    
    return {
        "nim": nim,
        "nama": nama_mahasiswa,
        "universitas": random.choice(DAFTAR_UNIVERSITAS),
        "jurusan": jurusan,
        "fakultas": fakultas,
        "tahunLulus": str(tahun_lulus),
        "nomerSertifikat": nomer_sertifikat,
    }

# ==============================================================================
# SCRIPT UTAMA
# ==============================================================================

if __name__ == "__main__":
    # 1. Hasilkan data teks
    sertifikat_data = generate_dummy_sertifikat_data()
    print("\n--- Data Teks yang Dihasilkan ---")
    for key, value in sertifikat_data.items():
        print(f"- {key}: {value}")

    # 2. Siapkan file PDF dummy sesuai yang dibutuhkan API
    filenames_to_delete = []
    files_for_request = {}

    try:
        print("\n--- Membuat File PDF Dummy ---")
        
        # Buat file Ijazah
        ijazah_filename = f"dummy_ijazah_{sertifikat_data['nim']}.pdf"
        create_dummy_pdf(ijazah_filename, "IJAZAH KELULUSAN", sertifikat_data)
        filenames_to_delete.append(ijazah_filename)

        # Buat file SKPI
        skpi_filename = f"dummy_skpi_{sertifikat_data['nim']}.pdf"
        create_dummy_pdf(skpi_filename, "SURAT KETERANGAN PENDAMPING IJAZAH (SKPI)", sertifikat_data)
        filenames_to_delete.append(skpi_filename)

        # Buka file untuk dikirim dalam request
        # Kunci harus 'file_ijazah' dan 'file_skpi' sesuai dengan yang diharapkan API
        files_for_request['file_ijazah'] = (ijazah_filename, open(ijazah_filename, 'rb'), 'application/pdf')
        files_for_request['file_skpi'] = (skpi_filename, open(skpi_filename, 'rb'), 'application/pdf')

        # 3. Kirim data dan file ke API
        print("\n--- Mengirim Data dan File ke API ---")
        print(f"URL: POST {API_URL}")
        
        response = requests.post(API_URL, data=sertifikat_data, files=files_for_request)
        
        # Menampilkan pesan error jika request gagal
        response.raise_for_status()

        # 4. Tampilkan hasil
        print("\n--- Hasil dari API ---")
        print(f"Status Code: {response.status_code}")
        print("Response JSON:", response.json())

    except requests.exceptions.HTTPError as http_err:
        print("\n--- PROSES GAGAL (HTTP Error) ---")
        print(f"Error: {http_err}")
        print("Response Body:", response.text)
    except Exception as e:
        print("\n--- PROSES GAGAL ---")
        print(f"Error: {e}")
        traceback.print_exc()

    finally:
        # 5. Selalu tutup file dan hapus file dummy
        print("\n--- Membersihkan File Dummy ---")
        for f_info in files_for_request.values():
            try:
                f_info[1].close() # Menutup file stream
            except Exception:
                pass
        
        for filename in filenames_to_delete:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  -> File '{filename}' berhasil dihapus.")
