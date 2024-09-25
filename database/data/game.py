from database.data.db_imports import *


class Game(SqlAlchemyBase):
    __tablename__ = 'game'
    tg_id = Column(Integer, primary_key=True)
    tokens = Column(Integer, default=5)
    premium = Column(Integer, default=0)
