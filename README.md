Lokun
=======

Record is the bookeeping system. It recieves payments and keeps track of what
users are allowed to connect and which are not. It hold the little customer 
data we keep (no other information is stored by us about our customers). 

Python packages needed
---------------------
 * json
 * sqlite3
 * bottle
 * BeautifulSoup
 * quopri
 * pycrypto

Dependencies from apt:
-----------------------------
 * python
 * python-pip
 * nsis 
 * openssl 
 * python-dev
 * build-essentials

DalPay crypto protocol
======

This protocol follows the Encrypt-Then-MAC principle and the main objective 
for implementing this protocol is to prevent disclosure of the username to
DalPay (or any other payment processor for that matter), since DalPay have 
the name, address and card number of a customer. 

When a user initiates a DalPay transaction, a message is placed in the `user1` 
parameter sent to dalpay from `www.lokun.is`. This parameter is then included 
in the callback that is sent to api.lokun.is. The message follows the following
 protocol:

     AES_ENCRYPT(Base64("Username$Nonce"), key) $ Nonce $ IV $ HMAC


The password from DalPay is compared, as it is the only provided mechanism
to be sure the message orignated from DalPay. This protocol does nothing to 
prevent false replay messages from a user. Thus, it does not protect Lokun from
a user potentially scamming a free VPN connection, but it protects users from
DalPay, if they were served an injunction. 

