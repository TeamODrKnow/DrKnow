import os
import webapp2
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

#######################################################################
## Function to retrieve and render a template
def render_template(handler, templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)

#######################################################################
## Handles and loads index page
class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        login = users.create_login_url('/')
        logout = users.create_logout_url('/')

        template_values = {
        'login': login,
        'logout': logout,
        'user': user
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
    def post(self) :
        NewUser = UserModel()
        NewUser.fname = self.request.get('fname')
        NewUser.lname = self.request.get('lname')
        NewUser.put()
        self.redirect('/')


app = webapp2.WSGIApplication( [
    ('/', MainPage),
    ('/registerUser.html', RegisterUser),
    ('/userRegister', ProcessUser)
], debug=True)
