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
