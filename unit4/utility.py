import secret
import hmac
import hashlib
import string
import random
import re
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def hash_str(s):
    return hmac.new(secret.cookie_secret, s).hexdigest()

def check_secure_val(h):
    x = h.split('|')
    if h == make_secure_val(x[0]):
        return x[0]

def make_salt():
    return "".join(random.choice(string.letters) for x in range(5))

def make_pw_hash(name, pw):
    salt = make_salt()
    ha = "%s,%s" % (hashlib.sha256(name+pw+salt).hexdigest(), salt)
    return ha

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    print h
    ha = "%s,%s" % (hashlib.sha256(name+pw+salt).hexdigest(), salt)
    print ha
    return ha == h

def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)
def valid_pass(pw):
    PASS_RE = re.compile(r"^.{3,20}$")
    return PASS_RE.match(pw)
def valid_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    return EMAIL_RE.match(email)

