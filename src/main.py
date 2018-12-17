from flask import jsonify
from flask import Flask, Response
from flask import request
from flask_cors import CORS
import pymongo
from pymongo import MongoClient
import json
from bson import ObjectId
from profile_setup import *

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

@app.route('/')
def index():
	# client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
	# db = client.server
	# user = db.users.find_one({'id' : '12152580425'})
	return('done')

@app.route('/get_user/')
def get_user():
	user = db.users.find_one({'id' : '12152580425'})
	user['_id'] = str(user['_id'])
	print(user)
	return jsonify(user)

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



if __name__=='__main__':
	# This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)