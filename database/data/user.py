from imports import *


class User(SqlAlchemyBase):
    __tablename__ = 'user'
    tg_id = Column(Integer, primary_key=True)
    language = Column(String, default='ru')
