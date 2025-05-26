from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String(66), unique=True, nullable=False)  # panjang hash tx biasanya 66 char (0x + 64 hex)
    sender_address = Column(String(42), nullable=False)  # panjang address Ethereum 42 char
    receiver_address = Column(String(42), nullable=False)
    amount = Column(Numeric(precision=38, scale=0), nullable=False)  # bisa sesuaikan precision/scale
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction(id={self.id}, hash={self.transaction_hash}, sender={self.sender_address})>"
