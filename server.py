from flask import Flask, render_template, request, redirect, flash, session
from pushbullet import PushBullet
from uuid import uuid4 as UUID
import os

# create the flask app
app = Flask(__name__)
app.secret_key = 'nice boat'

# store all the accounts in memory!
accounts = {}
auth_reqs = {}

def valid_request(required):
	return all(map(lambda x: x in request.form, required))

def get_pb_for_user(username):
	if username in accounts.keys():
		key = accounts[username]
		return PushBullet(key)
	return none

def is_logged_in():
	if 'auth_hash' in session:
		auth_hash = session['auth_hash']
		return auth_hash in auth_reqs.keys() and auth_reqs[auth_hash]
	return False

# show the home page
@app.route('/')
def root():
	if is_logged_in():
		flash('you are logged in as ' + session['username'])
	return render_template("index.html")

# create an account
@app.route('/create', methods=['POST'])
def create():
	if valid_request(['username', 'key']):
		username = request.form['username']
		key = request.form['key']
		if username not in accounts.keys():
			accounts[username] = key
			flash('created user ' + username)
		else:
			flash('user ' + username + ' already exists')
	else:
		flash('invalid request')	
	return redirect('/')	

# login
@app.route('/login', methods=['POST'])
def login():
	if request.form['username']:
		username = request.form['username']
		if username in accounts.keys():
			auth_hash = str(UUID())
			session['username'] = username
			session['auth_hash'] = auth_hash
			auth_reqs[auth_hash] = False

			pb = get_pb_for_user(username)
			success, push = pb.push_link('login as ' + username, 'fuwafuwa.co.uk:44544/auth?id=' + auth_hash)

			from time import sleep
			while not auth_reqs[auth_hash]:
				sleep(1)
	return redirect('/')

# authenticate
@app.route('/auth')
def authenticate():
	auth_hash = request.args.get('id')
	if auth_hash and auth_hash in auth_reqs.keys():
		auth_reqs[auth_hash] = True
		return 'authenticated'
	return 'nope'

# start the server
def run():
	app.run(debug=True, host='0.0.0.0', port=44544, threaded=True)

# if the script if being run directly start the server
if __name__ == '__main__':
	run()
