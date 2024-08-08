from imports import *


class Save(SqlAlchemyBase):
    __tablename__ = 'save'
    tg_id = Column(Integer, primary_key=True)
    text = Column(String, default='phrase_0_0')
    media = Column(String, default='media_0_0')
    keyboard = Column(String, default='keyboard_0_0')
    stage_id = Column(Integer, default=0)
    phrase_id = Column(Integer, default=0)
    msg_id = Column(Integer)
