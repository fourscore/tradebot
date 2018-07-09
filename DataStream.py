# Data Stream module - 07/08/2018 - Paul Leimer
#	opens a websocket link to the GDAX API, subscribes to the ticker channel
#	manages a queue that can be used by other threads to process messages from
#	GDAX
#
#	Only useful for data points


import gdax
from queue import Queue

class DataStream(gdax.WebsocketClient):
	def __init__(self, products):
		super().__init__(self)
		self.products = products
		self.channels = ['ticker']
		self.url = "wss://ws-feed.gdax.com/" 
		
		self._data_queue = Queue()
		
		self.start()
	
	def getStream(self):
		return self._data_queue
	
	def on_open(self):
		return
		
	def on_message(self, msg):
		self._data_queue.put(msg)
		
	def on_close(self):
		print("GDAX Stream terminated")