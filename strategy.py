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
# strategy() - within this function the conditions for trade must be defined


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
		self.broker = None

		self._stop_listeners = threading.Event()
		self.stop_request = threading.Event()
		self.update_status = threading.Event()

		self.setup()

	def run(self):
		# Three threads: one listening for updates from the broker, the other listening for updates from the auditors, and main
		# for making decisions one the data coming in from the other threads
		self.auditorListener = threading.Thread(target=self.listenAuditors)
		self.brokerListener = threading.Thread(target=self.listenBroker)

		self.auditorListener.start()
		self.brokerListener.start()

		try:
			while not self.stop_request.isSet():
				#run strategy when either auditors or broker makes an update
				self.update_status.wait()
				self.update_status.clear()
				self.strategy()
		except:
			self.close()
			return

	def listenAuditors(self):
		while not self._stop_listeners.isSet():
			for auditor in self.auditors:
				auditor.waitOnUpdate()
			self.update_status.set()

	def listenBroker(self):
		while not self._stop_listeners.isSet():
			#self.broker.waitOnUpdate()
			#self.update_status.set()
			return

	def close(self, timeout=None):
		self.stop_request.set()
		self._stop_listeners.set()
		self.auditorListener.join()
		self.brokerListener.join()

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
	def strategy(self):
		pass
