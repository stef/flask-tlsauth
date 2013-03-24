#!/usr/bin/env python

# run with
# env/bin/uwsgi --socket 127.0.0.1:8080 --chdir $PWD/demo -pp $PWD -w tlsauth_wsgi -p 1 --virtualenv $PWD/env --py-autoreload 1

from flask import Flask, Response
import os
Flask.secret_key = 'zxcvzxcvz'
app = Flask(__name__)

from tlsauth import CertAuthority
import flask_tlsauth as tlsauth

ca=CertAuthority('/home/stef/tasks/tlsauth/CA/public/root.pem',
                 '/home/stef/tasks/tlsauth/CA/private/root.pem',
                 '/home/stef/tasks/tlsauth/CA/conf/serial',
                 '/home/stef/tasks/tlsauth/CA/dummy.pem',
                 'http://www.example.com/crl.pem',
                 '/home/stef/tasks/tlsauth/CA/incoming',
                 )

adminOs=['ctrlc','ctrlCA']
tlsauth.tlsauth_init(app, ca, groups=adminOs)

@app.route('/hello')
@tlsauth.tlsauth(groups=adminOs)
def hello():
    return Response("hello world")
