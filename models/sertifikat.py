from sqlalchemy import Column, String, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import CHAR


Base = declarative_base()

class Sertifikat(Base):
    __tablename__ = 'sertifikat'

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    penerima = Column(String(42), nullable=False)
    nama = Column(String(255), nullable=False)
    universitas = Column(String(255), nullable=False)
    jurusan = Column(String(255), nullable=False)
    sertifikatToefl = Column(String(255), nullable=True)
    sertifikatBTA = Column(String(255), nullable=True)
    sertifikatSKP = Column(String(255), nullable=True)
    status_publish = Column(String(20), default='proses')
    tanggal = Column(Date, nullable=False)

    def __repr__(self):
        return f"<Sertifikat(id={self.id}, penerima={self.penerima}, nama={self.nama})>"
