#!/usr/bin/env python


__author__ = 'jml168@pitt.edu (J. Matthew Landis)'


import httplib2
import logging
import os
import pickle
import webapp2
import jinja2

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache



PROJECT_NUMBER = '934763316754'

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
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

class MainHandler(webapp2.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    variables = {
        'url': decorator.authorize_url(),
        'has_credentials': decorator.has_credentials()
        }

    self.response.write(template.render(variables))


class AboutHandler(webapp2.RequestHandler):

  @decorator.oauth_required
  def get(self):
    try:
      http = decorator.http()
      user = service.people().get(userId='me').execute(http=http)
      text = 'Hello, %s!' % user['displayName']

      template = JINJA_ENVIRONMENT.get_template('templates/welcome.html')
      self.response.write(template.render({'text': text }))
    except client.AccessTokenRefreshError:
      self.redirect('/')

class EngineHandler(webapp2.RequestHandler):

	@bq_decorator.oauth_required
  	def get(self):
  		try:
  			http = bq_decorator.http()
  			temp_data = {}
  			queryData = {'query':'SELECT word FROM [publicdata:samples.shakespeare] LIMIT 1000'}
  			tableData = bigquery_service.jobs()
  			response = tableData.query(projectId=PROJECT_NUMBER,body=queryData).execute()
  			template = JINJA_ENVIRONMENT.get_template('templates/engine.html')
  			self.response.write(template.render({'response':response}))
  		except client.AccessTokenRefreshError:
  			self.redirect('/')


app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/about', AboutHandler),
     (decorator.callback_path, decorator.callback_handler()),
     (bq_decorator.callback_path, bq_decorator.callback_handler())
    ],
    debug=True)
