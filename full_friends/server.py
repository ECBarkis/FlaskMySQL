from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector

app = Flask( __name__ )
app.secret_key = 'sEcrEtK3y'
EMAIL_REGEX = re.compile( r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$' )
mysql = MySQLConnector( app, 'full_friends' )

@app.route( '/' )
def index():
	query = "SELECT * FROM friends"
	friends = mysql.query_db( query )
	return render_template( 'index.html', all_friends = friends )

@app.route( '/friends', methods = [ 'POST' ] )
def create():
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	if len( first ) < 2:
		flash( 'First name must be at least two characters' )
	elif len( last ) < 2:
		flash( 'Last name must be at least two characters' )
	elif len( email ) < 1:
		flash( 'Email can not be empty' )
	elif not EMAIL_REGEX.match( email ):
		flash( 'Invalid email format')
	else:
		query = "INSERT INTO friends ( first_name, last_name, email, created_at, updated_at ) VALUES ( :first, :last, :email, NOW(), NOW() )"
		data = {
			'first': first,
			'last': last,
			'email': email
		}
		mysql.query_db( query, data )
	return redirect( '/' )

@app.route( '/friends/<id>/edit' )
def edit(id):
	query = "SELECT * FROM friends WHERE id = :id"
	data = { 'id': id }
	friend = mysql.query_db( query, data )
	return render_template( 'edit.html', friends = friend )

@app.route( '/friends/<id>', methods = [ 'POST' ] )
def update(id):
	rf = request.form
	first = rf[ 'first_name' ]
	last = rf[ 'last_name' ]
	email = rf[ 'email' ]
	query = "UPDATE friends SET first_name = :first, last_name = :last, email = :email, updated_at = NOW() WHERE id = :id"
	data = {
		'first': first,
		'last': last,
		'email': email,
		'id': id
	}
	mysql.query_db( query, data )
	return redirect( '/' )

@app.route( '/friends/<id>/delete', methods = [ 'POST' ] )
def destroy(id):
	query = "DELETE FROM friends WHERE id = :id"
	data = { 'id': id }
	mysql.query_db( query, data )
	return redirect( '/' )

app.run( debug = True )