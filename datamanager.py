# DataManager module - 7/8/2018 - Paul Leimer
#
#	DataManager acts as a intermediary between incoming data and api's that process that data
#
#	Data is managed on a time interval basis - data is stored in a ledger spanning a specified 
#	delta time into the past with respect to the present. Data existing before the delta is 
#	discarded.
#
#	Multiple ledgers can be instantiated and pulled from by external APIs. Frames are stored
#	within a ledger table and accessed by a unique ID string
#
#	DataManager accepts a data source as long as it follows the following protocol:
#		
#		* A data source must provide a queue for the frame to access
#		* Each message must contain the following information:
#			message = {
#				'time': <match timed in iso string format>,
#				'price': <float representation of closing price>
#			};
#
#
#	Rate data enters is not accounted for in order to allow for both real time data to be processed
#	as well as bulk data acquired previously for quick simulations
#
#	I/O bound, therefore the threading module is used
#
#	Bugs: Frame is not properly popping off out of date data points 
#		when: Every now and then
#		consequence: that data point has a 'percentage' value of 1.0 , causing percentages to add up to 2
#					instead of 1. Throws off statistical calculations
import threading
import queue
from queue import Queue
from datetime import datetime, timedelta, timezone
import time

#wraps a set containing data points for a time frame 
	#each point is in format: {'price':<price>, 'time':<time>, 'percentage': <percent of time interval>}
class Frame:
	def __init__(self, time_length):
		self._time_length = timedelta(seconds = time_length)
		self._data_points = []
		self.sync_complete = threading.Event()
		self.lock = threading.Lock()
		
	def addPoint(self, data_point):
		self.lock.acquire()
		#add data point to ledger
		try:
			self._data_points.append({
				'price': data_point['price'],
				'time': datetime.strptime(data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
				'percentage': 0.00
			})
			self.lock.release()
		except KeyError:
			self.lock.release()
			return
		
	def sync(self, present_time):
		self.lock.acquire()
		backend_time = present_time - self._time_length #time back of ledger exists at
		
		#calc percentage of time interval point encompasses
		for point in self._data_points:
			if point['time'] < backend_time:
					point['time'] = backend_time
			point['percentage'] = (present_time - point['time'])/self._time_length

		
		#align percentages
		for index, point in enumerate(self._data_points):
			if index != (len(self._data_points) - 1):
				point['percentage'] = point['percentage'] - self._data_points[index + 1]['percentage']
				
				if point['percentage'] == 0.00:
					self._data_points.pop(index)
		
		self.lock.release()
		self.sync_complete.set()
		
		
	#----------------------------------Functions for external use -----------------------------------------#
	#	Functions for use outside of this module

	
	def get(self):
		self.sync_complete.wait()
		self.sync_complete.clear()
		return self._data_points
		
	#fill frame with past data
	def inject(self, data):
		for field in data:
			self.addPoint(field)
		
	def __str__(self):
		return str(self._data_points)
		
		

class DataManager(threading.Thread):
			
	def __init__(self, data_source, real_time):
		super().__init__()
		self._data_source = data_source
		self._frame_record = []
		self._real_time = real_time
		
		self.stop_request = threading.Event()

	#-----------------------------Manager Functions-----------------------------#
	
	#edit ledgers as messages come in
	def run(self):
		
		while not self.stop_request.isSet():
			if not self._frame_record:
				print('DataManager must have registered frames in order to track data')
				return
					
			#real time
			if self._real_time:
				while True: #process all items in queue
					time_now = datetime.utcnow()
					try:
						data_point = self._data_source.get(False) #blocking is false because we want calculation to happen every second regardless of when message comes in
						for frame in self._frame_record: #add point
							frame.addPoint(data_point)
					except queue.Empty:
						break

				for frame in self._frame_record: #sync all existing ledgers
					frame.sync(time_now)
			
				#print(self._frame_record)
					
				
				
				#simulated time
				'''
				elif not self._real_time:
					try:
						data_point = self._data_source.get(True, 0.05) #process one item in queue at a time 
						for uid, frame in self.self._frame_record.items():
							frame.addPoint(data_point)
							frame.sync(datetime.strptime(data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ"))
					except queue.Empty:
						continue
				'''
					
			time.sleep(1)
	
	
	def close(self, timeout=None):
		self.stop_request.set()
		super().join(timeout)

	def registerFrame(self, frame):
		self._frame_record.append(frame)
	
	
