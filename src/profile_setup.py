import pprint
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import pymongo
from threading import Thread
from pymongo import MongoClient
from bson.objectid import ObjectId

## MONGO DB
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

## SPOTIFY CLIENT
client_credentials_manager = SpotifyClientCredentials(
	client_id='9c93bd032a4340b086b31bd30ec8f24c',
	client_secret='b893fd0a51d34e2399effa91c1026de7')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def authenticate_user(token):
	#scope = 'user-top-read user-library-read playlist-modify-private playlist-read-private user-read-playback-state user-modify-playback-state'
	max_songs = 1000 #00

	if token:
		#Set token to spotify library
		sp = spotipy.Spotify(auth=token)
		
		print('Loading saved tracks...')
		user_tracks = []
		for offset in range(0, max_songs, 50):
			results = sp.current_user_saved_tracks(50,offset)
			if(offset > results['total']):
				break
			user_tracks.extend([item['track'] for item in results['items']])
			print(len(user_tracks), end=' \r')    
		print(len(user_tracks))

		return user_tracks
	else:
		print("Can't get token for user")

def load_artists(user_tracks):
	## DISCOVER NEW TRACKS (based on user's profile)
	## ARTISTS
	# Get all user's artists
	all_user_artists = []
	[[all_user_artists.append(artist['id'])
		for artist in artist_list]
			for artist_list in [track['artists'] for track in user_tracks]]
	all_user_artists = set(all_user_artists)
	print("User's unique artists: ", len(all_user_artists))

	# # Get related artists
	# print('Loading related artists...')
	# all_related_artists = []
	# for artist_id in all_user_artists:
	#     related_artists = sp.artist_related_artists(artist_id)
	#     all_related_artists.extend([artist['id'] for artist in related_artists['artists']])
	#     print(len(all_related_artists), end=' \r')
	# print(len(all_related_artists))
	# all_related_artists = set(all_related_artists)
	# print("User's unique related artists: ", len(all_related_artists))

	# all_related_artists.append(all_user_artists)	

	all_related_artists = all_user_artists

	# Get all artist's top tracks
	print('Loading artists tracks...')
	all_tracks = []
	i = 0
	for artist_id in list(all_related_artists):
		i += 1
		artist_top_tracks = sp.artist_top_tracks(artist_id)
		#all_tracks.extend([(track['artists'][0]['name'], track['name'], track['id']) for track in artist_top_tracks['tracks']])
		all_tracks.extend(artist_top_tracks['tracks'])
		print('('+str(i)+'/'+str(len(all_related_artists))+')', len(all_tracks), end=' \r')
	print('('+str(i)+'/'+str(len(all_related_artists))+')', len(all_tracks))
	#all_tracks = set(all_tracks)
	print("Unique tracks: ", len(all_tracks))
	return (all_user_artists, all_tracks)


def save_tracks(all_tracks):
	## MONGODB
	for track, i in zip(all_tracks, range(len(all_tracks))):
	    track_item = {
	        'id': track['id'],
	        'album_id': track['album']['id'],
	        'album_image': track['album']['images'][0],
	        'artists_ids': [artist['id'] for artist in track['artists']],
	        'artists_names': [artist['name'] for artist in track['artists']],
	        'disc_number': track['disc_number'],
	        'duration_ms': track['duration_ms'],
	        'explicit': track['explicit'],
	        'external_ids': track['external_ids'],
	        'external_urls': track['external_urls'],
	        'href': track['href'],
	        'is_local': track['is_local'],
	        'name': track['name'],
	        'popularity': track['popularity'],
	        'preview_url': track['preview_url'],
	        'track_number': track['track_number'],
	        'type': track['type'],
	        'uri': track['uri'],
	    }
	    print(i, end=' \r')
	    db.tracks.update_one({'id' : track_item['id']}, {"$set": track_item}, upsert=True)

def save_features(all_tracks):
	features_list = []
	print('Loading tracks features...')
	for index in range(0, len(all_tracks), 100):
	    features_list.extend(sp.audio_features(tracks=[track['id'] for track in all_tracks[index:index+100]]))
	    print(len(features_list), end='\r')   
	print(len(features_list))
	
	## INSERINDO FEATURES NAS MUSICAS DO BANCO
	print('Inserting tracks features...')
	i = 0
	j = 0
	for features in features_list:
	    i += 1
	    #pp.pprint(features)
	    if(features is not None):
	        bla = db.tracks.update_one({'id' : features['id']}, {"$set": {'features': features}})
	    else:
	        j += 1
	    print(i, end='\r')   
	print(i)
	print('Tracks without features: ', j)


def load_user_relevant_tracks(user_id, user_tracks):
	# Get artists and all tracks
	(user_artists, all_tracks) = load_artists(user_tracks)
	# Get tracks to save
	all_tracks.extend(user_tracks)
	id_list = [item['id'] for item in all_tracks]
	results = db.tracks.find({'id': { '$in': id_list }}, {"id": 1})
	ids_in_db = [item['id'] for item in list(results)]
	print('tracks already in DB:', len(ids_in_db))
	filtered_tracks = [item for item in all_tracks if item['id'] not in ids_in_db]
	print('tracks not in DB:', len(filtered_tracks))
	#pp.pprint(filtered_tracks)
	save_tracks(filtered_tracks)
	# Get Features and save
	save_features(filtered_tracks)

	document = {
	    'finished_loading': True
	}
	db.users.update_one({'id' : user_id}, {"$set": document}, upsert=True)


def save_user(user_id, user_tracks, image, name):
	tracks_ids = [track['id'] for track in user_tracks]
	document = {
	    'id': user_id,
	    'tracks_ids': tracks_ids,
	    'finished_loading': False,
	    'image': image,
	    'name': name
	}
	result = db.users.insert_one(document)
	#save_tracks(user_tracks)

## CALLS
def startup_user(token):
	sp = spotipy.Spotify(auth=token)
	user = sp.current_user()
	user_db = db.users.find_one({'id' : user['id']})

	# Return if already set up
	if(user_db != None): return user['id']
	# Get tracks
	user_tracks = authenticate_user(token)
	# Save user & user tracks
	images = user['images']
	if(len(images) > 0):
		image = images[0]
	else:
		image = None
	save_user(user['id'], user_tracks, image, user['display_name'])
	thread = Thread(target=load_user_relevant_tracks, args=(user['id'], user_tracks,))
	thread.start()
	return user['id']

def check_user_status(user_id):
	user_db = db.users.find_one({'id' : user_id})
	if(user_db != None):
		return (True, user_db['id'], user_db['finished_loading'])
	else:
		return (False, None, None)