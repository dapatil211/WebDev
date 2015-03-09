import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **params):
        self.write(self.render_str(template, **params))

class FrontPage(Handler):
    def get(self):
        if(self.request.get("newPost")):
            self.redirect("/blog/newpost")
        else:
            posts = db.GqlQuery("select * from BlogEntry order by date desc")
            self.render("front_page.html", posts = posts)
class NewPost(Handler):
    def get(self):
        self.render("new_post.html", subject = "", content = "", error ="")
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if(subject and content):
            a = BlogEntry(subject = subject, content = content)
            a.put()
            self.redirect("/blog/%d"%a.key().id())
        else:
            self.render("new_post.html", subject = subject,
            content = content, error = "Please submit a subject and content please!")

class BlogPost(Handler):
    def get(self, blog_id):
        p = BlogEntry.get_by_id(int(blog_id))
        self.render("post.html", post=p)

class BlogEntry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    date = db.DateProperty(auto_now_add = True)

app = webapp2.WSGIApplication([('/blog', FrontPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/(\d+)', BlogPost)], 
                              debug = True)
