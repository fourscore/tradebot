# Statistics module watches for changes in the Ledger it is given and maintains an updated 
# playbook of all of the statistics regard the information in that ledger
#
# The API allows for requests of statistical data

import auditor

class Statistics(auditor.Auditor):
	def _init_(self, time_length):
		super()._init_(time_length)
		
		self.mean = 0
	
	def process(self):
		self.mean = self.calcMean()
		
		if self.mean > 500:
			with open('logs.txt', 'a') as log:
				log.write('\n\nError: statistical calculation error\n'
							+ 'mean: ' + str(self.mean))
				for point in self.data:
					log.write(str(point) + '\n')
			print(self.data)
		print(self.mean)
		
	def calcMean(self):
		mean = 0
		for point in self.data:
			mean = mean +  (float(point['percentage']) * float(point['price']))
		return mean
		