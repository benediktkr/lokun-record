lokun-record
=======

This is `record`. It gets it's name as it is the "book-keeper" for
[Lokun](https://lokun.is). It does a lot of things; authorizes or denies users access
to VPN servers, recieves payments, holds the little customer data we have (no other
information is stored by us about our users).

![Lokun](logo.png)

We believe in free software and thus `record` is licensed as AGPL. 

Python packages needed
---------------------
 * `json`
 * `sqlite3`
 * `bottle`
 * `BeautifulSoup`
 * `quopri`
 * `pycrypto`
 * `webtest`
 * `netaddr`
 * `fdfgen`

Dependencies from apt:
-----------------------------
 * `python`
 * `python-pip`
 * `nsis`
 * `openssl` 
 * `python-dev`
 * `build-essentials`
 * `pdftk` 

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

This is done to ensure that a 3-rd party handling payments doesn't have the 
information required to associate card details with a Lokun username.

Other parts
===

Do note that this project depends on other parts of Lokun that are not included
on github. These are `keycontrol` and `reikningar`. 

Maintainers 
====

Main: Benedikt Kristinsson <benedikt@lokun.is>

Karl Emil Karlsson <kalli@lokun.is>
