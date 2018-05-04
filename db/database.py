from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
# from flask.ext.sqlalchemy import SQLAlchemy
from helpers.helpers import secrets
import pdb

'''psql
postgres=# CREATE DATABASE sms;
CREATE DATABASE
postgres=# CREATE USER sms-admin WITH PASSWORD 'password';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE sms TO SMS-ADMIN;
GRANT'''


# engine = create_engine(connect(secrets('dbUser'), secrets(
# 'dbPassword'), "localhost", 5432, "sms"))
db_session = scoped_session(sessionmaker(autocommit=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    '''import all modules here that might define models so that they will be registered properly on the metadata. Otherwise you will have to import them first before calling init_db()'''

    import db.models
    Base.metadata.create_all(bind=engine)


def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object.
    We connect with the help of PostgreSQL URL
    postgresql://sms-admin:sms-admin-Password@localhost:5432/sms'''

    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
