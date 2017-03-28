from flask import Flask, render_template, redirect, request, session, flash
import re
from mysqlconnection import MySQLConnector

app = Flask( __name__ )
app.secret_key = 'S3cretK3y'
EMAIL_REGEX = re.compile( r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$' )
mysql = MySQLConnector( app, 'email' )

@app.route( '/' )
def index():
	return render_template( 'index.html' )

@app.route( '/create', methods = [ 'POST' ] )
def create():
	rf = request.form
	if not EMAIL_REGEX.match( rf[ 'email' ] ):
		flash( u'Email is not valid!', 'error' )
		return redirect( '/' )
	query = "INSERT INTO emails ( email, created_at, updated_at ) VALUES ( :email, NOW(), NOW() )"
	data = {
		'email': rf[ 'email' ]
	}
	mysql.query_db( query, data )
	return redirect( '/success' )

@app.route( '/success' )
def success():
	query = "SELECT * FROM emails"
	emails = mysql.query_db( query )
	query = "SELECT * FROM emails ORDER BY id DESC"
	email = mysql.query_db( query )
	return render_template( 'success.html', all_emails = emails, email = email )

@app.route( '/delete/<id>', methods = [ 'POST' ] )
def delete(id):
	query = "DELETE FROM emails WHERE id = :id"
	data = { 'id': id }
	mysql.query_db( query, data )
	return redirect( '/success' )

app.run( debug = True )