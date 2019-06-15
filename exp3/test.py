import PIL
from PIL import Image, ImageFilter
import tensorflow as tf

#去除加速sse的warning
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


def imageprepare():

	im = Image.open("in2.png").convert('L')

	tv = list(im.getdata()) #get pixel values
	#normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.我们写的是白底黑字，标准训练的是黑底白字，需要转换
	tva = [ (255-x)*1.0/255.0 for x in tv]

	return tva


def weight_variable(shape):
	initial = tf.truncated_normal(shape, stddev=0.1)
	return tf.Variable(initial)

def bias_variable(shape):
	initial = tf.constant(0.1, shape=shape)
	return tf.Variable(initial)

def conv2d(x, W):
	return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
	return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')   

def main():

	result=imageprepare()

	#详细解释见train.py
	x = tf.placeholder(tf.float32, [None, 784])
	W = tf.Variable(tf.zeros([784, 10]))
	b = tf.Variable(tf.zeros([10]))


	W_conv1 = weight_variable([5, 5, 1, 32])
	b_conv1 = bias_variable([32])
	x_image = tf.reshape(x, [-1,28,28,1])
	h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
	h_pool1 = max_pool_2x2(h_conv1)

	W_conv2 = weight_variable([5, 5, 32, 64])
	b_conv2 = bias_variable([64])
	h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
	h_pool2 = max_pool_2x2(h_conv2)

	W_fc1 = weight_variable([7 * 7 * 64, 1024])
	b_fc1 = bias_variable([1024])
	h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

	keep_prob = tf.placeholder(tf.float32)
	h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

	W_fc2 = weight_variable([1024, 10])
	b_fc2 = bias_variable([10])

	y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
	init_op = tf.global_variables_initializer()

	saver = tf.train.Saver()
	with tf.Session() as sess:
		sess.run(init_op)
		#使用之前保存的模型参数
		saver.restore(sess, "model/model.ckpt")
		prediction=tf.argmax(y_conv,1)
		predint=prediction.eval(feed_dict={x: [result],keep_prob: 1.0}, session=sess)
#		print(predint[0])
		return(predint[0])

#main()
