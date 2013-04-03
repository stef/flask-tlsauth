#!/usr/bin/env python

# run with
# env/bin/uwsgi --socket 127.0.0.1:8080 --chdir $PWD/demo -pp $PWD -w tlsauth_wsgi -p 1 --virtualenv $PWD/env --py-autoreload 1
# also create a ca in ../../x509-ca - for more info see tlsauth README

from flask import Flask, Response
import os
app = Flask(__name__)
app.secret_key = 'zxcvzxcvz'
#app.debug = True

from tlsauth import CertAuthority
import flask_tlsauth as tlsauth

ca=CertAuthority('../../x509-ca')

app.debug = True
adminOs=['CA admins']
tlsauth.tlsauth_init(app, ca, groups=adminOs)

@app.route('/hello')
@tlsauth.tlsauth(groups=adminOs)
def hello():
    return Response("hello world")
