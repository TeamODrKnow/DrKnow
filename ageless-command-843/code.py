import os
import webapp2
import tweepy
import sys
import pika
import json
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

#######################################################################
#get your own twitter credentials at dev.twitter.com
consumer_key = "9xNrmD6hE0xnRSYdZt5t0XT0B"
consumer_secret = "kperqjklvPhBCVvHI96aZIfJu5w1DHI2BZoNMdBEvBPfmuZIYG"
access_token = "46501499-cijYvv9ixtQKHLSiLt9QaRtcmWeEKvvGZK5s6ukw7"
access_token_secret = "D127XCAN02BPb0ZtcreCG6dpBJyiiLCeD6ckS2MgdHqwG"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


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
    def post(self) :
        NewUser = UserModel()
        NewUser.fname = self.request.get('fname')
        NewUser.lname = self.request.get('lname')
        NewUser.put()
        self.redirect('/')

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        #setup rabbitMQ Connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = connection.channel()

        #set max queue size
        args = {"x-max-length": 2000}

        self.channel.queue_declare(queue='twitter_topic_feed', arguments=args)

    def on_status(self, status):
        print status.text, "\n"

        data = {}
        data['text'] = status.text
        data['created_at'] = time.mktime(status.created_at.timetuple())
        data['geo'] = status.geo
        data['source'] = status.source

        #queue the tweet
        self.channel.basic_publish(exchange='',
                                    routing_key='twitter_topic_feed',
                                    body=json.dumps(data))

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))
sapi.filter(track=['pittsburgh'])

app = webapp2.WSGIApplication( [
    ('/', MainPage),
    ('/registerUser.html', RegisterUser),
    ('/userRegister', ProcessUser),
    ('/engine', CustomStreamListener)
], debug=True)
