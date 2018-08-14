# Bot.py	7/14/2018	Paul Leimer
#
#	Highest level implementation of cryptocurrency trading bot
#
#	Upon instantiation, sets up all of the necessary infrastructure to trade on a specified currency with a specified strategy
#	Each bot can only trade on a single product - to trade on multiple, new bots must be created
#	I will create a BotManager object to oversee the operation of many bots at the same time

from tickersimulator import DataStream
#from datastream import DataStream
from datamanager import DataManager
import time
import statistics
import threading
import requests
import sys
#to deleter
import teststrategy


class Bot(threading.Thread):

	#def __init__(self, strategy, product): #set up infrastructure
	def __init__(self, product): #TEMPORARY
		super().__init__()

		self.stop_request = threading.Event()

		# Steps to setup a bot object:
		# 1) create a data stream - may leave this up to bot manager so that I can trade on multiple coins at once
		# 2) create data manager, register it with datastream - may leave this up to bot manager so that I can trade on multiple coins at once
		# 3) Save instance variable of passed in strategy
		# 4) The strategy object contains auditors which contain frames. Register these frames to the data manager
		# 5) Inject historical data into those frames (else it will take time to fill up with data)


		# 6) create a broker
		# 7) register the broker with the strategy

		#create data stream and data manager
		self.stream = DataStream([product])
		print('[BOT] Completed creation of data stream')
		self.data_manager = DataManager(self.stream.getStream(), False)
		print('[BOT] Completed creation of data manager')

		#strategy
		#self.strategy = strategy
		self.strategy = teststrategy.TestStrat(self.data_manager) #TEMPORARY
		print('[BOT] Successfully initiated strategy')

		#register frames that auditors in strategy uses in data manager so they can be updated live
		#for auditor in self.strategy.getAuditors():
		#	self.data_manager.registerFrame(auditor.getFrame())

		#put in historical data


	def run(self):
		try:
			self.stream.start()
			self.data_manager.start()
			self.strategy.start()
			self.stop_request.wait()
		except:
			return

	def close(self, timeout=None):
		self.stop_request.set()

		#clean up
		self.strategy.close()
		self.data_manager.close()
		self.stream.close()
		super().join()

if __name__ == "__main__":
	#strat = teststrategy.TestStrat(self.data_manager)
	bot = Bot('BTC-USD')
	bot.start()
	'''
	try:
		print("Online")
		sys.stdout.flush()
		bot.start()
		time.sleep(10)
	except: pass
	print("Offline")
	sys.stdout.flush()
	'''

	time.sleep(2*60)
	bot.close()
