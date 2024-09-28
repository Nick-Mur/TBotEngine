from database.data.db_imports import *


class Transactions(SqlAlchemyBase):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True)
    date = Column(DATETIME)
