from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore, current_user
from flask_mail import Mail
from celery import Celery
from werkzeug.contrib.fixers import ProxyFix
from sqlalchemy.orm import sessionmaker
from db.database import db_session, init_db
from db.models import Base, User, User_Customer, Message, Role
import pdb

# Create app

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SECURITY_PASSWORD_SALT'] = 'super_secret_password_salt'
app.config['SECURITY_REGISTRABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# app.config['MAIL_SERVER'] = 'smtp.gmail.com.'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'your@mail.com'
# app.config['MAIL_PASSWORD'] = 'password'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)
current_user
# pdb.set_trace()
# mail = Mail(app)

# Create a user to test with


@app.before_first_request
def create_user():
    init_db()

    # user_datastore.create_user(
    #     email='yetanotherUser@gmail.com', password='password', phone='1733934673309', username='yetanothercompanyname')
    # db_session.commit()
    # customer = User_Customer(
    #     name='Peter3', email='peter3@gmail.com', phone='444556667', user_id=4)
    # db_session.add(customer)
    # db_session.commit()
    #
    # message = Message(message_uuid="kd447474Fkdkjdkjhdjd89jkljoihjrrk90909948484dj0fdf9d0fd9f0",
    #                   user_id=4, user_customer_id=11)
    #
    # db_session.add(message)
    # db_session.commit()
# pdb.set_trace()
# Views
# API's Endpoints (GET request only)
# Setup the task
# @celery.task
# def send_security_email(**kwargs):
#     # Use the Flask-Mail extension instance to send the incoming ``msg`` parameter
#     # which is an instance of `flask_mail.Message`
#     mail.send(Message(**kwargs))
#
#
# @security.send_mail_task
# def delay_security_email(msg):
#     pdb.set_trace()
#     mail.send(recipients=msg.recipients, subject=msg.subject, body=msg.body)
# @celery.task
# def send_security_email(**kwargs):
#     mail.send(Message(**kwargs))
# @security.send_mail_task
# def delay_security_email(msg):
#     mail.send(subject=msg.subject, sender=msg.sender,
#                               recipients=msg.recipients, body=msg.body)
# @security.context_processor
# def security_context_processor(*arg):


@app.route('/')
@app.route('/users/JSON/')
# @login_required
def usersJSON():
    users = db_session.query(User).all()
    return jsonify(Users=[i.serialize for i in users])


@app.route('/user/<int:user_id>/customers/JSON/')
# @login_required
def userCustomersJSON(user_id):
    # pdb.set_trace()
    user = db_session.query(User).filter_by(id=user_id)
    customers = db_session.query(
        User_Customer).filter_by(user_id=user_id).all()
    return jsonify(User=[i.serialize for i in user], User_Customer=[i.serialize for i in customers])


@app.route('/messages/JSON')
# @login_required
def messagesJSON():
    messages = db_session.query(Message).all()
    return jsonify(Message=[i.serialize for i in messages])


if __name__ == '__main__':
    app.run("", port=3000)
