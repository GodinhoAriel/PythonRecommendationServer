import pprint
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from sklearn.cluster import KMeans
import math

pp = pprint.PrettyPrinter()
client = MongoClient('mongodb://musicclustering:o5oF111QxnPaMXmk@clustermdb-shard-00-00-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-01-gg5i3.gcp.mongodb.net:27017,clustermdb-shard-00-02-gg5i3.gcp.mongodb.net:27017/test?ssl=true&replicaSet=ClusterMDB-shard-0&authSource=admin&retryWrites=true')
db = client.server

def euclidian_distance(pointA, pointB):
	distance = 0
	for valA, valB in zip(pointA, pointB):
		distance += (valA - valB) ** 2
	
	return math.sqrt(distance)


def sum_distances(centroids, labels, values):
	total_sum = 0
	
	for value, label in zip(values, labels):
		total_sum += euclidian_distance(value, centroids[label]) ** 2        
		
	return total_sum

def k_means(values, k):
	clf = KMeans(n_clusters = k)
	clf.fit(values)

	print('Fit done. k =', k)

	centroids = clf.cluster_centers_
	labels = clf.labels_

	total_distance = sum_distances(centroids, labels, values)
	
	return (centroids, labels, total_distance)

# def standart_deviation(mean, values):
# 	sd_vector = []
# 	for i in range(len(mean)):
# 		d_sum = 0
# 		for value in values:
# 			d_sum += (mean[i] - value[i]) ** 2
# 		sd = math.sqrt(d_sum / (len(values)-1))
# 		sd_vector.append(sd)
# 	return sd_vector

def generate_recommendation(user, count=100, k=8, min_popularity = 50):
	# Get user tracks
	results = db.tracks.find({'id' : {'$in' : user['tracks_ids']}}, {'_id': 0, 'id': 1, 'features.acousticness' : 1, 'features.danceability' : 1, 'features.energy' : 1, 'features.instrumentalness' : 1, 'features.liveness' : 1, 'features.speechiness' : 1, 'features.valence': 1})
	user_tracks = list(results);

	# extract values and run kmeans
	values = [list(item['features'].values()) for item in user_tracks]	
	(centroids, labels, total_distance) = k_means(values, k)

	# Get all tracks
	results = db.tracks.find({'id' : {'$in' : user['tracks_ids']}, 'popularity' : {"$gte": min_popularity} }, {'_id': 0, 'id': 1, 'features.acousticness' : 1, 'features.danceability' : 1, 'features.energy' : 1, 'features.instrumentalness' : 1, 'features.liveness' : 1, 'features.speechiness' : 1, 'features.valence': 1})
	tracks = [(item['id'], list(item['features'].values())) for item in list(results)]

	# Evaluate tracks
	evaluated_tracks = evaluate_tracks(centroids, labels, tracks)

	return [item[1] for item in evaluated_tracks[0:count]]


def evaluate_tracks(centroids, labels, tracks):
	performance_list = []
	for track in tracks:
		performance = recommendation_performance(track, centroids, labels)
		performance_list.append((performance, track[0]))
	performance_list.sort(reverse=True)
	return performance_list

def recommendation_performance(track, centroids, labels):
	performance = 0
	centroid = centroids[0]
	n_features = len(centroid)
	
	#find closest centroid and biggest centroid size
	lesser_distance = 999
	greatest_count = 0
	cluster_index = 0
	for i in range(len(centroids)):
		c = centroids[i]
		distance = euclidian_distance(c, track[1])
		count = list(labels).count(i)
		if distance < lesser_distance:
			lesser_distance = distance
			centroid = c
			cluster_index = i
		if count > greatest_count:
			greatest_count = count
	
	#ratio of the cluster's respective size in relation to the biggest cluster
	cluster_size_ratio = list(labels).count(cluster_index) / greatest_count
	
	# # Avarage of the cluster's deviations
	# cluster_avg_deviation = 0
	# for val in deviations[cluster_index]:
	#     cluster_avg_deviation += val **2        
	# cluster_avg_deviation = math.sqrt(cluster_avg_deviation) / n_features
	
	return  cluster_size_ratio * (1-lesser_distance)
