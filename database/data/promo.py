from database.data.db_imports import *


class Promo(SqlAlchemyBase):
    __tablename__ = 'promo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    code = Column(String)
    value = Column(Integer)
