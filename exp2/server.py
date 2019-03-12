import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
from uuid import uuid4

class ShoppingCart(object):
	totalInventory = 10
	callbacks = []
	carts = {}

	def register(self,callback):
		self.callbacks.append(callback)
	
	def unregister(self,callback):
		self.callbacks.remove(callback)

	def moveItemToCate(self,session):
		if session in self.carts:
			return
		self.carts[session] = True
		self.notifyCallbacks()
	
	def removeItemFromCart(self,session):
		if session not in self.carts:
			return
		del(self.carts[session])
		self.notifyCallbacks()
	
	def notifyCallbacks(self):
		for callback in self.callbacks:
			callback(self.getInventoryCount())
	
	def getInventoryCount(self):
		return self.totalInventory - len(self.carts)

class DetailHandler(tornado.web.RequestHandler):
	def get(self):
		session = uuid4()
		count = self.application.shoppingCart.getInventoryCount()
		self.render("index.html",session=session,count=count)

class CartHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument('action')
		session = self.get_argument('session')

		if not session:
			self.set_status(400)
			return

		if action == 'add':
			self.application.shoppingCart.moveItemToCart(session)
