# Data Stream module - 07/08/2018 - Paul Leimer
#	opens a websocket link to the GDAX API, subscribes to the ticker channel
#	manages a queue that can be used by other threads to process messages from
#	GDAX
#
#	At start, data stream queues past data of specified time into the past
#
#	Only useful for data points


import gdax
import time
from queue import Queue
from datetime import datetime, timedelta
from decimal import Decimal
import requests


def getHistoricalData(secs, product): #can't be less than one
		if(secs < 60):
			raise ValueError("Seconds must be greater than 60")

		public_client = gdax.PublicClient()
		ret = []
		res = []

		start_time = datetime.utcnow() - timedelta(seconds = secs)
		back_end = start_time

		while secs/60 > 300:
			end_time = start_time + timedelta(seconds = 300 * 60)

			try:
				res.append(public_client.get_product_historic_rates(product,  granularity = 60, start = start_time.isoformat(), end=end_time.isoformat())[::-1])
				start_time = end_time
				secs = secs - 60*300
				time.sleep(.6)

			except requests.exceptions.ConnectionError:
				print("[HISTORICAL DATA] Cannot connect to GDAX. No data returned")
				return []
			except:
				print("Invalid data. Trying again")
				continue


		time.sleep(.5)
		res.append(public_client.get_product_historic_rates(product,  granularity = 60, start = start_time.isoformat(), end=datetime.utcnow().isoformat())[::-1])

		#build results into proper jsons
		#gdax output is list containing:
		#[ time, low, high, open, close, volume ],
		#[ 1415398768, 0.32, 4.2, 0.35, 4.2, 12.3 ]

		for set in res:
			for field in set:
				if datetime.utcfromtimestamp(field[0]) >= (back_end - timedelta(seconds=60)):
					ret.append({
						'time': datetime.utcfromtimestamp(field[0]).isoformat() + '.00Z',
						'price': Decimal(field[4]),
						'last_size': Decimal(field[5])
					})

		return ret




class DataStream(gdax.WebsocketClient):
	def __init__(self, products):
		super().__init__(self)
		self.products = products
		self.channels = ['ticker']
		self.url = 'wss://ws-feed.pro.coinbase.com'

		self._data_queue = Queue()

	def getStream(self):
		return self._data_queue

	def on_open(self):
		return

	def on_message(self, msg):
		#try:
		#	msg['time'] = msg['time'][:-8]
		#except: pass
		self._data_queue.put(msg)

	def on_close(self):
		print("GDAX Stream terminated")
