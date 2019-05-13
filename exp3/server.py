import os.path
import numpy
import base64

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from PIL import Image
import time

from tornado.options import define,options

import test

ans=123

define('port',default=8000,help='run on the given port',type=int)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')

class ImageHandler(tornado.web.RequestHandler):
	def post(self):
		pp = self.get_argument('pp')
		imgdata = base64.b64decode(pp)
		file = open('tst.png','wb')
		file.write(imgdata)
		file.close()

		image = Image.open('tst.png')
		resized_image = image.resize((28,28),Image.ANTIALIAS)
		resized_image.save('in.png')
		
		im = Image.open('in.png')
		x,y=im.size
		p=Image.new('RGBA',im.size,(255,255,255))
		p.paste(im,(0,0,x,y),im)
		p.save('in2.png')

		time.sleep(5)
		global ans
		ans = test.main()
		

class AnsHandler(tornado.web.RequestHandler):
	def get(self):
		global ans
		self.render('ans.html',ans=ans)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[
			(r'/',IndexHandler),
			(r'/img',ImageHandler),
			(r'/ans',AnsHandler),
		]	
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
