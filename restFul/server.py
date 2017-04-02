from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt

app = Flask( __name__ )
bcrypt = Bcrypt( app )
app.secret_key = 'sEcrEtK3y'
EMAIL_REGEX = re.compile( r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$' )
mysql = MySQLConnector( app, 'restful' )

@app.route( '/users' )
def index():
	user_query = "SELECT * FROM users"
	user = mysql.query_db( user_query )
	return render_template( 'index.html', users = user )

@app.route( '/users', methods = [ 'POST' ] )
def create():
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	password = rf[ 'password' ]
	confirmation = rf[ 'confirmation' ]
	if len( first ) < 2:
		flash( 'First name must be at least two characters' )
		return redirect( '/users/new' )
	if len( last ) < 2:
		flash( 'Last name must be at least two characters' )
		return redirect( '/users/new' )
	if len( password ) < 8:
		flash( 'Password must be at least eight characters' )
		return redirect( '/users/new' )
	if not EMAIL_REGEX.match( email ):
		flash( 'Invalid email' )
		return redirect( '/users/new' )
	if password != confirmation:
		flash( 'Password does not match password confirmation' )
		return redirect( '/users/new' )
	pw_hash = bcrypt.generate_password_hash( password )
	query = "INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) VALUES ( :first, :last, :email, :password, NOW(), NOW() )"
	data = {
		'first': first,
		'last': last,
		'email': email,
		'password': pw_hash
	}
	mysql.query_db( query, data )
	return redirect( '/users' )

@app.route( '/users/new' )
def new():
	return render_template( 'create.html' )

@app.route( '/users/<id>' )
def show(id):
	user_query = "SELECT * FROM users WHERE id = :id LIMIT 1"
	user_data = { 'id': id }
	user = mysql.query_db( user_query, user_data )
	return render_template( 'show.html', users = user[ 0 ] )

@app.route( '/users/<id>/edit' )
def edit(id):
	user_query = "SELECT * FROM users WHERE id = :id LIMIT 1"
	user_data = { 'id': id }
	user = mysql.query_db( user_query, user_data )
	return render_template( 'edit.html', users = user[ 0 ] )

@app.route( '/users/<id>', methods = [ 'POST' ] )
def update(id):
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	query = "UPDATE users SET first_name = :first, last_name = :last, email = :email, updated_at = NOW() WHERE id = :id"
	data = {
	'first': first,
	'last': last,
	'email': email,
	'id': id
	}
	mysql.query_db( query, data )
	return redirect( '/users' )

@app.route( '/users/<id>/destroy' )
def destroy(id):
	query_delete = "DELETE FROM users WHERE id = :id"
	data = { 'id': id }
	mysql.query_db( query_delete, data )
	return redirect( '/users' )

app.run( debug = True )