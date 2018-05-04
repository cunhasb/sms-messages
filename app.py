from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore, current_user
from flask_security.forms import RegisterForm
from flask_heroku import Heroku
from flask_mail import Mail
from celery import Celery
from wtforms import StringField
from wtforms.validators import InputRequired
from werkzeug.contrib.fixers import ProxyFix
from sqlalchemy.orm import sessionmaker
from db.database import db_session, init_db
from db.models import Base, User, User_Api_Client, User_Customer, Message, Role
from helpers.helpers import secrets
# from flask.ext.sqlalchemy import SQLAlchemy
# python -m pip install pycrypto otherwise would not work
from Crypto.Cipher import AES
import binascii
import datetime
import pdb
import plivo
import os

# Create app

app = Flask(__name__)
app.config['DEBUG'] = True
# app.config['SECRET_KEY'] = secrets('secret')
# app.config['SECURITY_PASSWORD_SALT'] = secrets('salt')
app.config['SECRET_KEY'] = os.environ['SECRET']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SALT']

app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# app.config['MAIL_SERVER'] = secrets('mailServer')
# app.config['MAIL_PORT'] = secrets(mailPort)
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = secrets('mailUsername')
# app.config['MAIL_PASSWORD'] = secrets('mailPassword')

# Setup Flask-Security
heroku = Heroku(app)


def aes_encrypt(data):
    # cipher = AES.new(secrets('salt'))
    cipher = AES.new(os.environ['SALT'])

    data = data + (" " * (16 - (len(data) % 16)))
    return binascii.hexlify(cipher.encrypt(data)).decode('ascii')


def aes_decrypt(data):
    # cipher = AES.new(secrets('salt'))
    cipher = AES.new(os.environ['SALT'])
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


# Landing Page
@app.route('/')
# @login_required
def home():
    # this is the landing page
    return render_template('home.html', current_user=current_user)


"""--------------------------------------------------------------------------


                                    Views

 ----------------------------------------------------------------------------
"""


@app.route('/user/api-clients/')
@login_required
def ApiClients():
    clients = db_session.query(User_Api_Client).filter_by(
        user_id=current_user.id).all()
    return render_template('apiClients.html', clients=clients)


@app.route('/user/customers/')
@login_required
def Customers():
    customers = db_session.query(User_Customer).filter_by(
        user_id=current_user.id).all()
    return render_template('customers.html', customers=customers)


@app.route('/user/messages/')
@login_required
def SmsMessages():
    sms_messages = db_session.query(Message).filter_by(
        user_id=current_user.id).order_by(Message.id.desc()).all()
    # pdb.set_trace()
    return render_template('messages.html', sms_messages=sms_messages)


"""--------------------------------------------------------------------------


                                    Create

 ----------------------------------------------------------------------------
"""


@app.route('/user/api-client/new', methods=['GET', 'POST'])
@login_required
def apiClient():

    # pdb.set_trace()
    # this page will be for creating API Clients
    if request.method == 'POST':

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
            name=request.form['name'], email=request.form['email'], phone=request.form['phone'], user_id=current_user.id, status="SUBSCRIBED")
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

    if request.method == 'POST':
        apiClient = db_session.query(User_Api_Client).filter_by(
            user_id=current_user.id).all()[0]
        destinationNumbers = list(map(lambda x: db_session.query(User_Customer).filter_by(
            id=int(x)).one().phone, request.form.getlist('customerSelect')))

        # Commented out to not make unnecessary api calls
        client = plivo.RestClient(
            auth_id=aes_decrypt(apiClient.api_id), auth_token=aes_decrypt(apiClient.auth_id))
        response = client.messages.create(
            src=current_user.phone,
            dst="<".join(destinationNumbers),
            text=request.form['message'],
            url="https://sms-messeger.herokuapp.com/message/status")

        # pdb.set_trace()

        # message_uuid = []
        # for i in destinationNumbers:
        #     message_uuid.append(datetime.datetime.now())
        # pdb.set_trace()
        # response = {'message_uuid': message_uuid}
        # uncomment below when using api
        for i, uuid in enumerate(response.message_uuid, 0):
            # for i, uuid in enumerate(response['message_uuid'], 0):
            newMessage = Message(
                user_id=current_user.id, user_customer_id=int(request.form.getlist('customerSelect')[i]), message_uuid=uuid, message=request.form['message'], direction="outbound")
            db_session.add(newMessage)
            db_session.commit()
        flash('The message was sucessfully created!')
        return redirect(url_for('newMessage', customers=customers, current_user=current_user))
    else:
        # pdb.set_trace()
        return render_template('newMessage.html', customers=customers, current_user=current_user)


"""--------------------------------------------------------------------------


                                    API

 ----------------------------------------------------------------------------
"""


@app.route('/message/status', methods=['POST'])
def statusMessage():
    print (list(request.form))
    message = db_session.query(Message).filter_by(
        message_uuid == request.form["MessageUUID"]).one()

    message(status=request.form["Status"],
            units=request.form["Units"],
            total_rate=request.form["TotalRate"],
            total_amount=request.form["TotalAmount"])
    db_session.commit()
    return jsonify(message.serialize)


@app.route('/message/inbound/new', methods=['POST'])
def newInboundMessage():
    """ This page will be for all inbound messages, check if customer exists if so, check content of message if == "UNSUBSCRIBE", change user status.
    If customer does not exist add to database.
    """
    print ('requestform', request.form)
    # pdb.set_trace()
    user = db_session.query(User).filter_by(phone=request.form['To'])

    if user:
        customer = db_session.query(
            User_Customer).filter_by(phone == request.form['From']).one()
        if customer:
            if request.form['Text'] == "UNSUBSCRIBE":
                customer.status = "UNSUBSCRIBED"
        else:
            customer = User_Customer(
                name='UNKNOWN', phone=request.form['From'], user_id=user.id, status="SUBSCRIBED")
            db_session.add(customer)
            db_session.commit()

        newMessage = Message(
            user_id=user.id, user_customer_id=customer.id, message_uuid=request.form['MessageUUID'], message=request.form['Text'], direction="INBOUND", status="RECEIVED",
            units=request.form["Units"],
            total_rate=request.form["TotalRate"],
            total_amount=request.form["TotalAmount"], error_code="200")

        db_session.add(newMessage)
        db_session.commit()

        return jsonify(newMessage.serialize)
    return jsonify({"error": '400'})


@app.route('/users/JSON/')
# @login_required
def usersJSON():
    users = db_session.query(User).all()
    return jsonify(Users=[i.serialize for i in users])


@app.route('/user/<int:user_id>/customers/JSON/')
@login_required
def userCustomersJSON(user_id):
    # pdb.set_trace()
    user = db_session.query(User).filter_by(id == user_id).one()
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


if __name__ == '__main__':
    # app.run("", port=3000)
    app.run()
