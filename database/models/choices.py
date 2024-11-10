from database.core.db_imports import *


class Choices(SqlAlchemyBase):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    message_id = Column(Integer)
    choice = Column(String)
