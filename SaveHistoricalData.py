import datastream
from pymongo import MongoClient

#script to save a bunch of GDAX data base

client = MongoClient()
db = client.profitdb

data = datastream.getHistoricalData(2*24*60*60,'BTC-USD')

#format data like live ticker data, except stores time as seconds since epoch

response = db.exch_data.insert_many(data)
print('Posts: {0}'.format(response.inserted_ids))
	

