# strategy module handles the income of Auditor statistics and exchange 
# trade messages and implements a strategy for buying and selling
#
# strategy does not execute buying and selling options itself but instead 
# gives the go to the broker which handles interfacing with the GDAX authenticated
# client
#
# All strategies must inherit from main strategy class and overide the 
# setup(), buyOn and sellOn methods
#
# Needs to be able to:
#	- Create frames, register auditors on those frames, and listen to the auditors
#	- Two threads: one to listen for auditor updates and one to listen for exchange responses
#
# Implementing strategy:
#	- set it up, creating registering broker, creating frames and auditors
#
# To use:
# 	* Instantiate strategy
#	* pass to broker

# strategies should utilize the broker thread
from abc import ABCMeta, abstractmethod
import auditor
import threading

#import broker


class Strategy():
	__metaclass__ = ABCMeta

	def __init__(self):
		#these vaules must be created in set up
		self.auditors = []
		self._broker = None
		
		self.setup()
		
	def run(self):
		return
		
	def registerAuditor(self, auditor):
		self.auditors.append(auditor)
		
	def getAuditors(self):
		return self.auditors
	
		
	@abstractmethod	
	def setup(self): #create auditors and set conditions for buys and sells
		pass
		
	@abstractmethod	
	def strategy(self): #create auditors and set conditions for buys and sells
		pass
		
	
	
	
