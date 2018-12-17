import datetime
import pprint
import pymongo
from threading import Thread
from pymongo import MongoClient
from bson.objectid import ObjectId

## MONGO DB
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

def _room_create(owner_id, room_name):
	document = {
		'owner_id': owner_id,
		'name': room_name,
		'users': [],
		'creation_date': str(datetime.datetime.utcnow()),
		'last_modification_date': str(datetime.datetime.utcnow())
	}
	result = db.rooms.insert_one(document)
	room = db.rooms.find_one({'_id' : result.inserted_id})
	return (True, room)


def _room_add_user(user_id, room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None)
	else:
		new_users = room['users']
		new_users.append(user_id)
		db.rooms.update_one({'_id' : ObjectId(room_id)}, {"$set": {'users': new_users, 'last_modification_date': str(datetime.datetime.utcnow())}})
		room = db.rooms.find_one({'_id' : ObjectId(room_id)})
		return (True, room)

def _room_remove_user(user_id, room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None)
	else:
		new_users = room['users']
		new_users = [item for item in new_users if item != user_id]
		db.rooms.update_one({'_id' : ObjectId(room_id)}, {"$set": {'users': new_users, 'last_modification_date': str(datetime.datetime.utcnow())}})
		room = db.rooms.find_one({'_id' : ObjectId(room_id)})
		return (True, room)

def _room_get(room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	if(room == None):
		return (False, None, None)
	else:
		users_ids = room['users']
		users_ids.append(room['owner_id'])
		results = db.users.find({'id': { '$in': users_ids }}, {'id': 1, 'name': 1, 'image': 1, 'finished_loading': 1})
		return (True, room, list(results))
	(success, room, users) = _room_get(room_id)