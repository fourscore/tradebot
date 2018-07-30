# Statistics module watches for changes in the Ledger it is given and maintains an updated
# playbook of all of the statistics regard the information in that ledger
#
# The API allows for requests of statistical data
#
#
#

import auditor
import math

class Statistics(auditor.Auditor):
	def _init_(self, time_length):
		super()._init_(time_length)

		self.mean = 0.0
		self.log_mean = 0.0

	def process(self):
		self.log_mean = self.calcLogMean()
		self.mean = self.calcMean()


	def calcMean(self):
		mean = 0.0
		for point in self.data:
			mean = mean +  (float(point['percentage']) * float(point['price']))
		return mean

	def calcLogMean(self):
		mean = 0.0

		for point in self.data:
			mean = mean +  (float(point['percentage']) * float(point['price']))

		return 10*math.log(mean, 10)
