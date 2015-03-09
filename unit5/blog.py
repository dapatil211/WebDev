import ROT13
import os
import dbclass
import webapp2
import jinja2
import utility
from google.appengine.ext import db
import json

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

class FrontPageJSON(Handler):
    def get(self):
        posts = db.GqlQuery("select * from BlogEntry order by date desc")
        self.response.headers.add_header('Content-Type',
                str('application/json; charset=UTF-8'))
        self.write(json.dumps([{'content': str(p.content),
                     'date': p.date.strftime("%b %d, %Y"),
                     'subject':str(p.subject)} for p in posts]))

class NewPost(Handler):
    def get(self):
        self.render("new_post.html", subject = "", content = "", error ="")
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if(subject and content):
            a = dbclass.BlogEntry(subject = subject, content = content)
            a.put()
            self.redirect("/blog/%d"%a.key().id())
        else:
            self.render("new_post.html", subject = subject,
            content = content, 
            error = "Please submit a subject and content please!")

class BlogPost(Handler):
    def get(self, blog_id):
        p = dbclass.BlogEntry.get_by_id(int(blog_id))
        self.render("post.html", post=p)

class BlogPostJSON(Handler):
    def get(self, blog_id):
        p = dbclass.BlogEntry.get_by_id(int(blog_id))
        self.response.headers.add_header('Content-Type',
                str('application/json; charset=UTF-8'))
        self.write(json.dumps({'content': str(p.content),
                    'date': p.date.strftime("%b %d, %Y"),
                    'subject':str(p.subject)}))

class Signup(Handler):
    def get(self):
        cookie = self.request.cookies.get('user_id')
        if cookie and utility.check_secure_val(cookie):
            self.redirect("/blog/Welcome")
        else:
            self.write_form()
    def post(self):
        cookie = self.request.cookies.get('user_id')
        if cookie and utility.check_secure_val(cookie):
            self.redirect("/blog/Welcome")
        else:
            user = self.request.get('username')
            pass1 = self.request.get('password')
            pass2 = self.request.get('verify')
            email = self.request.get('email')
            valid_user = False
            valid_pw = False
            pw_match = True
            valid_email = True
            if(user):
                valid_user = utility.valid_username(user)
            if(pass1):
                valid_pw = utility.valid_pass(pass1)
                if(valid_pw):
                    pw_match = pass1 == pass2
            if(email):
                valid_email = utility.valid_email(email)

            if(valid_user and valid_pw and pw_match and valid_email):
                self.response.headers.add_header('Set-Cookie', 
                        str("user_id=%s; Path=/"%utility.make_secure_val(user)))
                p = utility.make_pw_hash(user, pass1)
                print p
                a = dbclass.User(user = user,
                                 pw = p)
                print a.pw
                if(email):
                    a.email = email
                a.put()
                self.redirect("/blog/Welcome")
            else:
                self.write_form(vu = valid_user, vp = valid_pw, pm = pw_match, 
                        ve = valid_email, user = user, email = email)
    def write_form(self, vu = True, vp = True, pm = True, ve =
            True, user = "", email = ""):
        error_u = ""
        error_p = ""
        error_m = ""
        error_e = ""
        if(not vu):
            error_u="That's not a valid username"
        if(not vp):
            error_p="That wasn't a valid password"
        if(not pm):
            error_m="Your passwords didn't match"
        if(not ve):
            error_e="That's not a valid email"
        self.render("Signup.html", error_u=error_u, 
                                   error_p=error_p,
                                   error_m=error_m,
                                   error_e=error_e, 
                                   user=user, 
                                   email=email)

class Welcome(Handler):
    def get(self):
        cookie = self.request.cookies.get('user_id')
        if(cookie):
            cookie_val = utility.check_secure_val(cookie)
            if(cookie_val):
                self.render("Welcome.html", user = cookie_val)
            else:
                self.redirect("/blog/signup")
        else:
            self.redirect("/blog/signup")
        
class Login(Handler):
    def get(self):
        cookie = self.request.cookies.get('user_id')
        if(cookie):
            cookie_val = utility.check_secure_val(cookie)
            if(cookie_val):
                self.render("Welcome.html", user = cookie_val)
            else:
                self.render("login.html", error="")
        else:
            self.render("login.html", error="")
    def post(self):
        username = self.request.get('username')
        pw = self.request.get('password')
        user = db.GqlQuery("select * from User where user=:1", username)
        print user[0].pw
        if user:
            p = user[0].pw
            if utility.valid_pw(username, pw, p):
                self.response.headers.add_header('Set-Cookie',
                    str("user_id=%s; Path=/"%utility.make_secure_val(username)))
                self.redirect('/blog/Welcome')
            else:
                self.render("login.html", error = "Invalid login")
        else:
            self.render("login.html", error = "Invalid login")
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', "user_id=; Path=/")
        self.redirect('/blog/signup')

app = webapp2.WSGIApplication([('/blog/?', FrontPage),
                               ('/blog/.json/?', FrontPageJSON),
                               ('/blog/newpost/?', NewPost),
                               ('/blog/(\d+)/?', BlogPost),
                               ('/blog/(\d+).json/?', BlogPostJSON),
                               ('/blog/signup/?', Signup),
                               ('/blog/Welcome/?', Welcome), 
                               ('/blog/login/?', Login),
                               ('/blog/logout/?', Logout)], 
                              debug = True)
