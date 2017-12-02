from flask import Flask, render_template, session, request, url_for, redirect, flash
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
import os

app = Flask(__name__)
app.config[ 'SECRET_KEY' ] = os.urandom(32)
socketio = SocketIO(app)
chat_rooms = {}

'''------------------ views ------------------'''
#index page allowing POST request for users to create and/or join a room
@app.route('/', methods=['GET', 'POST'])
def index():
	session['chat_user'] = ''
	session['chat_room'] = ''

	if request.method == 'POST':
		session['chat_user'] = request.form['chat_user']
		session['chat_room'] = request.form['chat_room']

		# flashes error message if there is either no user or chat room provided
		if session['chat_user'] == '' or session['chat_room'] == '':
			flash('Enter a Username and a Chat Room to enter.')
		else:
			if session['chat_room'] not in chat_rooms:
				chat_rooms[session['chat_room']] = 0
			return redirect(url_for('chat', room=session['chat_room']))

	return render_template('index.html', chat_rooms=chat_rooms)

#renders ta template for a chatroom that the user has created
@app.route('/chat/<room>', methods=['GET', 'POST'])
def chat(room):
	name = session['chat_user']
	return render_template('chat.html', name=name, room=room)
'''------------------ ----- ------------------'''

'''------------------ websocket events ------------------'''
#debug tool to show that someone has connected
@socketio.on('client_connected')
def handle_client_connect_event(json):
	print('*************************NEW USER CONNECTED*************************')

#event that shows user has joined the room upon creating/entering a room
@socketio.on('join')
def handle_join_room(json):
	print(chat_rooms[json['room']])
	chat_rooms[json['room']] += 1
	join_room(json['room'])
	print('************************* ' + json['user'] + ' joins room: ' + json['room'] + ' *************************')
	socketio.emit('status', {'msg': json['user'] + ' has entered the room.'}, room=json['room'])

#event that has user leave room upon user's request
@socketio.on('leave')
def handle_leave_room(json):
	chat_rooms[json['room']] -= 1
	session['chat_room'] = ''
	leave_room(json['room'])
	print('************************* ' + json['user'] + ' leaves room: ' + json['room'] + ' *************************')
	socketio.emit('status', {'msg': json['user'] + ' has left the room.'}, room=json['room'])

#event that closes room upon user's request
@socketio.on('close')
def handle_close_room(json):
	del chat_rooms[json['room']]
	print('************************* ' + json['user'] + ' closes room: ' + json['room'] + ' *************************')
	socketio.emit('status', {'msg': json['user'] + ' has closed the room'}, room=json['room'])
	close_room(json['room'])

#sends message from user to user's current room
@socketio.on('send_message')
def handle_send_message(json):
	print('************************* ' + 'message received: ' + str( json ) + ' *************************')
	socketio.emit('response', { 'username': json['username'], 'message': json['message'] }, room=json['room'])
'''------------------ ---------------- ------------------'''

if __name__ == '__main__':
    #socketio.run(app, host='0.0.0.0', port=80)
    socketio.run(app, debug=True)