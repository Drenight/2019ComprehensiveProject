### 综合项目实践报告二
### github连接https://github.com/Drenight/2019ComprehensiveProject/tree/master/exp2

### 功能要求
- 每个用户必须通过用户名登录系统
- 系统同时支持多个聊天室，每个聊天室支持多人聊天，用户可以选择创建新的、加入或退出已有的聊天室
- 用户在加入已有聊天室时，需要恢复用户在该聊天室历史在线那段时间内的聊天记录

### 技术要求
- 客户端使用websocket，服务端使用tornado，聊天室和聊天记录不需要写入数据库，只需记录在内存中即可

### 客户端
chatrooms.js
```
$(document).ready(function(){
//	xsrf = getCookie("_xsrf");

	setTimeout(requestRoom,100);

	$('#logout').click(function(event){
		jQuery.ajax({
			url:'//localhost:8000/logout',
			type:'GET',
			data:{
//				_xsrf: xsrf,
				user: document.user,
				logout: 'logout'
			},
			datatype: 'json',
			success: function(data,status,xhr){
				window.location.href='http://localhost:8000/login'
			}
		});	
	});

	$('#createRoom').click(function(event){
		jQuery.ajax({
			url:'//localhost:8000/rooms',
			type:'POST',
			data:{
//				_xsrf: xsrf,
				action:'add'
			},	
			dataType:'json',

			beforeSend: function(xhr,settings){
				$(event.target).attr('disabled','disabled');
			},
			success: function(data,status,xhr){
				$(event.target).removeAttr('disabled');
			}
		});
	});
});


function getCookie(name){
	var c = document.cookie.match("\\b"+name+"=([^;]*)\\b");
	return c ? c[1]:undefined;
};

function requestRoom(){

	var host = 'ws://localhost:8000/status';
	var websocket = new WebSocket(host);

	websocket.onopen = function(evt){ };
	websocket.onmessage = function(evt){
		$('#roomCnt').html($.parseJSON(evt.data)['cnt']);
	};
	websocket.onerror = function(evt){ };
};
```
chatroom.html
```
<html>

	<head>
		<title>ChatRoom</title>
		<!DOCTYPE<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"
		type="text/javascript"</script>
		<script src="http://libs.baidu.com/jquery/1.10.2/jquery.min.js"></script>

		<script>
			$(document).ready(function(){
	
				$('#sendMes').click(function(){
					sendText()	
				})

				sender=$("#user").val()
				roomID=$("#roomID").val()

				function requestText(){
					host="ws://localhost:8000/write/?sender=" + sender + "&roomID=" +roomID
					ws=new WebSocket(host);

					ws.onopen = function(event){}
					ws.onmessage = function(event){
						data = $.parseJSON(event.data);
						
						$('#chat').append(data['sender']+":<br>"+data['mes']+"<br>");
					}	
					ws.onerror = function(event){}
				}	
				
				requestText();

				function sendText(){
					ws.send($("#input").val());
				}
			})
		</script>
	</head>
	<body>
		<h1>Chatroom {{roomID}}</h1>
		<h1>Welcome,{{user}}</h1>

		<input type="hidden" value="{{roomID}}" id="roomID">
		<input type="hidden" value="{{user}}" id="user">

		<div id="chat" style="padding:100px;border: 1px solid#888">
		</div>

		<div id="write">
			<input type="text" name="input" id="input">
			<input type="submit" value="write" id="sendMes">	
		</div>

	</body>
</html>

```
index.html
```
<html>
    <head>
        <title>Welcome Back!</title>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"
			type="text/javascript"></script>
		<script src="{{ static_url('scripts/chatrooms.js') }}"
			type="application/javascript"></script>
    </head>
    <body>
        <h1>Welcome back, {{ user }}</h1>

		<div id="log out">
			<p> <input type="submit" value="logout" id="logout" /></p>
		</div>
		
		<div id="rooms">
			<p><input id="createRoom" type="submit" value="create"/></p>
			<p>Rooms:<span id="roomCnt">{{roomCnt}}</span>
		</div>
		
		<div id="enter">
			<form method="post" action="/join">
			<p>enter<br><input type="text" name="roomid"></p>
			<input type="submit" >
			</from>
		</div>

    </body>
</html>
```
login.html
```
<html>
    <head>
        <title>Please Log In</title>
    </head>

    <body>
        <form action="/login" method="POST">
            {% raw xsrf_form_html() %}
            Username: <input type="text" name="username" />
            <input type="submit" value="Log In" />
        </form>
    </body>
</html>
```
### 服务端
```
import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.options
import os.path

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Message:		#消息
	sender=""
	text=""
	roomID=""
	time=""

	def __init__(sender,text,roomID,time):
		self.sender=sender
		self.text=text
		self.roomID=roomID
		self.time=time


###############################################################################

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
#		self.render('index.html', user="self.current_user",roomCnt=roomCnt)

class LogoutHandler(BaseHandler):
	def get(self):		
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
		self.write_message('{"cnt":"%d"}' % count)	

#############################################################################


class chatRoom(object):
	callbacks = {}
	def register(self,callback):
		roomID = str(callback.get_argument("roomID"))
		if roomID in self.callbacks:
			self.callbacks[roomID].append(callback)
		else:
			self.callbacks[roomID]=[callback]	

	def unregister(self,callback):
		roomID = str(callback.get_argument("roomID"))
		self.callbacks[roomID].remove(callback)
	
	def callbackMessage(self,callback,message):
		roomID = str(callback.get_argument("roomID"))
		sender = str(callback.get_argument("sender"))
		message = {
			"mes":message,
			"sender":sender
		}
		self.board(roomID,message)
	def board(self,roomID,message):
		for callback in self.callbacks[roomID]:
			callback.write_message(json.dumps(message))

class JoinHandler(BaseHandler):
	def post(self):
		roomid=self.get_argument("roomid",0)
		self.render('chatroom.html',user=self.current_user,roomID=roomid)


class WriteHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.application.chatRoom.register(self)
	def on_close(self):
		self.application.chatRoom.unregister(self)
	def on_message(self,message):
		self.application.chatRoom.callbackMessage(self,message)

class Application(tornado.web.Application):
	def __init__(self):
		self.rooms = Rooms()
		self.chatRoom = chatRoom()

		settings = {
			"template_path": os.path.join(os.path.dirname(__file__), "templates"),
			"static_path": 'static',
			"cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
#			"xsrf_cookies": True,
			"login_url": "/login"
		}
		handlers = [
			(r'/', WelcomeHandler),
			(r'/login', LoginHandler),
			(r'/logout', LogoutHandler),
			(r'/rooms',RoomsHandler),
			(r'/status',StatusHandler),
			(r'/join',JoinHandler),
			(r'/write/',WriteHandler),
		]

		tornado.web.Application.__init__(self,handlers,**settings)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	application = Application()
	
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
```


