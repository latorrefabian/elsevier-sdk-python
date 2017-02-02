from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, ForeignKey, PickleType, Date
from elsevier.exceptions import ElsevierException


Base = declarative_base()


class Article(Base):

    __tablename__ = 'articles'
    uid = Column(String, primary_key=True)
    id_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    full_text = Column(PickleType, nullable=True)
    keywords = Column(PickleType, nullable=True)
    pub_date = Column(Date, nullable=True)
    accept_date = Column(Date, nullable=True)
    submit_date = Column(Date, nullable=True)

    def download(self, session):
        try:
            print('adding article ' + self.uid)
            session.add(self)
            session.commit()
        except Exception as e:
            print(e.args)
            print(self.title)
            session.rollback()

    def full_text_str(self):
        sections = self.full_text['xocs:serial-item']['article']['body']
        sections = sections['ce:sections']['ce:section']
        text = []
        for section in sections:
            for paragraph in section['ce:para']:
                   text.append(paragraph['#text'])

    def __repr__(self):
        return '<Article (Title=%s, id=%s)>' % (
                self.title.encode('utf8'), self.uid.encode('utf8'))

