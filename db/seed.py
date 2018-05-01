from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User_Customer, Message
from mimesis import Generic
import random
import pdb
# Creates connection with database
engine = create_engine(
    'postgresql://sms-admin:sms-admin-Password@localhost:5432/sms'
)
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()

# user = User(
#     email='someUser@gmail.com', password='password', phone='17328675309', username='SomeBusiness')
# session.add(user)
# session.commit()

# Create Customers
# customer = User_Customer(
#     name='Joe Doe',
#     phone='1800777777',
#     email=customeremail@gmail.com,)
#     user_id=1
# session.add(customer)
# session.commit()


# Create message
# message = Message(message_uui='dkdkd9303j3r93jfkdfdf0e9j309j09', user_id=db_session.query(
#     User).all()[0], customer_id=db_session.query(User_Customer).all()[0])
# session.add(message)
# session.commit()
#
# pdb.set_trace()
