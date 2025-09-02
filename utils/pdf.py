from fpdf import FPDF
import qrcode
import io
from datetime import datetime
import locale
import os
from dotenv import load_dotenv

load_dotenv()

URL_VERIFY = os.getenv('URL_FRONTEND')
print(URL_VERIFY)

try:
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
except locale.Error:
    print("Peringatan: Locale 'id_ID.UTF-8' tidak ditemukan. Format tanggal mungkin dalam Bahasa Inggris.")
    pass

class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

def create_certificate_pdf(cert_data, ipfs_metadata):
    """
    Membuat PDF sertifikat dengan layout yang sama persis seperti di jsPDF.
    """
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    margin = 25
    page_width = pdf.w 

    verification_url = f'{URL_VERIFY}/verify/{cert_data["hashMetadata"]}'
    qr_img = qrcode.make(verification_url)
    qr_stream = io.BytesIO()
    qr_img.save(qr_stream, format="PNG")
    qr_stream.seek(0)
    
    pdf.set_y(30)
    pdf.set_font('Helvetica', '', 14)
    pdf.cell(0, 10, cert_data["universitas"].upper(), 0, 1, 'C')

    pdf.set_line_width(0.5)
    pdf.line(margin, 40, page_width - margin, 40)

    pdf.set_y(55)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'SERTIFIKAT KELULUSAN', 0, 1, 'C')
    
    pdf.set_y(70)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, 'Tanda Tangan Digital (Blockchain Hash)', 0, 1, 'C')
    
    pdf.set_y(76)
    pdf.set_font('Courier', '', 9)
    pdf.set_text_color(100, 100, 100) 
    pdf.cell(0, 6, cert_data["hashMetadata"].lower(), 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_y(96)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, ipfs_metadata["nama"].upper(), 0, 1, 'C')
    
    pdf.set_y(108)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, 'telah memenuhi segala syarat kelulusan dan dinyatakan', 0, 1, 'C')

    pdf.set_y(118)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'LULUS', 0, 1, 'C')

    pdf.set_y(138)
    pdf.set_font('Helvetica', '', 11)
    
    details = [
        ("Nomor Sertifikat", cert_data["nomerSertifikat"]),
        ("Nomor Induk Mahasiswa", cert_data["nim"]),
        ("Program Studi", ipfs_metadata["jurusan"]),
        ("Fakultas", ipfs_metadata["fakultas"]),
        ("Tahun Lulus", ipfs_metadata["tahunLulus"]),
    ]
    
    label_width = 55
    col2_x = margin + label_width
    for label, value in details:
        pdf.set_x(margin)
        pdf.cell(label_width, 8, label, 0, 0, 'L')
        pdf.cell(3, 8, ':', 0, 0, 'R')
        pdf.set_x(col2_x)
        pdf.multi_cell(page_width - margin - col2_x, 8, str(value), 0, 'L')
        pdf.ln(0)
        
    
    sig_y = pdf.get_y() + 20

    pdf.set_y(sig_y)

    tanggal_str = datetime.now().strftime('%d %B %Y')
    pdf.cell(0, 7, f'Yogyakarta, {tanggal_str}', 0, 1, 'R')
    pdf.cell(0, 7, 'Rektor,', 0, 1, 'R')
    pdf.ln(16)
    pdf.cell(0, 7, '(Nama Rektor)', 0, 1, 'R')

    qr_size = 30
    qr_y = pdf.h - margin - qr_size - 10 
    pdf.image(qr_stream, x=margin, y=qr_y, w=qr_size, h=qr_size)
    
    text_qr_x = margin + qr_size + 5
    text_qr_y = qr_y + (qr_size / 2) - 6
    pdf.set_xy(text_qr_x, text_qr_y)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(0, 5, 'Verifikasi Keaslian Dokumen:', 0, 1)
    pdf.set_x(text_qr_x)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(0, 5, 'Pindai QR Code untuk detail sertifikat di blockchain.', 0, 1)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer