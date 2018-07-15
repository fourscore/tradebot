# manages the buying and selling of coin on GDAX
# Creates orders, sends them to authenticated client
# Manages order book of all orders on the market
#
# Records closed orders to the database

import gdax
import threading
import time, json
import decimal
		

# Use this class to maintain an update list of your open orders on the market
class OrderBook:
	def __init__(self):
		self.open_orders = []
		
	def record(self, order_msg):
		for order in self.open_orders:
			#update order:
		

class UserChannel(gdax.WebsocketClient):
	def __init__(self, acc):
		super().__init__()
		self.url = acc['ch_url']
		self.api_key = acc['key']
		self.api_secret = acc['secret']
		self.api_passphrase = acc['passphrase']
		
		self.products = ['BTC-USD']
		self.channels = ["user"]
		self.auth = True
			
	def on_open(self):
		print('User channel opened')

	def on_message(self, message):
		with open('OrderReplies.txt', 'a+') as ref:
			for item in message:
				ref.write(str(item) + '\n')
			ref.write('\n')	
		print(message)
	
	def on_close(self):
		print('User channel closed')
		
		

class Broker:
	def __init__(self, acc):
	
		#set up authenticated client
		auth_client = gdax.AuthenticatedClient(acc['key'], acc['secret'], acc['passphrase'],
                                  api_url=acc['auth_url'])
		
		#user channel (for responses)
		user_channel = UserChannel(acc)
		
		user_channel.start()
		try:
			time.sleep(10*60)
		except: pass
		
		print(auth_client.buy(price='10',product_id='BTC-USD', type='market'))
		user_channel.close()
	
	def sell(self):
		# post sell to exchange with given parameters
		# if successful, record it in order book and return true
		# else return false
	
	def buy(self):
		# post buy to exchange with given parameters
		# if successful, record it in order book and return true
		# else return false
		
	def cancel_order(self):
		#get size of order left
		#cancel order
		#if cancel successful, return size left
		#else return zero
		
	
		
		
if __name__ == '__main__':

	with open('account.json') as f:
		accs = json.loads(f.read())
		
	
	acc = accs['sandbox']
	broker = Broker(acc)
	