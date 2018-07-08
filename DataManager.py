# DataManager module - 7/8/2018 - Paul Leimer
#
#	DataManager acts as a intermediary between incoming data and api's that process that data
#
#	Data is managed on a time interval basis - data is stored in a ledger spanning a specified 
#	delta time into the past in reference to the present. Data existing before the delta is 
#	discarded.
#
#	Multiple ledgers can be instantiated and pulled from by external APIs. Ledgers are stored
#	within a ledger table and accessed by a unique ID string
#
#	DataManager accepts a data source as long as it follows the following protocol:
#		
#		* A data source must be passed in - this must take the form of a queue
#		* Data may enter at any rate - time is not accounted for based on rate information enters
#		* Each message must contain the following information:
#			message = {
#				'time': <match timed in iso string format>,
#				'price': <float representation of closing price>,
#				'volume': <int representation of volume at time of match>
#			};
#
#
#	Rate is not accounted for in order to allow for both real time data to be processed
#	as well as bulk data acquired previously for quick simulations
#
#	I/O bound, therefore the threading module is used

import threading, Queue
from datetime import datetime, timedelta, timezone
import time

class DataManager(threading.Thread):
	
	#wraps a set containing data points for a time frame 
	#each point is in format: {'price':<price>, 'time':<time>, 'percentage': <percent of time interval>}
	class Ledger:
		def __init__(self, time_length):
			self._time_length = timedelta(seconds = time_length)
			self._data_points = []
			
		def sync(self, data_point, present_time):
			backend_time = present_time - self._time_length #time back of ledger exists at
			
			#add data point to ledger
			self._data_points.append({
				'price': data_point['price'],
				'time': datetime.fromtimestamp(data_point['time'], timezone.utc),
				'percentage': 0.00
			}) 
			
			#calc percentage of time interval point encompasses
			for point in self._data_points:
				point['percentage'] = (present_time - point['time'])/self._time_length * 100
			
			#destroy points that are out of time range (greater than 100% of time interval)
			self._data_points[:] = [point for point in self._data_points if point['percentage'] < 100]
		
		def getPrices(self):
			prices = []
			for point in self._data_points:
				prices.append(point['price'])
			return prices[1:]
			
		def getTimes(self):
			times = []
			for point in self._data_points:
				prices.append(point['time'])
			return prices[1:]
			
		

	def __init__(self, data_source, real_time):
		super().__init__()
		self._data_source = data_source
		self._ledger_table = {}
		self._real_time = real_time
		
		self.stop_request = threading.Event()

	#-----------------------------Manager Functions-----------------------------#
	
	#edit ledgers as messages come in
	def run(self):
		while not self.stop_request.isSet():
			#real time
			if self._real_time:
				while True: #process all items in queue
					time_now = datetime.utcnow()
					try:
						data_point = self.data_source.get(False) #blocking is false because we want calculation to happen every second regardless of when message comes in
						for uid, ledger in self._ledger_table.iteritems(): #sync all existing ledgers
							ledger.sync(data_point, time_now)
					except Queue.Empty:
						break
				
				time.sleep(1)
			
			
			#simulated time
			else not self._real_time:
				try:
					data_point = self.data_source.get(True, 0.05) #process one item in queue at a time 
					for uid, ledger in self._ledger_table.iteritems():
						ledger.sync(data_point, datetime.fromtimestamp(data_point['time'], timezone.utc))
				except Queue.Empty:
					continue
	
	
	def join(self, timeout=None):
		self.stop_request.set()
		super().join(timeout)
	
	
	#---------------------------- API Calls ------------------------------------#
	
	#	Creates a new ledger object of length delta time in seconds
	#	returns an identifier to that ledger for future access
	#	does not return a ledger object - do not want external api's to 
	#	directly access the ledger
	
	def newLedger(self, seconds, uid):
		self._ledger_table[uid] = Ledger(seconds)
	
	#returns all prices in specified ledger as a list, most recent being in slot zero
	def getPrices(self, uid):
		return self.ledger_table[uid].getPrices()
	
	#returns all times in specified ledger as a list, most recent being in slot zero
	def getTimes(self, uid):
		return self.ledger_table[uid].getTimes()
	
	#returns most recent match price
	def getLastPrice(self):
		return self.ledger_table[uid].getPrices()[-1]
	
	#resturn time of last match
	def getLastTime(self):
		return self.ledger_table[uid].getTimes()[-1]
	
	
	
	
	
	
	



