import sys
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server
from flask import Flask 
app = Flask(__name__)

@app.route('/')
def index():
	return "Hello World"

@app.route('/temperature', methods=['GET'])
def temperature():
	user = db.users.find_one({'id' : '12152580425'})
	return user

if __name__=='__main__':
	# This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)