from database.core.db_imports import *


class Transactions(SqlAlchemyBase):
    __tablename__ = 'transactions'
    transaction_id = Column(Text, primary_key=True)
    date = Column(DATETIME)
