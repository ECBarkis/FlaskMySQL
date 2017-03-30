from flask import Flask, render_template, redirect, request, flash, session
import re
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt

app = Flask( __name__ )
bcrypt = Bcrypt( app )
app.secret_key = 'sEcrEtK3y'
EMAIL_REGEX = re.compile( r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$' )
mysql = MySQLConnector( app, 'login' )

@app.route( '/' )
def index():
	return render_template( 'index.html' )

@app.route( '/users', methods = [ 'POST' ] )
def create_user():
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	password = rf[ 'password' ]
	confirmation = rf[ 'confirmation' ]
	pw_hash = bcrypt.generate_password_hash( password )
	query = "INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) VALUES ( :first, :last, :email, :password, NOW(), NOW() )"
	data = {
		'first': first,
		'last': last,
		'email': email,
		'password': pw_hash,
	}
	if len( first ) < 2:
		flash( 'First name must be at least two characters' )
	elif len( last ) < 2:
		flash( 'Last name must be at least two characters' )
	elif not EMAIL_REGEX.match( email ):
		flash( 'Invalid email format')
	elif len( password ) < 8:
		flash( 'Password must be at least eight characters' )
	elif password != confirmation:
		flash( 'Password does not match password confirmation')
	else:
		mysql.query_db( query, data )
	return redirect( '/' )

@app.route( '/login', methods = [ 'POST' ] )
def login():
	rf = request.form
	email = rf[ 'email' ]
	password = rf[ 'password' ]
	user_query = "SELECT * FROM users where email = :email LIMIT 1"
	data = { 'email': email }
	user = mysql.query_db( user_query, data )
	if len( email ) < 1:
		flash( 'Email must be present' )
		return redirect( '/' )
	if bcrypt.check_password_hash( user[ 0 ][ 'password' ], password ):
		return 'Hello Login'
	else:
		flash( 'Could not login try again' )
		return redirect( '/' )

app.run( debug = True )