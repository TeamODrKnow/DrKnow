import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

#######################################################################
## Function to retrieve and render a template
def render_template(handler, templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)


class MainPage(webapp2.RequestHandler):
    def get(self):
        render_template(self, 'index.html', {})

class RegisterUser(webapp2.RequestHandler):
    def get(self):
        render_template(self, 'registerUser.html', {})

class UserModel(ndb.Model) :
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()

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
