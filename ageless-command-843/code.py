import os
import webapp2

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


app = webapp2.WSGIApplication( [
    ('/', MainPage)
], debug=True)
