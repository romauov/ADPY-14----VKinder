import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db_adm_pass import db_pass, db_admin
import psycopg2


Base = declarative_base()

engine = sq.create_engine(f'postgresql+psycopg2://{db_admin}:{db_pass}@localhost:5432/vkinder_DB')
Session = sessionmaker(bind=engine)


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    bdate = sq.Column(sq.String)
    age_min = sq.Column(sq.Integer)
    age_max = sq.Column(sq.Integer)
    city_name = sq.Column(sq.String)
    city_id = sq.Column(sq.Integer)
    matchingusers = relationship('MatchingUser', secondary='dating_to_matching', back_populates='datinguser')
    blacklistedusers = relationship('BlacklistedUser', secondary='dating_to_blacklisted', back_populates='datinguser')

class MatchingUser(Base):
    __tablename__ = 'matchinguser'

    matching_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    dating_id = relationship(DatingUser)
    photos = relationship('Photos', secondary='matching_to_photos', back_populates='matchinguser')

class Photos(Base):
    __tablename__ = 'userphotos'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    matching_id = relationship(MatchingUser)
    photo_link = sq.Column(sq.String)
    likes_count = sq.Column(sq.Integer)

class BlacklistedUser(Base):
    __tablename__ = 'blacklisteduser'

    blacklisted_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    age = sq.Column(sq.Integer)
    dating_id = relationship(DatingUser)

dating_to_matching = sq.Table(
    'dating_to_matching', Base.metadata,
    sq.Column('dating_id', sq.Integer, sq.ForeignKey('datinguser.dating_id')),
    sq.Column('matching_id', sq.Integer, sq.ForeignKey('matchinguser.matching_id')),
)

matching_to_photos = sq.Table(
    'matching_to_photos', Base.metadata,
    sq.Column('matching_id', sq.Integer, sq.ForeignKey('matchinguser.matching_id')),
    sq.Column('photo_id'), sq.Integer, sq.ForeignKey('photos.photo_id'),
)

dating_to_blacklisted = sq.Table(
    'dating_to_matching', Base.metadata,
    sq.Column('dating_id', sq.Integer, sq.ForeignKey('datinguser.dating_id')),
    sq.Column('matching_id', sq.Integer, sq.ForeignKey('blacklisteduser.blacklisted_id')),
)






if __name__ == '__main__':
    Base.metadata.create_all(engine)
