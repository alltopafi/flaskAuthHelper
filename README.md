This is a python helper that I wrote to enable using LDAP groups and basic auth with python. 

This was greatly inspired from [Flask-BasicAuth-LDAP](https://pypi.org/project/Flask-BasicAuth-LDAP/) hopefully when I get some time I can clean this up and submit it. 

TODO: Allow for no group to be used and need to allow sub-search to be dynamic.

Example use:

```
from flask import Flask, jsonify
from ldapBasicAuthHelper import *
from ldap3 import Connection, Server
import pdb; pdb.set_trace()
from functools import update_wrapper


app = Flask(__name__)


app.config['LDAP_HOST'] = 'ldap://192.168.1.1'
app.config['LDAP_PORT'] = 389
app.config['LDAP_DOMAIN'] = 'dc=example,dc=org'
app.config['LDAP_READ_USER'] = 'cn=readonlyUser,dc=example,dc=org'
app.config['LDAP_READ_PSSWD'] = 'ReAdOnLy'

auth = LDAPBasicAuthHelper(app)

@auth.unauthorizedhandler 
def custom_unathorized_view(): 
    return jsonify({'message': 'Athorize first'}), 401

@app.route('/secret', methods=['GET'])
@auth.authenticateWithGroup('api_access_g')
def authenticated_view():
   return jsonify({'status': 'secret'})
'''
