import webapp2
import string
import cgi
import re
form1="""
<form method="post">
  <b>Enter some text to ROT13:</b>
  <br>
  <br>
  <textarea rows="6" cols="50" name="text">%(convertedText)s</textarea>
  <br>
  <input type="submit">
</form>
"""

form2= """
<form method="post">
  <b>Signup</b>
  <br>
  <br>
  <label>
    Username
    <input type="text" name="username" value="%(user)s">
    %(error_u)s
  </label>
  <br>
  <label>
    Password
    <input type="password" name="password">
    %(error_p)s
  </label>
  <br>
  <label>
    Verify Password
    <input type="password" name="verify">
    %(error_m)s
  </label>
  <br>
  <label>
    Email (optional)
    <input type="text" name="email" value="%(email)s">
    %(error_e)s
  </label>
  <br>
  <input type="submit">
</form>  
"""

class ROT13(webapp2.RequestHandler):
    def get(self):
        self.write_form()
    def post(self):
        text = self.request.get('text')
        if(text):
            text = process_text(text)
        self.write_form(text=text)
    
    def write_form(self, text=""):
        self.response.out.write(form1%{"convertedText": text})

class Signup(webapp2.RequestHandler):
    def get(self):
        self.write_form()
    def post(self):
        user = self.request.get('username')
        pass1 = self.request.get('password')
        pass2 = self.request.get('verify')
        email = self.request.get('email')
        valid_user = False
        valid_pw = False
        pw_match = True
        valid_email = True
        if(user):
            valid_user = self.valid_username(user)
        if(pass1):
            valid_pw = self.valid_pass(pass1)
            if(valid_pw):
                pw_match = pass1 == pass2
        if(email):
            valid_email = self.valid_email(email)

        if(valid_user and valid_pw and pw_match and valid_email):
            self.redirect("/Welcome?username=%s"%user)
        else:
            print user
            print valid_user
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
        self.response.out.write(form2%{"error_u":error_u,
                                       "error_p":error_p,
                                       "error_m":error_m,
                                       "error_e":error_e,
                                       "user":user,
                                       "email": email})
    def valid_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(username)
    def valid_pass(self, pw):
        PASS_RE = re.compile(r"^.{3,20}$")
        return PASS_RE.match(pw)
    def valid_email(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        return EMAIL_RE.match(email)

class Welcome(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Welcome %s!"%self.request.get('username'))

def process_text(text):
    #s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #trans = s[13:] + s[:13]
    #rot13 = string.maketrans(s + s.lower(), trans + trans.lower())
    #string.translate(text, rot13)
    text = text.encode("rot13")
    text = cgi.escape(text, quote=True)
    return text

application = webapp2.WSGIApplication([('/ROT13', ROT13),
                                       ('/Signup', Signup),
                                       ('/Welcome', Welcome)],debug=True)
