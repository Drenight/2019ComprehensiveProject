### 综合项目实践报告１
### github链接https://github.com/Drenight/2019ComprehensiveProject/tree/master/exp1

### 功能要求
- 用户可以使用该程序为某活动设置一、二、三等奖名额以及参与人员名单
- 参与人员奖项不能兼得，每人只有一次中奖机会，每次可以抽取同等奖项的若干位中奖者

### 技术要求
- 客户端采用H5网页，服务端使用Tornado，所有数据可以直接记录在内存中，可以不写入数据库，一次抽取若干名，要求采用Numpy随机函数一次生成

### 客户端
#### index.html
```
<!DOCTYPE html>
<html>
    <head><title>ROLLLLLLL</title></head>
    <body>
        <h1>Enter prize below.</h1>
        <form method="post" action="/roll">
        <p>First_prize<br><input type="text" name="first_prize"></p>
        <p>Second_prize<br><input type="text" name="second_prize"></p>
        <p>Third_prize<br><input type="text" name="third_prize"></p>
		<p>Player<br><input type="text" name="player"></p>
        
<!--		<p>Player<br> 
			<textarea tows=4 cols=55 name='player'></textarea></p>
		
-->			
		<input type="submit">
        </form>
    </body>
</html>
```

#### final.html
```
<!DOCTYPE html>
<html>
    <head><title>Winner</title></head>
    <body>
        <h1>Winner</h1>
        <p>一等奖{{fp}}</p>
		<p>二等奖{{sp}}</p>
		<p>三等奖{{tp}}</p>
    </body>
</html>
```

### 服务端
#### server.py
```
import os.path
import numpy

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define,options
define('port',default=8000,help='run on the given port',type=int)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')

class RollHandler(tornado.web.RequestHandler):
	def post(self):
		player_text = self.get_argument('player')
		player=list(player_text.split(' '))

		fp = int(self.get_argument('first_prize'))
		sp = int(self.get_argument('second_prize'))
		tp = int(self.get_argument('third_prize'))

#		self.render('final.html',player=player)
		tot = len(player)
		now = tot
			
		fpplayer=list()
		spplayer=list()
		tpplayer=list()
		
		winner=set()

		while(now > 0 and fp>0):

			ind=int(numpy.random.uniform(0,tot))
			if(ind in winner):
				continue
			winner.add(ind)
			fpplayer.append(player[ind])
			now=now-1
			fp=fp-1

		while(now > 0 and sp>0):
			ind=int(numpy.random.uniform(0,tot))
			if(ind in winner):
				continue
			winner.add(ind)
			spplayer.append(player[ind])
			now=now-1
			sp=sp-1
		
		while(now > 0 and tp>0):
			ind=int(numpy.random.uniform(0,tot))
			if(ind in winner):
				continue
			winner.add(ind)
			tpplayer.append(player[ind])
			now=now-1
			tp=tp-1
		
		self.render('final.html',fp=fpplayer,sp=spplayer,tp=tpplayer)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[
			(r'/',IndexHandler),
			(r'/roll',RollHandler)
		]
#		template_path = os.path.join(os.path.dirname(__file__),"templates")		
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
```
