from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from elsevier.exceptions import ElsevierException


Base = declarative_base()


class Article(Base):

    __tablename__ = 'articles'
    uid = Column(String, primary_key=True)
    id_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    full_text = Column(String, nullable=True)

    def download(self, session):
        try:
            print('adding article ' + self.uid)
            session.add(self)
            session.commit()
        except Exception as e:
            print(e.args)
            session.rollback()

    def __repr__(self):
        return '<Article (Title=%s, id=%s)>' % (
                self.title.encode('utf8'), self.uid.encode('utf8'))

