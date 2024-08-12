from imports import *


class Save(SqlAlchemyBase):
    __tablename__ = 'save'
    id = Column(Integer, autoincrement=True, primary_key=True)
    tg_id = Column(Integer)
    type_id = Column(Integer)

    text_now = Column(String, default='phrase_0_0_0')
    media_now = Column(String, default='media_0_0_0')
    keyboard_now = Column(String, default='next_0')

    text_previous = Column(String, default='phrase_0_0_0')
    media_previous = Column(String, default='media_0_0_0')
    keyboard_previous = Column(String, default='next_0')

    stage_id = Column(Integer, default=0)
    phrase_id = Column(Integer, default=0)
    msg_id = Column(Integer)
