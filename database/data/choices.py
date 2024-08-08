from imports import *


class Choices(SqlAlchemyBase):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    choice_id = Column(Integer)
    result_choice = Column(Integer)
