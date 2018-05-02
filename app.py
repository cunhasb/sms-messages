from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore, current_user
from flask_security.forms import RegisterForm
from flask_mail import Mail
from celery import Celery
from wtforms import StringField
from wtforms.validators import InputRequired
from werkzeug.contrib.fixers import ProxyFix
from sqlalchemy.orm import sessionmaker
from db.database import db_session, init_db
from db.models import Base, User, User_Api_Client, User_Customer, Message, Role
# python -m pip install pycrypto otherwise would not work
from Crypto.Cipher import AES
import binascii
import datetime
import pdb
import math

# Create app

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SECURITY_PASSWORD_SALT'] = 'super_secret_password_salt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# app.config['MAIL_SERVER'] = 'smtp.gmail.com.'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'your@mail.com'
# app.config['MAIL_PASSWORD'] = 'password'

# Setup Flask-Security


def aes_encrypt(data):
    cipher = AES.new('super_secret_key')
    data = data + (" " * (16 - (len(data) % 16)))
    return binascii.hexlify(cipher.encrypt(data)).decode('ascii')


def aes_decrypt(data):
    cipher = AES.new('super_secret_key')
    return cipher.decrypt(binascii.unhexlify(data)).rstrip().decode('ascii')


class ExtendedRegisterForm(RegisterForm):

    username = StringField(
        "Username",  [InputRequired("Please enter your username.")])
    phone = StringField(
        "Phone Number",  [InputRequired("Please enter your phone number.")])


user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm)
# pdb.set_trace()
current_user
# mail = Mail(app)

# Create a user to test with


@app.before_first_request
def create_user():
    init_db()


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
# @login_required
def home():
    # this is the landing page
    return render_template('home.html', current_user=current_user)


@app.route('/users/JSON/')
# @login_required
def usersJSON():
    users = db_session.query(User).all()
    return jsonify(Users=[i.serialize for i in users])


@app.route('/user/<int:user_id>/customers/JSON/')
@login_required
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


@app.route('/user/api-clients/JSON')
# @login_required
def apiClientsJSON():
    apiClients = db_session.query(User_Api_Client).all()
    return jsonify(User_Api_Client=[i.serialize for i in apiClients])


@app.route('/user/api-client/new', methods=['GET', 'POST'])
@login_required
def apiClient():

    # pdb.set_trace()
    # this page will be for creating API Clients
    if request.method == 'POST':
        # pdb.set_trace()
        # strings to be encrypted need to be multiples of 16
        # obj = AES.new('super_secret_key', AES.MODE_CBC,
        #               'super_secret_IV_')
        # paddedApiId = obj.encrypt(("{0:%s}" % (int(math.ceil(
        #     len(request.form['api_id']) / 16.0) * 16))).format(request.form['api_id']))
        # paddedAuthId = obj.encrypt(("{0:%s}" % (int(math.ceil(
        #     len(request.form['auth_id']) / 16.0) * 16))).format(request.form['auth_id']))
        # pdb.set_trace()

        newClient = User_Api_Client(
            name=request.form['name'], api_id=aes_encrypt(request.form['api_id']), auth_id=aes_encrypt(request.form['auth_id']), user_id=current_user.id)

        print('new_client=', newClient.api_id, newClient.auth_id)
        db_session.add(newClient)
        db_session.commit()
        flash('%s was sucessfully added!' % request.form['name'])
        return redirect(url_for('apiClient'))
    else:
        # pdb.set_trace()
        return render_template('apiClient.html')


@app.route('/user/customer/new', methods=['GET', 'POST'])
@login_required
def newCustomer():
    # This page will be for creating a new Customer
    if request.method == 'POST':

        newCustomer = User_Customer(
            name=request.form['name'], email=request.form['email'], phone=request.form['phone'], user_id=current_user.id)
        db_session.add(newCustomer)
        db_session.commit()
        flash('%s was sucessfully added!' % request.form['name'])
        return redirect(url_for('newCustomer', current_user=current_user))
    else:
        # pdb.set_trace()
        return render_template('newCustomer.html', current_user=current_user)


@app.route('/user/message/new', methods=['GET', 'POST'])
@login_required
def newMessage():
    # This page will be for creating a new Customer
    customers = db_session.query(
        User_Customer).filter_by(user_id=current_user.id).all()
    print ('customers', len(customers))
    if request.method == 'POST':
        pdb.set_trace()
        apiClient = db_session.query(User_Api_Client).filter_by(
            user_id=current_user.id).one()

        message_uuid = datetime.datetime.now()
        # pdb.set_trace()
        newMessage = Message(
            user_id=current_user.id, user_customer_id=int(request.form['customer_id']), message_uuid=message_uuid, message=request.form['message'])
        db_session.add(newMessage)
        db_session.commit()
        flash('The message was sucessfully created!')
        return redirect(url_for('newMessage', customers=customers, current_user=current_user))
    else:
        # pdb.set_trace()
        return render_template('newMessage.html', customers=customers, current_user=current_user)


if __name__ == '__main__':
    app.run("", port=3000)
