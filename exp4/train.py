import glob
import os.path
import random
import numpy as np
import tensorflow as tf
from tensorflow.python.framework import graph_util

# 保存训练数据通过瓶颈层后提取的特征向量
TRAIN_FILE = './train_dir/model.pb'
# 处理好之后的数据文件。
INPUT_DATA = 'flower_processed_data.npy'
# inception-v3 模型瓶颈层的节点个数
BOTTLENECK_TENSOR_SIZE = 2048
# 定义神经网路的设置
LEARNING_RATE_BASE = 0.01
LEARNING_RATE_DECAY = 0.99
STEPS = 2000
BATCH = 100
N_CLASSES = 5

def train():
    # 加载预处理好的数据。
    processed_data = np.load(INPUT_DATA)
    # 获取训练数据
    training_images = processed_data[0]
    n_training_example = len(training_images)
    # 获取训练数据对应的类型
    training_labels = processed_data[1]
    #获取验证数据
    validation_images = processed_data[2]
    #获取验证数据类型
    validation_labels = processed_data[3]
    #获取测试数据
    testing_images = processed_data[4]
    #获取测试数据标签
    testing_labels = processed_data[5]

    print("%d training examples, %d validation examples and %d testing examples." % (
        n_training_example, len(validation_labels), len(testing_labels)))
    # 定义喂数据占位张量
    bottleneck_input = tf.placeholder(tf.float32, [None, BOTTLENECK_TENSOR_SIZE],name='BottleneckInputPlaceholder');
    ground_truth_input = tf.placeholder(tf.int64, [None], name='GroundTruthInput')
    # 定义单层全连接神经网络
    with tf.name_scope('output'):
        weights = tf.Variable(tf.truncated_normal([BOTTLENECK_TENSOR_SIZE, N_CLASSES], stddev=0.001))
        biases = tf.Variable(tf.zeros([N_CLASSES]))
        logits = tf.matmul(bottleneck_input, weights) + biases
        final_tensor = tf.nn.softmax(logits, name='prob')
        # 损失
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=ground_truth_input)
    cross_entropy_mean = tf.reduce_mean(cross_entropy)
    global_step=tf.Variable(0,trainable=False)
    learning_rate=tf.train.exponential_decay(LEARNING_RATE_BASE,global_step,len(training_labels)/BATCH,LEARNING_RATE_DECAY)
    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cross_entropy_mean)
    # 正确率
    with tf.name_scope('evaluation'):
        correct_prediction = tf.equal(tf.argmax(final_tensor, 1), ground_truth_input)
        evaluation_step = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    with tf.Session() as sess:
        # 初始化参数
        init = tf.global_variables_initializer()
        sess.run(init)
        start = 0
        end = BATCH
        for i in range(STEPS):
            sess.run(train_step, feed_dict={
                bottleneck_input: training_images[start: end],
                ground_truth_input: training_labels[start: end]})

            if i % 30 == 0 or i + 1 == STEPS:
                validation_accuracy = sess.run(evaluation_step, feed_dict={
                    bottleneck_input: validation_images, ground_truth_input: validation_labels})
                print('Step %d: Validation accuracy = %.1f%%' % (
                    i, validation_accuracy * 100.0))

            start = end
            if start == n_training_example:
                start = 0

            end = start + BATCH
            if end > n_training_example:
                end = n_training_example

        # 在最后的测试数据上测试正确率。
        test_accuracy = sess.run(evaluation_step, feed_dict={
            bottleneck_input: testing_images, ground_truth_input: testing_labels})
        print('Final test accuracy = %.1f%%' % (test_accuracy * 100))
        # 把训练好的模型保存为pb二进制文件，模型加载可以参考data_process.py文件进行重新加载模型
        constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph_def, ["output/prob"])
        with tf.gfile.FastGFile(TRAIN_FILE, mode='wb') as f:
            f.write(constant_graph.SerializeToString())
if __name__ == '__main__':
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    train()
