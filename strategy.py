# strategy.py	07/4/2018	Paul Leimer
#
# Abstract:
#
# The Strategy class is one of two classes in this entire program that the front-end user will interact with -  
# here, a trading strategy is defined
#
# Each strategy must inherit from this class and override the setup() and strategy() functions
#
# setup() - the user must define all of their Auditor - type objects here and register them bytearray
#			calling the registerAuditor() function on them
#
# strateg() - within this function the conditions for trade must be defined
			
			
from abc import ABCMeta, abstractmethod
import auditor
import threading


#import broker


class Strategy(threading.Thread):
	__metaclass__ = ABCMeta

	def __init__(self):
		super().__init__()
		#these vaules must be created in set up
		self.auditors = []
		self._broker = None
		
		self.stop_request = threading.Event()
		
		self.setup()
		
	def run(self):
		try:
			while not self.stop_request.isSet():
				for auditor in self.auditors:
					auditor.waitOnUpdate()
				self.strategy()
		except:
			return
			
			
	def close(self, timeout=None):
		self.stop_request.set()
		
		for auditor in self.auditors:	
			auditor.close()
			
		super().join(timeout)
		
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
		
	
	
	
