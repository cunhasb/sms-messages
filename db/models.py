from db.database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, ForeignKey, String, Integer
import pdb


# models

class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    email = Column(String(255), unique=True)
    phone = Column(String(14), nullable=False, unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    current_login_ip = Column(String(100))
    last_login_ip = Column(String(100))
    current_login_at = Column(String(100))
    login_count = Column(Integer())
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'password': self.password

        }


class User_Api_Client(Base):
    __tablename__ = 'user_api_client'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    api_id = Column(String(255))
    auth_id = Column(String(255))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship(User, single_parent=True)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'api_id': self.api_id,
            'auth_id': self.auth_id
        }


class User_Customer(Base):
    __tablename__ = 'user_customer'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    phone = Column(String(14), nullable=False, unique=True)
    email = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship(User, single_parent=True)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'user_id': self.user_id,

        }


class Message(Base):

    __tablename__ = 'message'
    id = Column(Integer(), primary_key=True)
    message_uuid = Column(String(255), unique=True)
    message = Column(String())
    direction = Column(String(10))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user_customer_id = Column(
        Integer, ForeignKey('user_customer.id', ondelete='CASCADE'))

    customer = relationship(
        "User_Customer", primaryjoin="and_(User_Customer.id == foreign(Message.user_customer_id),""User_Customer.user_id==Message.user_id)")

    @property
    def serialize(self):
        # Returns object data in easily serializeable information
        return{
            'id': self.id,
            'message_uuid': self.message_uuid,
            'user_id': self.user_id,
            'customer_id': self.user_customer_id,
            'message': self.message,
            'direction': self.direction

        }
