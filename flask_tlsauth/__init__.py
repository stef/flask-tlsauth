#!/usr/bin/env python

from flask import request, Response, render_template, redirect
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
from tlsauth import todn, gencert, mailsigned, load
import os, datetime, jinja2
BASEPATH = os.path.dirname(os.path.abspath(__file__))

def tlsauth(unauth=None, groups=None):
    """ (FLASK) decorator letting execution pass if TLS authenticated
        and if given certs Organization is in groups.

        if TLS authentication fails execution is diverted to unauth,
        which per default returns 403
    """
    if not unauth:
        def unauth():
            return Response("Forbidden",403)
    def decor(func):
        def wrapped(*args,**kwargs):
            if request.environ['verified']=="SUCCESS" and (not groups or todn(request.environ['dn']).get('O') in groups):
                return func(*args,**kwargs)
            return unauth(*args,**kwargs)
        return wrapped
    return decor

class UserForm(Form):
    """ (FLASK) simple registration WTForm
    """
    name = TextField('Name')
    email = TextField('Email')
    org = TextField('Organization')

class CSRForm(Form):
    """ (FLASK) even simpler CSR submission WTForm
    """
    csr = TextAreaField('Certificate Signing Request')

def renderUserForm(ca):
    """ (FLASK) form handles user registration requests.
        This is the web-based way to do this irresponsibly.
    """
    def wrapped():
        form = UserForm()
        if form.validate_on_submit():
            return Response(
                gencert(str(form.name.data),
                        str(form.email.data),
                        str(form.org.data),
                        ca),
                mimetype="application/x-pkcs12")
        return render_template('register.html', form=form)
    return wrapped

def renderCSRForm(ca, blindsign=False, scrutinizer=None):
    """ (FLASK) form handles CSR submissions.
        blindsign disables reviewing by authorized personel, and enables automatic signing.
        scrutinizer is a function returning true if allowed to be signed.
    """
    def wrapped():
        form = CSRForm()
        if form.validate_on_submit():
            if blindsign:
                if not scrutinizer or scrutinizer(str(form.csr.data)):
                    return Response(ca.signcsr(str(form.csr.data)),
                                    mimetype="text/plain")
            else:
                ca.submit(str(form.csr.data))
                return Response("Thank you. If all goes well you should soon "
                                "receive your signed certificate.")
        return render_template('certify.html', form=form)
    return wrapped

def renderCert(ca):
    """ provides the CA root cert
    """
    def wrapped():
        return Response(ca._pub, mimetype="text/plain")
    return wrapped

def certify(ca, groups=None):
    """ provides facility for users belonging to `groups` to sign incoming CSRs
    """
    def wrapped(id):
        err=authenticated(groups)
        if err: return err
        path=ca._incoming+'/'+request.path.split('/')[3]
        print "certifying", path
        cert=ca.signcsr(load(path))
        mailsigned([cert])
        os.unlink(path)
        return redirect('/tlsauth/csrs/')
    return wrapped

def reject(ca, groups=None):
    """ provides facility for users belonging to `groups` to reject incoming CSRs
    """
    def wrapped(id):
        err=authenticated(groups)
        if err: return err
        path=ca._incoming+'/'+request.path.split('/')[3]
        os.unlink(path)
        return redirect('/tlsauth/csrs/')
    return wrapped

def authenticated(groups):
    """ (FLASK) helper function to check if user is authenticated and in a given group.
    """
    if not request.environ['verified']=="SUCCESS" or (groups and todn(request.environ['dn']).get('O') not in groups):
        return Response("Forbidden",403)

def showcsrs(ca,groups=None):
    """ (FLASK) authenticated view list of submitted CSRs
    """
    def wrapped():
        try:
            err=authenticated(groups)
            if err: return err
            return render_template('csrs.html',
                                   certs=[(todn(cert.get_subject()),
                                           datetime.datetime.fromtimestamp(os.stat(path).st_mtime),
                                           os.path.basename(path))
                                          for cert, path
                                          in ca.incoming()])
        except:
            import traceback
            print traceback.format_exc()
    return wrapped

def testAuth():
    """ test if you are TLS authenticated
        mountpoint: /tlsauth/test/
    """
    return Response(request.environ['verified'] + "<br />" + request.environ['dn'])

def tlsauth_init(app, ca, groups=None):
    """ automatically register routes for flask
    """
    app.add_url_rule('/tlsauth/register/', 'register', renderUserForm(ca), methods=("GET", "POST"))
    app.add_url_rule('/tlsauth/certify/', 'certify', renderCSRForm(ca, blindsign=False), methods=("GET", "POST"))
    app.add_url_rule('/tlsauth/cert/', 'cert', renderCert(ca))
    app.add_url_rule('/tlsauth/csrs/', 'csrs', showcsrs(ca, groups=groups))
    app.add_url_rule('/tlsauth/sign/<string:id>', 'sign', certify(ca, groups=groups))
    app.add_url_rule('/tlsauth/reject/<string:id>', 'reject', reject(ca, groups=groups))
    app.add_url_rule('/tlsauth/test/', 'test', testAuth)

    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(BASEPATH+'/templates'),
        ])
