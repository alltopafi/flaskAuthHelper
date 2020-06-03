# -*- coding: utf-8 -*-
import os
from functools import wraps

from flask import g, jsonify, request
from ldap3 import Connection, Server
from ldap3.core.exceptions import LDAPBindError, LDAPPasswordIsMandatoryError
from pprint import pprint

from ldap3.utils.log import set_library_log_detail_level, OFF, BASIC, NETWORK, EXTENDED

set_library_log_detail_level(EXTENDED)

class LDAPBasicAuthHelper:
    def __init__(self, app=None, host=None, port=None, domain=None):
        if app is not None:
            self.init_app(app, host=host, port=port, domain=domain)
        else:
            self.app = None

    def init_app(self, app, host=None, port=None, domain=None):
        self.app = app
        self.host = host
        self.port = port
        self.domain = domain
        self._unauthorizedfunc = None

    def authenticate(self, group):
        auth = request.authorization
        if auth and auth.type == 'basic':
            login, password = auth.username, auth.password
            try:
                server = Server(self.app.config['LDAP_HOST'], port=self.app.config['LDAP_PORT'])

                conn = Connection(
                    server, auto_bind=True, user=self.app.config['LDAP_READ_USER'], password=self.app.config['LDAP_READ_PSSWD']
                )
                conn.search('cn='+ login + ',ou=User,' + self.app.config['LDAP_DOMAIN'], '(&(ou=cn=' + group +')(userPassword=' + password + '))')

                if conn.entries:
                    return True
                else:
                    return jsonify({'Error':'must login first'}), 401

            except (LDAPPasswordIsMandatoryError, LDAPBindError):
                return jsonify({'error':'LDAPPASSWPRD or Ldap bind error with connection to ldap server'})
        else:
            return jsonify({'Error':'Only Basic Auth is supported.'}), 401

    def unauthorizedhandler(self, route):
        self._unauthorizedfunc = route

    def challenge(self):
        if self._unauthorizedfunc:
            return self._unauthorizedfunc()
        return (
            jsonify(
                {
                    'status': 'error',
                    'message': 'Invalid username/password specified'
                }
            ), 401
        )

    def required(self, route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            if self.authenticate('test'):
                return route(*args, **kwargs)
            return self.challenge()
        return wrapper

    def authenticateWithGroup(self, group='default'):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                authResult = self.authenticate(group)
                if authResult is True:
                    return f(*args, **kwargs)
                return authResult  
            return wrapped
        return decorator
