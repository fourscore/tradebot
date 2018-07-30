# all classes that want to to process data over a certain interval must derive from this
# class and override the process() function

from abc import ABCMeta, abstractmethod
from datamanager import Frame
import threading

class Auditor(threading.Thread):
	__metaclass__ = ABCMeta

	def __init__(self, time_length, product):
		super().__init__()
		self.stop_request = threading.Event()
		self.updated = threading.Event()
		self.frame = Frame(time_length, product)
		self.data = []

		self.start()

	def run(self):

		# upon frame update, update data
		# process new statistics
		# notify strategy when done

		while not self.stop_request.isSet():
			self.data = self.frame.get() #waits until new data is ready in frame
			self.process()

			#notify external threads (that are listening) that auditor has updated
			self.updated.set()

	def close(self, timeout=None):
		self.stop_request.set()
		super().join(timeout)

	def getFrame(self):
		return self.frame

	def waitOnUpdate(self, timeout=None):
		self.updated.wait(timeout)
		self.updated.clear()

	@abstractmethod
	def process(self):
		pass
