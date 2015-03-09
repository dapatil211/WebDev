from google.appengine.ext import db
class BlogEntry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    date = db.DateProperty(auto_now_add = True)

class User(db.Model):
    user = db.StringProperty(required = True)
    pw = db.StringProperty(required = True)
    email = db.StringProperty()

