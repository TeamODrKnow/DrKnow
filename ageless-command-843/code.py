#!/usr/bin/env python

__author__ = 'jml168@pitt.edu (J. Matthew Landis)'


import os
import logging
import pickle
import webapp2
import time
import httplib2

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
#######################################################################

PROJECT_NUMBER = '934763316754'

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """""
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

http = httplib2.Http(memcache)
service = discovery.build("plus", "v1", http=http)
bigquery_service = discovery.build("bigquery","v2", http=http)

decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

bq_decorator = appengine.oauth2decorator_from_clientsecrets(
  CLIENT_SECRETS,
  scope='https://www.googleapis.com/auth/bigquery',
  message=MISSING_CLIENT_SECRETS_MESSAGE)

## Function to retrieve and render a template
def render_template(handler, templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)

#######################################################################
## Handles and loads index page
class MainPage(webapp2.RequestHandler):

    def get(self):
        nickname = "null"
        email = "null"
        user = users.get_current_user()
        login = users.create_login_url('/')
        logout = users.create_logout_url('/')
        os.system("python stream.py")
        if user != None:
            nickname = user.nickname()
            email = user.email()

        template_values = {
        'login': login,
        'logout': logout,
        'user': user,
        'nickname': nickname,
        'email': email
        }
        render_template(self, 'index.html', template_values)

#######################################################################
## Handle user info and profile
class RegisterUser(webapp2.RequestHandler):
    def get(self):
        render_template(self, 'registerUser.html', {})

#######################################################################
## Establish user objects
class UserModel(ndb.Model) :
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()

#######################################################################
## process user objects
class ProcessUser(webapp2.RequestHandler) :

    @bq_decorator.oauth_required
    http = decorator.http()
    def post(self) :
        NewUser = UserModel()
        NewUser.fname = self.request.get('fname')
        NewUser.lname = self.request.get('lname')
        NewUser.put()
        self.redirect('/')

#######################################################################
## process user objects
class EngineHandler(webapp2.RequestHandler) :

    @bq_decorator.oauth_required
    def get(self) :
        http = bq_decorator.http()
        temp_data = {}
        temp_path = 'templates/engine.html'
        queryData = {'query':'SELECT word FROM [rtda.tweets] LIMIT 1000'}
        tableData = bigquery_service.jobs()
        response = tableData.query(projectId=PROJECT_NUMBER,body=queryData).execute()
        self.response.out.write(response)

app = webapp2.WSGIApplication( [
    ('/', MainPage),
    ('/registerUser.html', RegisterUser),
    ('/userRegister', ProcessUser),
    ('/engine', EngineHandler),
    (decorator.callback_path, decorator.callback_handler()),
    (bq_decorator.callback_path, bq_decorator.callback_handler())
], debug=True)
