import DataStream
from pymongo import MongoClient

#script to save a bunch of GDAX data base

client = MongoClient()
db = client.profitdb

data = DataStream.getHistoricalData(3*24*60*60,'ETH-USD')

response = db.exch_data.insert_many(data)
print('Posts: {0}'.format(response.inserted_ids))
	

