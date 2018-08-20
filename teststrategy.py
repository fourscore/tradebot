import strategy
import statistics
import sys
from datamanager import CandleRecord

class TestStrat(strategy.Strategy):
	def setup(self):
		self.candle_record = self.dm.newCandleRecord(60, 100, 'BTC-USD')

		self.stats = statistics.Statistics(self.candle_record)
		self.registerAuditor(self.stats)


	def strategy(self):
		print("Mean: " + str(self.stats.mean))
		try:
			print("Volume for 5 minutes: " + str(self.stats.getVolume(5)))
		except Exception as e:
			print('[TEST STRAT] Record not of size yet')
			print(e)

		print("EMA 12: " + str(self.stats.getEMA(12)))
		print("EMA 24: " + str(self.stats.getEMA(24)))

		#sys.stdout.flush()

		#if abs(self.stats_long.mean - self.stats_short.mean) < 10.00:
		#	print('buy')
