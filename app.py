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
from helpers.helpers import setEnvironVariables
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

# Setup Flask-Security
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
    return render_template('/home/home.html')


"""--------------------------------------------------------------------------


                                    Views

 ----------------------------------------------------------------------------
"""


@app.route('/user/api-clients/')
@login_required
def ApiClients():
    clients = db_session.query(User_Api_Client).filter_by(
        user_id=current_user.id).all()
    return render_template('/apiClients/apiClients.html', clients=clients)


@app.route('/user/customers/')
@login_required
def Customers():
    customers = db_session.query(User_Customer).filter_by(
        user_id=current_user.id).all()
    return render_template('/customers/customers.html', customers=customers)


@app.route('/user/messages/')
@login_required
def SmsMessages():
    sms_messages = db_session.query(Message).filter_by(
        user_id=current_user.id).order_by(Message.id.desc()).all()
    # pdb.set_trace()
    return render_template('/messages/messages.html', sms_messages=sms_messages)


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
        try:
            db_session.commit()
            flash('%s was sucessfully added!' % request.form['name'])
            return redirect(url_for('apiClient'))
        except:
            print('some error could not save transaction, rolling back')
            db_session.rollback()
            db_session.commit()
    else:
        # pdb.set_trace()
        return render_template('/apiClients/apiClientNew.html')


@app.route('/user/customer/new', methods=['GET', 'POST'])
@login_required
def newCustomer():
    # This page will be for creating a new Customer
    if request.method == 'POST':

        newCustomer = User_Customer(
            name=request.form['name'], email=request.form['email'], phone=request.form['phone'], user_id=current_user.id, status="SUBSCRIBED")
        db_session.add(newCustomer)
        try:
            db_session.commit()
            flash('%s was sucessfully added!' % request.form['name'])
            return redirect(url_for('newCustomer'))
        except:
            print('some error could not save transaction, rolling back')
            db_session.rollback()
            db_session.commit()
    else:
        # pdb.set_trace()
        return render_template('/customers/newCustomer.html')


@app.route('/user/message/new', methods=['GET', 'POST'])
@login_required
def newMessage():
    try:
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

            # message_uuid = []
            # for i in destinationNumbers:
            #     message_uuid.append(datetime.datetime.now())
            # response = {'message_uuid': message_uuid}
            # uncomment below when using api
            for i, uuid in enumerate(response.message_uuid, 0):

                # uncomment below when not using api
                # for i, uuid in enumerate(response['message_uuid'], 0):
                newMessage = Message(
                    user_id=current_user.id, user_customer_id=int(request.form.getlist('customerSelect')[i]), message_uuid=uuid, message=request.form['message'], direction="outbound")
                db_session.add(newMessage)
                db_session.commit()
            flash('The message was sucessfully created!')
            return redirect(url_for('newMessage', customers=customers))
        else:
            return render_template('/messages/newMessage.html', customers=customers)
    except:
        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()
        flash('There was some errors and some of your messages my have Failed!')
        return render_template('/messages/newMessage.html', customers=customers)


"""--------------------------------------------------------------------------


                                    Edit

 ----------------------------------------------------------------------------
"""


@app.route('/user/api-client/<int:api_client_id>/edit', methods=['GET', 'POST'])
@login_required
def apiClientEdit(api_client_id):

    # pdb.set_trace()
    # this page will be for creating API Clients
    try:
        client = db_session.query(User_Api_Client).filter_by(id=api_client_id)
        if client.one():
            if request.method == 'POST':
                client.update({
                    "name": request.form['name'], "api_id": aes_encrypt(request.form['api_id']), "auth_id": aes_encrypt(request.form['auth_id'])})
                db_session.commit()
                flash('%s was sucessfully updated!' % request.form['name'])
                return redirect(url_for('apiClientEdit', api_client_id=api_client_id))

            else:
                # pdb.set_trace()
                apiClient = client.one()
                id = apiClient.id
                api_id = aes_decrypt(apiClient.api_id)
                auth_id = aes_decrypt(apiClient.auth_id)
                name = apiClient.name
                return render_template('/apiClients/apiClientEdit.html', id=id, api_id=api_id, auth_id=auth_id, clientName=name)

        else:
            flash('API Client Id %s not found!' % api_client_id)
            return render_template('/apiClients/apiClients.html')
    except:
        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()
        flash('API Client Id %s not found!' % api_client_id)
        return render_template('/apiClients/apiClients.html')


@app.route('/user/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def customerEdit(customer_id):

    # pdb.set_trace()
    # this page will be for creating API Clients
    try:
        customer = db_session.query(User_Customer).filter_by(id=customer_id)
        if customer.first():
            if request.method == 'POST':
                customer.update({
                    "name": request.form['customerName'], "phone": request.form['customerPhone'], "email": request.form['customerEmail'], 'status': request.form['customerStatus']})

                db_session.commit()
                flash('%s was sucessfully updated!' %
                      request.form['customerName'])
                # return redirect(url_for('customerEdit', customer_id=customer.one().id))
                return redirect(url_for('Customers', customers=db_session.query(User_Customer).filter_by(
                    user_id=current_user.id).all()))
            else:
                # pdb.set_trace()

                return render_template('/customers/customerEdit.html', customer=customer.one())

        else:
            flash('Customer with Id %s not found!' % customer_id)
            # return render_template('/customers/customers.html')
            return redirect(url_for('Customers', customers=db_session.query(User_Customer).filter_by(
                user_id=current_user.id).all()))
    except:
        db_session.rollback()
        db_session.commit()
        flash('Something went wrong, rolling back transactions!')
        return redirect(url_for('Customers', customers=db_session.query(User_Customer).filter_by(
            user_id=current_user.id).all()))


"""--------------------------------------------------------------------------


                                    Delete

 ----------------------------------------------------------------------------
"""


@app.route('/user/api-client/<int:api_client_id>/delete', methods=['GET', 'POST'])
@login_required
def apiClientDelete(api_client_id):

    try:
        client = db_session.query(User_Api_Client).get(api_client_id)
        db_session.delete(client)
        db_session.commit()
        flash("%s was sucessfully Deleted!" % client.name)
        clients = db_session.query(User_Api_Client).filter_by(
            user_id=current_user.id).all()
        return render_template('/apiClients/apiClients.html', clients=clients)
    except:
        flash("Something went wrong rolling back transaction!" % client.name)
        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()


@app.route('/user/customer/<int:customer_id>/delete', methods=['GET', 'POST'])
@login_required
def customerDelete(customer_id):
    try:
        customer = db_session.query(User_Customer).get(customer_id)
        db_session.delete(customer)
        db_session.commit()
        flash("%s was sucessfully Deleted!" % customer.name)
        customers = db_session.query(User_Customer).filter_by(
            user_id=current_user.id).all()
        return render_template('/customers/customers.html', customers=customers)
    except:

        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()
        flash("Encountered some errors, rolling back transactions")
        customers = db_session.query(User_Customer).filter_by(
            user_id=current_user.id).all()
        return render_template('/customers/customers.html', customers=customers)


@app.route('/message/<int:message_id>/delete', methods=['GET', 'POST'])
@login_required
def messageDelete(message_id):

    message = db_session.query(Message).get(message_id)
    # pdb.set_trace()
    try:
        db_session.delete(message)
        db_session.commit()
        flash("%s was sucessfully Deleted!" % message.message)
        sms_messages = db_session.query(Message).filter_by(
            user_id=current_user.id).order_by(Message.id.desc()).all()
        return render_template('/messages/messages.html', sms_messages=sms_messages)
    except:
        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()
        flash("Something went wrong, rolling back transaction!")
        sms_messages = db_session.query(Message).filter_by(
            user_id=current_user.id).order_by(Message.id.desc()).all()
        return render_template('/messages/messages.html', sms_messages=sms_messages)


"""--------------------------------------------------------------------------


                                    API

 ----------------------------------------------------------------------------
"""


@app.route('/message/status', methods=['POST'])
def statusMessage():
    try:
        message = db_session.query(Message).filter_by(
            message_uuid=request.form["MessageUUID"])
        message.update({"status": request.form["Status"],
                        "units": request.form["Units"],
                        "total_rate": request.form["TotalRate"],
                        "total_amount": request.form["TotalAmount"],
                        "message_time": datetime.datetime.now()})
        db_session.commit()
        print(message.one().serialize)
        return jsonify(message.one().serialize)
    except:
        print('some error could not save transaction, rolling back')
        db_session.rollback()
        db_session.commit()


@app.route('/message/inbound/new', methods=['POST'])
def newInboundMessage():
    """ This page will be for all inbound messages, check if customer exists if so, check content of message if == "UNSUBSCRIBE", change user status.
    If customer does not exist add to database.
    """
    try:
        print ('requestform', request.form)
        tel = str(request.form['To'])
        print (tel)
        print("type %s" % type(tel))
        print ("session %s" % db_session)
        print ("User %s" % User)
        outro = db_session.query(User).all()[0].phone
        print ("outro", outro)
        teste = db_session.query(User).filter(User.phone == '17323605788')
        print('teste %s,%s' % (teste, teste.first().phone))
        first = db_session.query(User).filter_by(phone='17323605788')
        print ("first %s" % first)
        print ("first_phone %s" % first.one().phone)
        print("type(%s) = %s - type of To=%s %s, tel=to== %s" % (first.phone, type(phone),
                                                                 tel, type(tel), tel == first.phone))
        print('first=%s' % first.first().phone)
        user = db_session.query(User).filter_by(
            phone=tel).one()

        if user:
            customer = db_session.query(
                User_Customer).filter_by(phone=request.form['From']).first()
            if customer:
                if request.form['Text'] == "UNSUBSCRIBE":
                    customer.status = "UNSUBSCRIBED"
            else:
                customer = User_Customer(
                    name='UNKNOWN', phone=request.form['From'], user_id=user.id, status="SUBSCRIBED")
                db_session.add(customer)
                db_session.commit()

            newMessage = Message(
                user_id=user.id, user_customer_id=customer.id, message_uuid=request.form['MessageUUID'], message=request.form['Text'], direction="inbound", status="RECEIVED",
                units=request.form["Units"],
                total_rate=request.form["TotalRate"],
                total_amount=request.form["TotalAmount"], error_code="200", message_time=datetime.datetime.now())

            db_session.add(newMessage)
            db_session.commit()
            return jsonify(newMessage.serialize)
    except:
        print('Something went wrong, rolling back transaction!')
        db_session.rollback()
        db_session.commit()


@app.route('/users/JSON/')
@login_required
def usersJSON():
    users = db_session.query(User).all()
    return jsonify(Users=[i.serialize for i in users])


@app.route('/user/<int:user_id>/customers/JSON/')
@login_required
def userCustomersJSON(user_id):
    # pdb.set_trace()
    user = db_session.query(User).filter_by(id=user_id).one()
    customers = db_session.query(
        User_Customer).filter_by(user_id=user_id).all()
    return jsonify(User=[i.serialize for i in user], User_Customer=[i.serialize for i in customers])


@app.route('/messages/JSON')
@login_required
def messagesJSON():
    messages = db_session.query(Message).all()
    return jsonify(Message=[i.serialize for i in messages])


@app.route('/user/api-clients/JSON')
@login_required
def apiClientsJSON():
    apiClients = db_session.query(User_Api_Client).all()
    return jsonify(User_Api_Client=[i.serialize for i in apiClients])


if __name__ == '__main__':
    # app.run("", port=3000)
    app.run()
