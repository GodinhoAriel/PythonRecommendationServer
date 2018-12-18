import pprint
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import math
from music_clustering import *
from room import *

pp = pprint.PrettyPrinter()
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

def moderator_generate_playlist(room_id):
	room = db.rooms.find_one({'_id' : ObjectId(room_id)})
	user = db.users.find_one({'id' : room['owner_id']})
	track_ids = generate_recommendation(user, count=20, k=8, min_popularity = 50)
	print(track_ids)
	room_room_set_playlist(room_id, track_ids)

	(success, playlist) = room_room_get_playlist(room_id)
	print(playlist)
	return (success, playlist)

