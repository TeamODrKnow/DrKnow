import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

#######################################################################
## Function to retrieve and render a template

var isLoggedIn = 0;

def render_template(handler, templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)


class MainPage(webapp2.RequestHandler):
    def get(self):
        if isLoggedIn == 0
            render_template(self, 'index.html', {})
        else

            render_template(self, 'indexRegistered.html', {})

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
        isLoggedIn = 1;
        self.redirect('/')


app = webapp2.WSGIApplication( [
    ('/', MainPage),
    ('/registerUser.html', RegisterUser),
    ('/userRegister', ProcessUser)
], debug=True)
