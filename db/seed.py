from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, User_Customer, Message
from mimesis import Generic
import random
import pdb
# Creates connection with database
engine = create_engine(
    'postgresql://sms:sms-admin-Password@localhost:5432/sms'
)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

pdb.set_trace()
# session.add(user)
