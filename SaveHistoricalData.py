import datastream
from pymongo import MongoClient

#script to save a bunch of GDAX data base

client = MongoClient()
db = client.profitdb

try:
    data = datastream.getHistoricalData(3*24*60*60,'BTC-USD')

    #format data like live ticker data, except stores time as seconds since epoch

    response = db.exch_data.insert(data)
    print('Successfully saved data to document exch_data')
    #print('Posts: {0}'.format(response.inserted_ids))

except Exception as e:
    print('Failed to get data; error: ' + str(e))
