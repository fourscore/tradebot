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

import threading
import queue
from queue import Queue
from datetime import datetime, timedelta, timezone
import time

#wraps a set containing data points for a time frame 
	#each point is in format: {'price':<price>, 'time':<time>, 'percentage': <percent of time interval>}
class Ledger:
	def __init__(self, time_length):
		self._time_length = timedelta(seconds = time_length)
		self._data_points = []
		
	def addPoint(self, data_point, present_time):
		#add data point to ledger
		self._data_points.append({
			'price': data_point['price'],
			'time': datetime.strptime(data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
			'percentage': 0.00
		}) 
		
	def sync(self, present_time):
		backend_time = present_time - self._time_length #time back of ledger exists at
		
		#calc percentage of time interval point encompasses
		for point in self._data_points:
			if point['time'] < backend_time:
					point['time'] = backend_time
			point['percentage'] = (present_time - point['time'])/self._time_length * 100
		
		#align percentages
		for index, point in enumerate(self._data_points):
			if index != (len(self._data_points) - 1):
				point['percentage'] = point['percentage'] - self._data_points[index + 1]['percentage']
				
				if point['percentage'] == 0.00:
					self._data_points.pop(index)
				
	
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
		
	def __repr__(self):
		return str(self._data_points)
		
		

class DataManager(threading.Thread):
			
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
						data_point = self._data_source.get(False) #blocking is false because we want calculation to happen every second regardless of when message comes in
						for uid, ledger in self._ledger_table.items(): #add point
							ledger.addPoint(data_point, time_now)
					except queue.Empty:
						break
					except KeyError:
						break

				for uid, ledger in self._ledger_table.items(): #sync all existing ledgers
					ledger.sync(time_now)
				print(self._ledger_table)
				
				time.sleep(1)
			
			
			#simulated time
			elif not self._real_time:
				try:
					data_point = self._data_source.get(True, 0.05) #process one item in queue at a time 
					for uid, ledger in self._ledger_table.items():
						ledger.addPoint(data_point, datetime.strptime(data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ"))
						ledger.sync(datetime.strptime(data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ"))
				except queue.Empty:
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
	
	
	
	
