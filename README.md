# SMS - Messenger

Built using Python and Flask with Postgresql database


Send and receive messages using Plivo API. 

Crud functionality

Multi-User

Add/Remove/Edit API Clients (Plivo Information)
Add/Remove/Edit Customers (Contacts to send and receive Messages)
Add/Delete Messages (Messages Sent and Received)

Application uses Plivo API, Does not work if you don't have your own API and Auth keys.

Flow:

1 - Login or Register yourself.
2 - Create one Client API - containing your api key and auth code . You can get a free Account https://manage.plivo.com/accounts/login/?next=/dashboard/ , documentation is found here https://developers.plivo.com/. In order to send messages in the USA, Plivo requires a Plivo Number. Using free account will send messages only to international numbers but will receive all messages coming to your account.
3 - Create a customer to send messages. 
4 - Create a message to send message. 
5 - All messages (sent and received) are displayed in the message page, Whenever someone sends you a message and his number is not in your database it will create a new customer with that number.

hosted site 
https://messenger-sms.herokuapp.com/
