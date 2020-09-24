import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db_adm_pass import db_pass, db_admin
# import psycopg2


Base = declarative_base()

engine = sq.create_engine(f'postgresql+psycopg2://{db_admin}:{db_pass}@localhost:5432/vkinder_DB')
Session = sessionmaker(bind=engine)


class DatingUser(Base):
    __tablename__ = 'DatingUser'

    dating_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    bdate = sq.Column(sq.String)
    age_min = sq.Column(sq.Integer)
    age_max = sq.Column(sq.Integer)
    city_name = sq.Column(sq.String)
    city_id = sq.Column(sq.Integer)
    matchingusers = relationship('MatchingUser', backref='DatingUser')
    blacklistedusers = relationship('BlacklistedUser', backref='DatingUser')

class MatchingUser(Base):
    __tablename__ = 'MatchingUser'

    matching_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    id_dater = sq.Column(sq.Integer,sq.ForeignKey('DatingUser.dating_id'))
    photos = relationship('Photos', backref='MatchingUser')

class Photos(Base):
    __tablename__ = 'Photos'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    id_matcher = sq.Column(sq.Integer, sq.ForeignKey('MatchingUser.matching_id'))
    photo_link = sq.Column(sq.String)
    likes_count = sq.Column(sq.Integer)

class BlacklistedUser(Base):
    __tablename__ = 'BlacklistedUser'

    blacklisted_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    id_dater = sq.Column(sq.Integer,sq.ForeignKey('DatingUser.dating_id'))


# if __name__ == '__main__':
#     Base.metadata.create_all(engine)
