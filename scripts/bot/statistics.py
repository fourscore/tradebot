# Statistics module watches for changes in the Ledger it is given and maintains an updated
# playbook of all of the statistics regard the information in that ledger
#
# The API allows for requests of statistical data
#
#
#

import auditor
import math
from datamanager import Frame, CandleRecord
from decimal import Decimal

class Statistics(auditor.Auditor):
	def __init__(self, source):
		#enforce use of candle records
		if type(source) != CandleRecord:
			raise Exception('[SATISTICS] Statistics auditor requires source of type CandleRecord')

		super().__init__(source)

		self.mean = Decimal(0.0)
		self.ema = Decimal(0.0)

	#things to be calculated on every receipt of data should be included in this function
	def process(self):
		self.mean = self.calcMean()


	def calcMean(self):
		mean = Decimal(0.0)
		for candle in self.data:
			if not candle.close:
				mean += candle.current_price
			else:
				mean += candle.close
		return mean/len(self.data)

	#sizes: list of
	def getEMA(self, size):
		mult = Decimal(2/(size + 1))
		ema = self.mean
		for candle in self.data:
			ema = Decimal((candle.current_price - ema) * mult + ema)
		return ema



	#num_candles: how many candles to include in calculations
	def getVolume(self, num_candles):
		if num_candles > len(self.data): raise Exception("[STATISTICS] Error in calculating volume: requested candles excedes candle record size")

		volume = Decimal(0.0)
		for iter in range(-1,-1*num_candles,-1): volume += self.data[iter].volume
		return volume
