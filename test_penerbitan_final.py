import os
import requests
import random
from faker import Faker
from fpdf import FPDF

# Inisialisasi Faker dan daftar konstanta
fake = Faker('id_ID')
DAFTAR_UNIVERSITAS = ["Universitas Muhammadiyah Yogyakarta"]
DAFTAR_JURUSAN_TEKNIK = ["Teknologi Informasi", "Teknik Sipil", "Teknik Elektro", "Teknik Mesin"]

def create_dummy_pdf(filename, title, nama, nim):
    """
    Membuat file PDF sederhana dengan margin eksplisit dan 
    memastikan setiap baris dicetak dari left margin yang sama.
    """
    pdf = FPDF(format='A4', unit='mm')
    pdf.add_page()

    # 1) Set margin kiri/kanan (10 mm)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # 2) Hitung effective page width
    epw = pdf.w - pdf.l_margin - pdf.r_margin

    # 3) Cetak judul di tengah
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(epw, 10, title, ln=1, align='C')
    pdf.ln(10)

    # 4) Cetak Nama dan NIM, baris per baris, left-aligned
    pdf.set_font("helvetica", size=12)
    # Nama
    pdf.set_x(pdf.l_margin)
    pdf.cell(epw, 8, f"Nama: {nama}", ln=1, align='L')
    # NIM
    pdf.set_x(pdf.l_margin)
    pdf.cell(epw, 8, f"NIM: {nim}", ln=1, align='L')
    pdf.ln(5)

    # 5) Cetak statement panjang dengan multi_cell
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        epw, 8,
        f"Dengan ini menyatakan bahwa yang bersangkutan telah memenuhi syarat untuk '{title}'."
    )

    # 6) Simpan file
    pdf.output(filename)
    print(f"File PDF dummy '{filename}' berhasil dibuat.")

def generate_dummy_sertifikat_data():
    firstName = fake.first_name_male()
    lastName = fake.last_name_male()
    nama_mahasiswa = firstName + ' ' + lastName
    tahun_masuk = random.choice(["2020", "2021", "2022"])
    kode_jurusan = "0140"
    nomor_urut = f"{fake.random_int(min=1, max=999):03d}"
    nim = f"{tahun_masuk}{kode_jurusan}{nomor_urut}"
    return {
        "nim": nim,
        "nama": nama_mahasiswa,
        "universitas": random.choice(DAFTAR_UNIVERSITAS),
        "jurusan": random.choice(DAFTAR_JURUSAN_TEKNIK),
        "tanggalTerbit": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')
    }

if __name__ == "__main__":
    sertifikat_data = generate_dummy_sertifikat_data()
    print("\n--- Data Teks yang Dihasilkan ---")
    print(sertifikat_data)

    # Siapkan dummy PDF
    filenames_to_upload = {}
    dokumen_syarat = {
        'pdf_perpustakaan': "Surat Keterangan Bebas Perpustakaan",
        'pdf_laboratorium': "Surat Keterangan Bebas Laboratorium",
        'pdf_keuangan': "Surat Keterangan Bebas Keuangan",
        'pdf_skripsi': "Bukti Penyerahan Skripsi",
        'pdf_toefl': "Sertifikat TOEFL"
    }
    files_for_request = {}

    try:
        print("\n--- Membuat File PDF Dummy ---")
        for key, title in dokumen_syarat.items():
            filename = f"dummy_{key}_{sertifikat_data['nim']}.pdf"
            create_dummy_pdf(filename, title, sertifikat_data['nama'], sertifikat_data['nim'])
            filenames_to_upload[key] = filename

        for key, filename in filenames_to_upload.items():
            files_for_request[key] = (filename, open(filename, 'rb'), 'application/pdf')

        print("\n--- Mengirim Data dan File ke API ---")
        API_URL = "http://127.0.0.1:5000/sertifikat"
        response = requests.post(API_URL, data=sertifikat_data, files=files_for_request)
        response.raise_for_status()

        print("\n--- Hasil dari API ---")
        print(f"Status Code: {response.status_code}")
        print("Response JSON:", response.json())

    except Exception as e:
        print("\n--- PROSES GAGAL ---")
        print(f"Error: {e}")

    finally:
        print("\n--- Membersihkan File Dummy ---")
        for _, f_info in files_for_request.items():
            try:
                f_info[1].close()
            except:
                pass
        for filename in filenames_to_upload.values():
            if os.path.exists(filename):
                os.remove(filename)
                print(f"File '{filename}' berhasil dihapus.")
