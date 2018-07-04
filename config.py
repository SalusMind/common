import json
from functools import wraps

from flask import session
from flask import redirect

from sparkpost import SparkPost
from pymongo import MongoClient


data = None

with open("~/secret.json", 'r') as json_file:
    data = json.loads(json_file.read())

APP_NAME = data['app_name']
DEBUG = True
SECRET_KEY = APP_NAME

client = MongoClient()
db = client[APP_NAME]

sp = SparkPost(data['sparkpost_key'])


class g:
    def __init__(self):
        self.bcrypt = None


class Errors:
    def __init__(self):
        self.status = False

    def custom(self, message):
        return {'status': self.status, 'message': message}

    def invalid_request(self):
        return self.custom('Invalid request parameters.')

    def credentials_invalid(self):
        return self.custom('The username or password incorrect.')
    
    def confirm_email(self):
        return self.custom('A confirmation email has been sent to '+email+'. You must verify before signing in.')    

    def missing_parameters(self):
        return self.custom('Please fill all fields.')
    
    def user_suspended(self):
        return self.custom('User account is suspended. Contact support@salusmind.com for more information.')
    
    def user_exists(self, email):
        return self.custom('User account with email '+email+' already exists.')


class Success:
    def __init__(self):
        self.status = True
    
    def custom(self, message):
        return {'status': self.status, 'message': message}

    def confirmation(self):
        return self.custom('Email verification successful.')



def send_confirmation_email(fname, email, confirm_key):
    return sp.transmissions.send(
        use_sandbox=False,
        recipients=[email],
        html='''
        <p>Hey '''+fname+''',</p>
        <p>
            You are recieving this email because you have signed up 
            to <a href="https://salusmind.com">Salus Mind</a>, a mental health monitoring service.<br><br>
            Before you can get started, you must confirm your email using the following link:<br>
            <a href="https://salusmind.com/api/user/confirm/'''+email+'''/'''+confirm_key+'''">Confirm Email Address</a>
         <p>
         <p>
            Thanks,<br>
            The Salus Mind Team
         </p>
	 <p>
            <small>
                P.S. This email was automatically generated. Contact <a href="mailto:support@salusmind.com">support@salusmind.com</a> 
                for any questions, comments, issues, or concerns.
            </small>
            <br>
            <small>P.S.S. If you did not sign up for this service, please disregard this email.</small>
         </p>

        ''',
        from_email='hello@salusmind.com',
        subject='Welcome to Salus Mind'
    )



def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        else:
            user = db.users.find_one({'email': session['user']['email']})
            user['_id'] = str(user['_id'])
            session['user'] = user
        return f(*args, **kwargs)
    return decorated


def non_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' in session:
            return redirect('/profile')
        return f(*args, **kwargs)
    return decorated


