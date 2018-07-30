import strategy
import statistics
import sys

class TestStrat(strategy.Strategy):
	def __init__(self):
		super().__init__()


	def setup(self):
		#self.stats_long = statistics.Statistics(10*60)
		#self.registerAuditor(self.stats_long)

		self.stats_short = statistics.Statistics(60*60, 'BTC-USD')
		self.registerAuditor(self.stats_short)

	def strategy(self):
		#print(self.stats_long.mean)
		print(self.stats_short.mean)
		sys.stdout.flush()
		print(self.stats_short.log_mean)
		sys.stdout.flush()

		#if abs(self.stats_long.mean - self.stats_short.mean) < 10.00:
		#	print('buy')
