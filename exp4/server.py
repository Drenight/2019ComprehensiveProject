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

import label_image

ans=123

define('port',default=8000,help='run on the given port',type=int)

#初始handle
class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')


class ImageHandler(tornado.web.RequestHandler):
	def post(self):
		pp = self.get_argument('pp')
#pp = pp[1:]
		imgdata = base64.b64decode(pp)
		file = open('qwq.jpg','wb')
		file.write(imgdata)
		file.close()
		
#		time.sleep(5)

		image = Image.open('qwq.jpg')
		resized_image = image.resize((299,299),Image.ANTIALIAS)
		resized_image.save('in.jpg')
		
		im = Image.open('in.jpg')

		time.sleep(5)
		global ans
		ans = label_image.main()
		

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
