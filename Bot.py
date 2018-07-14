# Sets up everything and runs a trading script

import DataStream
#from DataStream import DataStream
from DataManager import DataManager
import time
import statistics
import threading

#to deleter
import teststrategy


# create a data stream - may leave this up to bot manager so that I can trade on multiple coins at once
# create data manager, register it with datastream - may leave this up to bot manager so that I can trade on multiple coins at once
# load a strategy object that is passed into it
	#strategy object should have a registor auditor function that registers and auditor to that builds list of auditors created
	#that users will use
# get list of auditors from strategy, register them with DM

# create a broker
# register the broker with the strategy
# run strategy
# report results to the bot manager


class Bot(threading.Thread):
	def __init__(self, strategy): #set up infrastructure
		super().__init__()

		#create data stream and data manager
		self.stream = DataStream.DataStream(['ETH-USD'])
		self.data_manager = DataManager(self.stream.getStream(), True)
		
		#strategy
		self.strategy = strategy

		#register frames that auditors in strategy uses in data manager so they can be updated live
		for auditor in self.strategy.getAuditors():
			self.data_manager.registerFrame(auditor.getFrame())
			
		#put in historical data
		
	def run(self):
		try:
			self.stream.start()
			self.data_manager.start()
			
			#for now, have strategy run in bot's thread
			#self.strategy.run()
			time.sleep(5*60)
		
		except KeyboardInterrupt:
			pass
			
		for auditor in self.strategy.getAuditors():	
			auditor.close()
		self.data_manager.close()	
		self.stream.close()
		
		
if __name__ == "__main__":
	strat = teststrategy.TestStrat()
	bot = Bot(strat)
	bot.start()
	bot.join()


