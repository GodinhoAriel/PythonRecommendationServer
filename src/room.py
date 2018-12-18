import datetime
import pprint
import pymongo
from threading import Thread
from pymongo import MongoClient
from bson.objectid import ObjectId
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

## MONGO DB
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

## SPOTIFY CLIENT
client_credentials_manager = SpotifyClientCredentials(
	client_id='9c93bd032a4340b086b31bd30ec8f24c',
	client_secret='b893fd0a51d34e2399effa91c1026de7')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def room_room_set_playlist(room_id, track_ids):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return False
	else:
		db.rooms.update_one({'_id' : ObjectId(room_id)}, {"$set": {'playlist': track_ids, 'last_modification_date': str(datetime.datetime.utcnow())}})
		return True

def room_room_create(owner_id, room_name):
	document = {
		'owner_id': owner_id,
		'name': room_name,
		'users': [],
		'playlist': None,
		'creation_date': str(datetime.datetime.utcnow()),
		'last_modification_date': str(datetime.datetime.utcnow())
	}
	result = db.rooms.insert_one(document)
	room = db.rooms.find_one({'_id' : result.inserted_id})
	room['_id'] = str(room['_id'])
	return (True, room)


def room_room_add_user(user_id, room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None)
	else:
		new_users = room['users']
		new_users.append(user_id)
		db.rooms.update_one({'_id' : ObjectId(room_id)}, {"$set": {'users': new_users, 'last_modification_date': str(datetime.datetime.utcnow())}})
		room = db.rooms.find_one({'_id' : ObjectId(room_id)})
		room['_id'] = str(room['_id'])
		return (True, room)

def room_room_remove_user(user_id, room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None)
	else:
		new_users = room['users']
		new_users = [item for item in new_users if item != user_id]
		db.rooms.update_one({'_id' : ObjectId(room_id)}, {"$set": {'users': new_users, 'last_modification_date': str(datetime.datetime.utcnow())}})
		room = db.rooms.find_one({'_id' : ObjectId(room_id)})
		room['_id'] = str(room['_id'])
		return (True, room)

def room_room_get(room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None, None)
	else:
		users_ids = room['users']
		users_ids.append(room['owner_id'])
		results = db.users.find({'id': { '$in': users_ids }}, {'id': 1, 'name': 1, 'image': 1, 'finished_loading': 1})
		users = list(results)
		for user in users:
			user['_id'] = str(user['_id'])
		room['_id'] = str(room['_id'])
		return (True, room, users)

def room_room_get_list(limit):
	rooms = db.rooms.find({}).sort("last_modification_date", pymongo.DESCENDING).limit(limit)
	if(rooms == []):
		return (False, None)
	else:
		tuples_room_user = []
		for room in rooms:
			users_ids = room['users']
			users_ids.append(room['owner_id'])
			results = db.users.find({'id': { '$in': users_ids }}, {'id': 1, 'name': 1, 'image': 1, 'finished_loading': 1})
			users = list(results)
			for user in users:
				user['_id'] = str(user['_id'])
			room['_id'] = str(room['_id'])
			tuples_room_user.append({'room': room, 'users': users})
		return (True, tuples_room_user)

def room_room_get_playlist(room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None)
	else:
		track_ids = room['playlist'];
		result = db.tracks.find({'id': { '$in': track_ids }}, {'_id': 0, 'id': 1, 'name': 1, 'artists_names': 1, 'album_image': 1})
		return (True, list(result))

def room_export_playlist(user_id, name, room_id, token):	
	sp = spotipy.Spotify(auth=token)
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	playlist = sp.user_playlist_create(user_id, name, public=False, description='Playlist gerada automaticamente.')
	sp.user_playlist_replace_tracks(user=user_id, playlist_id=playlist['id'], tracks=room['playlist'])
	return (True, playlist['external_urls'])