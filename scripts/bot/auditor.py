# all classes that want to to process data over a certain interval must derive from this
# class and override the process() function
#
# params:
#		source - object that provides a get() method that waits for event, and on event,
#				returns some data. These could be Frame(s) or CandleRecord(s)

from abc import ABCMeta, abstractmethod
from datamanager import Frame
import threading

class Auditor(threading.Thread):
	__metaclass__ = ABCMeta

	def __init__(self, source):
		super().__init__()
		print('[AUDITOR] Creating auditor with source of type ' + str(type(source)))
		self.stop_request = threading.Event()
		self.updated = threading.Event()
		self.source = source
		self.data = []

		self.start()
		print('[AUDITOR] Auditor launched')

	def run(self):

		# upon source update, update data
		# process new statistics
		# notify strategy when done

		while not self.stop_request.isSet():
			self.data = self.source.get() #waits until new data is ready in source
			self.process()

			#notify external threads (that are listening) that auditor has updated
			self.updated.set()

	def close(self, timeout=None):
		self.stop_request.set()
		super().join(timeout)

	def getSource(self):
		return self.source

	def waitOnUpdate(self, timeout=None):
		self.updated.wait(timeout)
		print('[AUDITOR] Recieved update')
		self.updated.clear()

	@abstractmethod
	def process(self):
		pass
