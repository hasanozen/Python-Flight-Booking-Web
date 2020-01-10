from datetime import datetime
from __main__ import db
from flask_user import  UserManager, UserMixin
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

	# User authentication information. The collation='NOCASE' is required
	# to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
	email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
	email_confirmed_at = db.Column(db.DateTime())
	password = db.Column(db.String(255), nullable=False, server_default='')

	# User information
	first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
	last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

	# Define the relationship to Role via UserRoles
	roles = db.relationship('Role', secondary='user_roles')



	def __repr__(self):
		return f"User('{self.email}','{self.password}'"

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class Points(db.Model):
	__tablename__ = 'points'
	id = db.Column(db.Integer(), primary_key=True)
	point = db.Column(db.Integer(), nullable=True)

# ucusların bulunduğu tablo
class Flight(db.Model):
	__tablename__ = 'flight'
	flight_id = db.Column(db.Integer, primary_key=True)
	airline_Name = db.Column(db.String(80), nullable=False)
	from_location = db.Column(db.String(20), nullable=False)
	to_location = db.Column(db.String(120), nullable=False)
	departure_time = db.Column(db.String(120), nullable=False)
	arrival_time = db.Column(db.String(120), nullable=False)
	depart_date = db.Column(db.String(120), nullable=True)
	total_seats = db.Column(db.Integer, nullable=False)
	status = db.Column(db.String(20), nullable=True)
# ucus detaylarının bulunduğu tablo


class Flight_Details(db.Model):
	__tablename__ = 'flight_details'
	flight_id = db.Column(db.Integer, db.ForeignKey('flight.flight_id'))
	flight_departure_date= db.Column(db.String(120), primary_key=True)
	price = db.Column(db.Integer, nullable=False)
	available_seats=db.Column(db.Integer, nullable=False)


class Ticket_Info(db.Model):
	__tablename__ = 'ticket_info'
	ticket_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	flight_id = db.Column(db.Integer, db.ForeignKey('flight.flight_id'))
	flight_departure_date = db.Column(db.String(120), db.ForeignKey('flight_details.flight_departure_date'))
	status= db.Column(db.String(20), nullable=False)
	idNo=db.Column(db.String(20), nullable=True)
	name=db.Column(db.String(120), nullable=True)
	lastname=db.Column(db.String(120), nullable=True)
	birthday = db.Column(db.String(120), nullable=True)
	mail=db.Column(db.String(120), nullable=True)
	phone = db.Column(db.String(120), nullable=True)


#bir takım işlemlerin yapılabilmesi için oluşturumuş bir class
class Yolcu():
	def __init__(self, sayi,id):
		self.kolcu=sayi
		self.id=id


engine = create_engine('sqlite:///Airway.sqlite')

Base.metadata.create_all(engine)