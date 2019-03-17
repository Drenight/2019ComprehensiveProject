import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.options
import os.path
import json

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

room = [list() for i in range(100)]		#最大100个聊天室
inRoom = dict()							#查询usr在哪个聊天室


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.redirect("/")

class WelcomeHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		roomCnt = self.application.rooms.getRooms()
		self.render('index.html', user=self.current_user,roomCnt=roomCnt)

class LogoutHandler(BaseHandler):
	def get(self):
		if (self.get_argument("logout", None)):
			if self.current_user in inRoom:
				room[inRoom[self.current_user]].remove(self.current_user)
			
			self.clear_cookie("username")
			self.redirect("/")
##############################################################################

class Rooms(object):
	cnt = 0
	callbacks = []
	def register(self,callback):
		self.callbacks.append(callback)
	def unregister(self,callback):
		self.callbacks.remove(callback)
	def addRoom(self):
		self.cnt+=1
		self.notifyCallbacks()

	def notifyCallbacks(self):
		for callback in self.callbacks:
			callback(self.getRooms())
	def getRooms(self):
		return self.cnt

class RoomsHandler(tornado.web.RequestHandler):
	def post(self):
		action = self.get_argument('action')
		
		if action == 'add':
			self.application.rooms.addRoom()
		else:
			self.set_status(400)
		
class StatusHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.application.rooms.register(self.callback)
	def on_close(self):
		self.application.rooms.unregister(self.callback)
	def on_message(self,message):
		pass
	def callback(self,count):
		self.write_message('{"roomCnt":"%d"}' % count)	

#############################################################################

class JoinHandler(BaseHandler):
	def get(self):
		roomid = self.get_argument("roomid",0)
		room[roomid].append(self.current_user)

		self.render('chatroom.html',user=self.current_user)

class Application(tornado.web.Application):
	def __init__(self):
		self.rooms = Rooms()
		
		settings = {
			"template_path": os.path.join(os.path.dirname(__file__), "templates"),
			"static_path": 'static',
			"cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
			"xsrf_cookies": True,
			"login_url": "/login"
		}
		handlers = [
			(r'/', WelcomeHandler),
			(r'/login', LoginHandler),
			(r'/logout', LogoutHandler),
			(r'/rooms',RoomsHandler),
			(r'/status',StatusHandler),
			(r'/join',JoinHandler),
		]

		tornado.web.Application.__init__(self,handlers,**settings)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	application = Application()
	
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
