from database.data.db_imports import *

class Save(SqlAlchemyBase):
    __tablename__ = 'save'
    id = Column(Integer, autoincrement=True, primary_key=True)
    tg_id = Column(Integer)
    type_id = Column(Integer, default=0)

    stage_id = Column(Integer, default=0)
    phrase_id = Column(Integer, default=0)
    msg_id = Column(Integer)
