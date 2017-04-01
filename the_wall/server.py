from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt

app = Flask( __name__ )
bcrypt = Bcrypt( app )
app.secret_key = 'sEcrEtK3y'
EMAIL_REGEX = re.compile( r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$' )
mysql = MySQLConnector( app, 'wall' )

@app.route( '/' )
def index():
	return render_template( 'index.html' )

@app.route( '/register', methods = [ 'POST' ] )
def create_user():
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	password = rf[ 'password' ]
	confirmation = rf[ 'confirmation' ]
	if len( first ) < 1:
		flash( 'First name must be present' )
	elif len( last ) < 1:
		flash( 'Last name must be present')
	elif not EMAIL_REGEX.match( email ):
		flash( 'Invalid email address' )
	elif len( password ) < 7:
		flash( 'Password must have seven characters' )
	elif password != confirmation:
		flash( 'Password does not match password confirmation' )
	else:
		pw_hash = bcrypt.generate_password_hash( password )
		query = "INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) VALUES ( :first, :last, :email, :password, NOW(), NOW() )"
		data = {
			'first': first,
			'last': last,
			'email': email,
			'password': pw_hash
		}
		mysql.query_db( query, data )
		flash( 'You have been registered' )
	return redirect( '/' )

@app.route( '/login', methods = [ 'POST' ] )
def login():
	rf = request.form
	email = rf[ 'email' ]
	password = rf[ 'password' ]
	user_query = "SELECT * FROM users where email = :email LIMIT 1"
	data = { 'email': email }
	user = mysql.query_db( user_query, data )
	if not user:
		flash( 'No email matches a user')
		return redirect( '/' )
	if bcrypt.check_password_hash( user[ 0 ][ 'password' ], password ):
		session[ 'user' ] = user[ 0 ][ 'id' ]
		return redirect( '/wall' )
	else:
		flash( 'Password does not match' )
		return redirect( '/' )

@app.route( '/wall' )
def wall():
	user_query = "SELECT * FROM users WHERE id = :id LIMIT 1"
	user_data = { 'id': session[ 'user' ] }
	user = mysql.query_db( user_query, user_data )
	message_query = "SELECT * FROM users JOIN messages ON messages.user_id = users.id"
	message = mysql.query_db( message_query )
	comment_query = "SELECT * FROM comments JOIN users ON users.id = comments.user_id"
	comments = mysql.query_db( comment_query )
	return render_template( 'wall.html', users = user, messages = message, comments = comments )

@app.route( '/message/<id>', methods = [ 'POST' ] )
def create_message(id):
	rf = request.form
	content = rf[ 'content' ]
	query = "INSERT INTO messages ( content, created_at, updated_at, user_id ) VALUES ( :content, NOW(), NOW(), :id )"
	data = {
		'content': content,
		'id': id
	}
	mysql.query_db( query, data )
	return redirect( '/wall' )

@app.route( '/comment/<message>', methods = [ 'POST' ] )
def create_comment(message):
	rf = request.form
	content = rf[ 'content' ]
	query = "INSERT INTO comments ( content, created_at, updated_at, message_id, user_id ) VALUES ( :content, NOW(), NOW(), :message, :user )"
	data = {
		'content': rf[ 'content' ],
		'message': message,
		'user': session[ 'user' ]
	}
	mysql.query_db( query, data )
	return redirect( '/wall' )

@app.route( '/logout' )
def logout():
	session.pop( 'user' )
	return redirect( '/' )

app.run( debug = True )