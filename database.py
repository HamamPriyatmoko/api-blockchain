from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.sertifikat import Base  # model dari models.py

# Sesuaikan username, password, database name
DATABASE_URL = 'mysql+mysqlconnector://root:@127.0.0.1:3306/blockchain_data'

engine = create_engine(DATABASE_URL, echo=True)  # echo=True untuk log SQL (opsional)

Session = sessionmaker(bind=engine)

# Buat tabel jika belum ada
Base.metadata.create_all(engine)
