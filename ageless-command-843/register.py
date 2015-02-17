import os
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import ndb

def render_template(handler, templatename, templatevalues) :
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)
  
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

    

app = webapp2.WSGIApplication([
  ('/userRegister', ProcessUser) 
], debug = True)