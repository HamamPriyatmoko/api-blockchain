from models.sertifikat import Sertifikat
from database import Session
from sqlalchemy.exc import NoResultFound
from datetime import date

class SertifikatService:
    def __init__(self):
        self.session = Session()

    def create_sertifikat(self, data: dict) -> Sertifikat:
        """
        Buat sertifikat baru dari data dict, simpan ke DB.
        data harus berisi keys:
        penerima, nama, universitas, jurusan,
        sertifikat_toefl, sertifikat_bta, sertifikat_skp, tanggal (date atau str)
        """
        # Jika tanggal berupa string, ubah ke date
        tanggal = data.get('tanggal')
        if isinstance(tanggal, str):
            tanggal = date.fromisoformat(tanggal)

        sertifikat = Sertifikat(
            penerima=data.get('penerima'),
            nama=data.get('nama'),
            universitas=data.get('universitas'),
            jurusan=data.get('jurusan'),
            sertifikatToefl=data.get('sertifikatToefl'),
            sertifikatBTA=data.get('sertifikatBTA'),
            sertifikatSKP=data.get('sertifikatSKP'),
            status_publish='proses',
            tanggal=tanggal,
        )
        self.session.add(sertifikat)
        self.session.commit()
        return sertifikat

    def get_sertifikat_by_id(self, sertifikat_id):
        """
        Ambil sertifikat berdasarkan UUID id
        """
        sertifikat = self.session.query(Sertifikat).filter_by(id=sertifikat_id).first()
        if not sertifikat:
            raise NoResultFound(f"Sertifikat dengan id {sertifikat_id} tidak ditemukan")
        return sertifikat
    
    def update_status(self, sertifikat):
        if sertifikat:
            sertifikat.status_publish = 'publish'
            self.session.commit()
    
    def get_all_sertifikat(self):
        return self.session.query(Sertifikat).all()
