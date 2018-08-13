# DataManager module - 7/8/2018 - Paul Leimer
#
#	DataManager acts as a intermediary between incoming data and api's that process that data
#
#	Data is managed on a time interval basis - data is stored in a ledger spanning a specified
#	delta time into the past with respect to the present. Data existing before the delta is
#	discarded.
#
#	Multiple frames can be instantiated and pulled from by external APIs. Frames are stored
#	within a frame table
#
#	DataManager accepts a data source as long as it follows the following protocol:
#
#		* A data source must provide a queue for the frame to access
#		* Each message must contain the following information:
#			message = {
#				'time': <match timed in iso string format>,
#				'price': <decimal class representation of closing price>,
#				'last_size': <decimal class object of product size>
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
from datastream import getHistoricalData
import time

#wraps a set containing data points for a time frame
	#each point is in format: {'price':<price>, 'time':<time>, 'percentage': <percent of time interval>}
class Frame:
	def __init__(self, time_length, product):
		self._time_length = timedelta(seconds = time_length)
		self._data_points = []
		self.sync_complete = threading.Event()
		self.lock = threading.Lock()

		print("Collecting historical data...")
		self._inject(getHistoricalData(time_length, product))



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
		index = 0
		while index < len(self._data_points):
			if index != (len(self._data_points) - 1):
				self._data_points[index]['percentage'] = self._data_points[index]['percentage'] - self._data_points[index + 1]['percentage']

				if self._data_points[index]['percentage'] == 0.0:
					self._data_points.pop(index)
					index -= 1

			index += 1



		self.lock.release()
		self.sync_complete.set()

	#fill frame with past data
	def _inject(self, data):
		for field in data:
			self.addPoint(field)

	#----------------------------------Functions for external use -----------------------------------------#
	#	Functions for use outside of this module

	def get(self):
		self.sync_complete.wait()
		self.sync_complete.clear()
		return self._data_points

	def __str__(self):
		return str(self._data_points)

#Candle - updates itself with data passed in for interval of time specified by length.
#	stores information about that time interval, such as open price, high,
#	close price, and volume during bucket
#
#	candle class will set is_closed flag to true when it's closing time is reached
#	and will discontinue updating even if new data is passed in
#
#	External programs are responsible for watching if a candle has closed, getting
#	and storing the data, and re-opening the candle for a new interval if the
#	candle should be re-used
#

class Candle:
	def __init__(self, length, open_time, start_point):
		self.length = timedelta(seconds = length)
		self.time = open_time

		price = start_point['price']
		self.low =	 price
		self.high =  price
		self.open =  price
		self.close = None
		self.volume = 0

		self.is_closed = False

	#only update if time of data is within time interval specified by
	#self.time and self.time + self.length
	def sync(self, last_data_point):
		data_time = datetime.strptime(last_data_point['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
		price = last_data_point['price']
		if data_time <= (self.time + self.length):
			if self.low > price: self.low = price
			if self.high < price: self.high = price
			if data_time >= self.time: self.volume += last_data_point['volume']
		else:
			self.is_closed = True
			if not self.close:
				self.close = price
				self.volume += last_data_point['volume']

	#inject data into a candle for time that has already passed
	#if candle is closed, don't bother
	def _inject(self, data):
		for point in data:
			self.sync(point)
			if self.is_closed:
				return


	def __str__(self):
		return str(self.time) + " " + str(self.low) + " " + str(self.high) + " " + str(self.open) + " " + str(self.close) + " " + str(self.volume)



#CandleRecord - contains candles of specified granularity spanning a specified
#	number of num_candles
#
#	for now, historical data will come straight from gdax. Later, it should come
#	from the database

class CandleRecord:
	def __init__(self, granularity, num_candles, product):

		if (granularity < 60) and (granularity % 60 == 0):
			print('[CANDLE RECORD] Granularity must be greater than or equal to 60 ' +
					'and in multiples of 60. Aborted')
			return

		self.granularity = granularity
		self.num_candles = num_candles
		self.product = product
		self.record = []

		#fill record with previous data
		prev_data = getHistoricalData(num_candles * granularity, product)
		start_time = datetime.strptime(prev_data[1]['time'], "%Y-%m-%dT%H:%M:%S.%fZ")

		#try:
		for iter in range(num_candles):
			candle = Candle(granularity, start_time, prev_data[int(iter * (granularity / 60))])
			candle._inject(prev_data)
			self.record.append(candle)

			#calc open time for next candle
			start_time = start_time + timedelta(seconds=granularity)

		#except Exception as e:
		#	print("[CANDLE RECORD] Failed to fill record. Aborting with err ")
		#	print(e)





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


#for testing classes
if __name__ == '__main__':
	rec = CandleRecord(60, 10, 'BTC-USD')
	print('Record: ')
	for can in rec.record:
		print(can)
