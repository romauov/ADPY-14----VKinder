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

# class MatchingUser(Base):
#     __tablename__ = 'matching_user'
#
#     matching_id = sq.Column(sq.Integer, primary_key=True)
#     first_name = sq.Column(sq.String)
#     last_name = sq.Column(sq.String)
#     age = sq.Column(sq.Integer)
#     dating_id =
#
# class Photos(Base):
#     photo_id =
#     matching_id =
#     photo_link =
#     likes_count =
#
# class BlacklistedUser(Base):
#     __tablename__ = 'matching_user'
#
#     matching_id = sq.Column(sq.Integer, primary_key=True)
#     first_name = sq.Column(sq.String)
#     last_name = sq.Column(sq.String)
#     age = sq.Column(sq.Integer)
#     dating_id =






if __name__ == '__main__':
    Base.metadata.create_all(engine)
