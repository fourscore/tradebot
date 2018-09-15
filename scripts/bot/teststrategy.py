import strategy
import statistics
from decimal import Decimal
from pymongo import MongoClient

class TestStrat(strategy.Strategy):
	def setup(self):
		self.candle_record = self.dm.newCandleRecord(1*60, 2000, 'BTC-USD')

		self.stats = statistics.Statistics(self.candle_record)
		self.registerAuditor(self.stats)

		self.dmac = 0.0 #definitely not the right term

		self.last_trade = Decimal(0.0)
		self.profit = Decimal(0.0)

		self.ema12_plot = []
		self.ema24_plot = []
		self.mean_plot = []

	def strategy(self):
		ema12 = self.stats.getEMA(12)
		self.ema12_plot.append(ema12)

		ema24 = self.stats.getEMA(24)
		self.ema24_plot.append(ema24)

		self.mean_plot.append(self.stats.mean)

		new_dmac = ema12 - ema24

		with open('dummytrades.txt', 'a') as f:
			if (self.dmac > 0.0) and (new_dmac < 0.0):
				#sell
				f.write("Sold at " + str(self.candle_record.record[-1].current_price) + "\n")

				if self.last_trade != 0.0:
					gain = Decimal(self.candle_record.record[-1].current_price - self.last_trade)
					self.profit += gain

					f.write("Gain: " + str(gain) + "\n")
					f.write("Total profit: " + str(self.profit) + "\n\n")

				self.last_trade = self.candle_record.record[-1].current_price

			if (self.dmac < 0.0) and (new_dmac > 0.0):
				#buy
				f.write("Bought at " + str(self.candle_record.record[-1].current_price)  + "\n")

				self.last_trade = self.candle_record.record[-1].current_price

		self.dmac = new_dmac

	def graph(self):
		import matplotlib.pyplot as plt
		import numpy as np

		client = MongoClient()
		db = client.profitdb

		product_data = db.exch_data.find()

		time = np.array([integer for integer in range(len(self.ema12_plot))])
		product_prices = np.float64([candle['price'] for candle in product_data])
		product_prices = product_prices[0:len(self.ema12_plot)]
		print(len(time))
		print(len(product_prices))
		print(len(self.ema12_plot))
		print(len(self.ema24_plot))
		plt.plot(time, product_prices)
		plt.plot(time, np.float64(self.ema12_plot), 'r')
		plt.plot(time, np.float64(self.ema24_plot), 'b')
		plt.plot(time, np.float64(self.mean_plot[0:len(self.ema12_plot)]), 'g')
		plt.show()
