# manages the buying and selling of coin on GDAX
# Creates orders, sends them to authenticated client
# Manages order book of all orders on the market
#
# Records closed orders to the database

import gdax
import threading
import time, json
from decimal import Decimal
import requests
import hmac
import hashlib
from pymongo import MongoClient
from gdax_auth import GdaxAuth

# Use this class to maintain an update list of your open orders on the market
# An order book is kept as such:
#	open_orders = {
#	<first order id>: [
#						{
#							<original gdax response to order submission>
#						},
#						{
#							<match message 1>
#						},
#						{
#							<match message 2>
#						}
#						.
#						.
#						.
#						{
#							<match message n>
#						}
#					]
#	<second order id>: {
#						.
#						.
#						.
#					}
#				}
# When message is of type 'done', order in open_orders corresponding to the
# the message is disregarded
#
# Messages of type 'match' are stored to the database

class OrderBook:
	def __init__(self):
		self.open_orders = {}
		self.last_order = None

		client = MongoClient('localhost', 27017)
		self.db = client.profitdb


	def record(self, order_msg):
		print('Recording an order update. New order book: ')
		print(self.open_orders)

		try:
			#match replies have taker_order_id and maker_order_id
			if order_msg['type'] == 'match':
				#find if order_id is a taker or maker
				if order_msg['taker_order_id'] in self.open_orders:
					order_id = order_msg['taker_order_id']
					self.open_orders[order_id].append(order_msg)
				elif order_msg['maker_order_id'] in self.open_orders:
					order_id = order_msg['maker_order_id']
					self.open_orders[order_id].append(order_msg)

				self.db.tradehist.insert(self.open_orders[order_id])
			elif order_msg['type'] == 'received':
				order_id = order_msg['order_id']
				self.last_order = order_id
				self.open_orders[order_id] = [order_msg]
				print(self.open_orders)
			else:
				order_id = order_msg['order_id']

				if order_msg['type'] != 'done':
					self.open_orders[order_id] = order_msg
				else:
					del self.open_orders[order_id]


		except Exception as e:
			#print("Disregarding message that does not contain an order id")
			print(e)

		return

	def get_last_order():
		return self.open_orders[self.last_order]

class UserChannel(gdax.WebsocketClient):
	def __init__(self, acc, order_book):
		super().__init__()
		self.url = acc['ch_url']
		self.api_key = acc['key']
		self.api_secret = acc['secret']
		self.api_passphrase = acc['passphrase']

		self.order_book = order_book
		self.products = ['BTC-USD']
		self.channels = ["user"]
		self.auth = True

		self.order_filled = threading.Event()

	def on_open(self):
		print('User channel opened')

	def on_message(self, message):
		with open('OrderReplies.txt', 'a+') as ref:
		   for item in message:
			   ref.write(str(item) + '\n')
		   ref.write('\n')

		self.order_book.record(message)


		if (message['type'] == "pending"):
		   self.order_filled.set()



	def on_close(self):
		print('User channel closed')



class Broker():
	def __init__(self, acc):
		self.auth_client = gdax.AuthenticatedClient(acc['key'], acc['secret'], acc['passphrase'], api_url=acc['auth_url'])
		self.auth = GdaxAuth(acc['key'], acc['secret'], acc['passphrase'])
		self.order_book = OrderBook()

		#user channel (for responses)
		self.user_channel = UserChannel(acc, self.order_book)

		self.user_channel.start()

	def get_account(self, account_id):
		r = requests.get(self.auth_client.url + '/accounts/' + account_id, auth=self.auth, timeout=30)
		return r.json()

	def sell(self):
		# post sell to exchange with given parameters
		# if successful, record it in order book and return true
		# else return false

		account_id = ""
		price = 10
		size = .001
		product_id = 'BTC-USD'

		data = {
			'price': price,
			'size': size,
			'side': 'buy',
			'product_id': product_id
		}

		current_balance = self.get_account(account_id)['balance']
		print(current_balance)

		if (price * size < Decimal(current_balance)):

		  route = self.auth_client.url + '/orders'
		  r = requests.post(route, data=json.dumps(data), auth=self.auth, timeout=30)

		  print(r.json())
		  self.order_book.record(r.json())

		return

	def buy(self, **kwargs):
		# post buy to exchange with given parameters
		# if successful, record it in order book and return true
		# else return false
		account_id = "585d0d0c-719a-4bb2-aaa6-73e5c03ed458"
		price = 10
		size = .001
		product_id = 'BTC-USD'

		# Dummy dictionary of data,
		data = {
			'price': price,
			'size': size,
			'side': 'buy',
			'product_id': product_id
		}


		current_balance = self.get_account(account_id)['balance']
		print(current_balance)

		if (price * size < Decimal(current_balance)):

			route = self.auth_client.url + '/orders'
			r = requests.post(route, data=json.dumps(data), auth=self.auth, timeout=30)

			print(r.json())
			self.order_book.record(r.json())

		# purchases will go into a google sheet

		return

	def cancel_order(self):
		#get size of order left
		#cancel order
		#if cancel successful, return size left
		#else return zero
		return

	def get_last_order(self):
		return self.order_book.get_last_order()

	def wait_on_event(self):
		self.user_channel.order_filled.wait()

	def destroy(self):
		self.user_channel.close()


if __name__ == '__main__':

	with open('accounts.json') as f:
		accs = json.loads(f.read())


	acc = accs['sandbox']
	broker = Broker(acc)
