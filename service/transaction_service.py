from models.transaction import Transaction
from database import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime

class TransactionService:
    def __init__(self):
        self.session = Session()

    def create_transaction(self, data: dict) -> Transaction:
        """
        Buat transaksi baru dan simpan ke DB.
        Data dict harus berisi:
        transaction_hash, sender_address, receiver_address, amount, timestamp (optional)
        """
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        transaction = Transaction(
            transaction_hash=data.get('transaction_hash'),
            sender_address=data.get('sender_address'),
            receiver_address=data.get('receiver_address'),
            amount=data.get('amount'),
            timestamp=timestamp or datetime.utcnow()
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction

    def get_transaction_by_hash(self, tx_hash: str) -> Transaction:
        """
        Cari transaksi berdasarkan hash.
        """
        transaction = self.session.query(Transaction).filter_by(transaction_hash=tx_hash).first()
        if not transaction:
            raise NoResultFound(f"Transaction with hash {tx_hash} not found")
        return transaction

    def list_transactions(self, limit=100):
        """
        Ambil daftar transaksi terbaru, default limit 100.
        """
        return self.session.query(Transaction).order_by(Transaction.timestamp.desc()).limit(limit).all()
    
    def get_latest_tx_hash_by_receiver(self, receiver_address: str):
        transaction = self.session.query(Transaction) \
            .filter_by(receiver_address=receiver_address) \
            .order_by(Transaction.timestamp.desc()) \
            .first()
        if transaction:
            return transaction.transaction_hash
        return None

