import datetime
from flask import Flask
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import  UserManager, UserMixin
from flask_login import LoginManager
from functools import wraps
import datetime as datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ConfigClass(object):
    """ Flask application config """
   
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
    
    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Airway.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings 
    # #USER_ENABLE_EMAIL=True ise bu ayarları yapın. Google güvenlik ayarları bu işlemi yapmanıza izin vermeyebilir.
    #Detaylı bilgiyi https://support.google.com/accounts/answer/6010255?p=lsa_blocked&hl=en-GB&visit_id=636759033269131098-410976990&rd=1 dan edinebilirsiniz. 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'xyz@gmail.com' # gmail adresinizi girin
    MAIL_PASSWORD = 'sifre' # gmail şifrenizi girin
    MAIL_DEFAULT_SENDER = '"MyApp" <xyz@gmail.com>'

    # Flask-User settings
    USER_APP_NAME = "Alışveriş Sitesi"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

# Create Flask app load app.config
app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)
engine = create_engine('sqlite:///Airway.sqlite')
connection=engine.connect()
Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


from models import *

#login_manager tanımlanmasıve kullanıcı id alma fonksiyonu
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Initialize Flask-BabelEx
babel = Babel(app)
# Initialize Flask-SQLAlchemy
@babel.localeselector
def get_locale():
   translations = [str(translation) for translation in babel.list_translations()]
#   return request.accept_languages.best_match(translations)
# @babel.localeselector
#def get_locale():
#   if request.args.get('lang'):
#       session['lang'] = request.args.get('lang')
#       return session.get('lang', 'tr')



# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!

# Define the Role data-model

# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

# Create all database tables
db.create_all()

# Create 'member@example.com' user with no roles
if not User.query.filter(User.email == 'member@example.com').first():
    user = User(
        email='member@example.com',
        email_confirmed_at=datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    db.session.add(user)
    db.session.commit()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(
        email='admin@example.com',
        email_confirmed_at=datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()

# giriş yapılmasının gerekliliğini kontrol eden fonksiyon
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not current_user.is_authenticated:
			flash('önce giriş yapmalısınız')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

# giriş yapan kullanıcının admin olup olmadığının kontrol edilmesi
def roles_required(*role_names):
	def wrapper(view_function):
		@wraps(view_function)
		def decorator(*args, **kwargs):
			if not current_user.is_authenticated:
				flash('önce giriş yapmalısınız')
				return render_template('signin.html')
			if not current_user.has_roles(*role_names):
				flash('bu sayfayı görme yetkiniz yok')
				return render_template('index.html')
			return view_function(*args, **kwargs)
		return decorator
	return wrapper


# The Home page is accessible to anyone

from routes import *




if __name__ == '__main__':
	app.run(debug=True)