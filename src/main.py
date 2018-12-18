from flask import jsonify
from flask import Flask, Response
from flask import request
from flask_cors import CORS
import pymongo
from pymongo import MongoClient
import json
from bson import ObjectId
from profile_setup import *
from room import *
from moderator import *
# from music_clustering import *

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

@app.route('/')
def index():
	# client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
	# db = client.server
	# user = db.users.find_one({'id' : '12152580425'})
	return('index')

@app.route('/example/')
def example():
	return jsonify(
		{ 
		'salas': [
			{
				'id': 1,
				'nome': 'Churrasco casa do ariel',
				'id_anfitriao': 'U1'
			},
			{
				'id': 2,
				'nome': 'Ouvindo no CEE',
				'id_anfitriao': 'U2'
			},
			{
				'id': 3,
				'nome': 'Ano novo na praia',
				'id_anfitriao': 'U3'
			}
		]
	})

## USER SETUP

@app.route('/setup_user/', methods = ['POST'])
def setup_user():
	data = request.json
	#print(data['token'])
	user_id = startup_user(data['token'])
	return jsonify({
		'success': True,
		'user_id': user_id
		})

@app.route('/check_user/', methods = ['POST'])
def check_user():
	data = request.json
	#print(data['token'])
	(success, user_id, finished_loading) = check_user_status(data['id'])
	return jsonify({
		'success': success,
		'user_id': user_id,		
		'finished_loading': finished_loading
		})

## ROOM CONTROL

@app.route('/room_create/', methods = ['POST'])
def room_create():
	data = request.json
	(success, room) = room_room_create(data['owner_id'], data['room_name'])
	user_db = db.users.find_one({'id' : data['owner_id']}, {'id': 1, 'name': 1, 'image': 1, 'finished_loading': 1})
	image = None
	if(user_db != None):
		image = user_db['image']
	return jsonify({
		'success': success,
		'room': room,
		'owner_image': image
		})

@app.route('/room_add_user/', methods = ['POST'])
def room_add_user():
	data = request.json
	(success, room) = room_room_add_user(data['user_id'], data['room_id'])
	return jsonify({
		'success': success,
		'room': room
		})

@app.route('/room_remove_user/', methods = ['POST'])
def room_remove_user():
	data = request.json
	(success, room) = room_room_remove_user(data['user_id'], data['room_id'])
	return jsonify({
		'success': success,
		'room': room
		})

@app.route('/room_get/', methods = ['POST'])
def room_get():
	data = request.json
	(success, room, users) = room_room_get(data['room_id'])
	return jsonify({
		'success': success,
		'room': room,
		'users': users
		})

@app.route('/room_get_list/', methods = ['GET', 'POST'])
def room_get_list():
	data = request.json
	limit = 20
	if(data != None and data != {}):
		limit = data['limit']
	print(data)
	print(limit)
	(success, tuples_room_user) = room_room_get_list(limit)
	return jsonify({
		'success': success,
		'room_list': tuples_room_user
		})

## Playlists:


@app.route('/playlist_create/', methods = ['POST'])
def playlist_create():
	data = request.json
	(success, playlist) = moderator_generate_playlist(data['room_id'])	
	return jsonify({
		'success': success,
		'playlist': playlist
		})

@app.route('/playlist_get/', methods = ['POST', 'GET'])
def playlist_get():
	data = request.json
	(success, playlist) = room_room_get_playlist(data['room_id'])	
	return jsonify({
		'success': success,
		'playlist': playlist
		})

@app.route('/playlist_generate_url/', methods = ['POST'])
def playlist_generate_url():
	data = request.json
	(success, url) = room_export_playlist(data['user_id'], data['name'], data['room_id'], data['token'])	
	return jsonify({
		'success': success,
		'url': url
		})

if __name__=='__main__':
	# This is used when running locally only. When deploying to Google App
	# Engine, a webserver process such as Gunicorn will serve the app. This
	# can be configured by adding an `entrypoint` to app.yaml.
	app.run(host='127.0.0.1', port=8080, debug=True)