import strategy
import statistics

class TestStrat(strategy.Strategy):
	def __init__(self):
		super().__init__()
		
		
	def setup(self):
		self.stats_long = statistics.Statistics(45)
		self.registerAuditor(self.stats_long)
		
		self.stats_short = statistics.Statistics(10)
		self.registerAuditor(self.stats_short)
		
	def strategy(self):
		if self.stats_long.mean == self.stats_long.short:
			print('buy')
