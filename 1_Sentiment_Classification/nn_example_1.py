import tensorflow as tf
import numpy as np

'''
Use NN to classify a random 0 and 1 list, into 3 classes:

[1, 0, 0] if there are 0, 3, 6, ..., 15 ones in the list
[0, 1, 0] if there are 1, 4, 7, ..., 16 ones in the list
[0, 0, 1] otherwise

After 20,000 epoches, we can get the following result:

Loss:  0.257163
Epoch: 13400, Accuracy
, train acc: 0.953125, test acc: 0.966
Model saved at step 13400
'''


class NN(object):
    def __init__(self, n_input_layer, n_hidden_layer_1, n_hidden_layer_2, n_hidden_layer_3, n_hidden_layer_4,
                 n_output_layer, learning_rate):
        self.n_input_layer = n_input_layer
        self.n_hidden_layer_1 = n_hidden_layer_1
        self.n_hidden_layer_2 = n_hidden_layer_2
        self.n_hidden_layer_3 = n_hidden_layer_3
        self.n_hidden_layer_4 = n_hidden_layer_4
        self.n_output_layer = n_output_layer
        self.learning_rate = learning_rate

        with tf.name_scope("input"):
            self.add_input()

        with tf.name_scope("hidden_1"):
            h1 = self.add_layer(self.xs, self.n_input_layer, self.n_hidden_layer_1, activation=tf.nn.tanh)

        with tf.name_scope("hidden_2"):
            h2 = self.add_layer(h1, self.n_hidden_layer_1, self.n_hidden_layer_2, activation=tf.nn.tanh)

        with tf.name_scope("hidden_3"):
            h3 = self.add_layer(h2, self.n_hidden_layer_2, self.n_hidden_layer_3, activation=tf.nn.tanh)

        with tf.name_scope("hidden_4"):
            h4 = self.add_layer(h3, self.n_hidden_layer_3, self.n_hidden_layer_4, activation=tf.nn.tanh)

        with tf.name_scope("output"):
            self.pred = self.add_layer(h4, self.n_hidden_layer_4, self.n_output_layer, activation=None)

        with tf.name_scope("cost"):
            self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(self.pred, self.ys))
            # self.cost = tf.reduce_mean(-tf.reduce_sum(self.ys * tf.log(self.pred), reduction_indices=[1]))

        with tf.name_scope("train"):
            self.train_op = tf.train.AdamOptimizer(self.learning_rate).minimize(self.cost)

    def add_input(self):
        self.xs = tf.placeholder(tf.float32, [None, self.n_input_layer], name="xs")
        self.ys = tf.placeholder(tf.float32, [None, self.n_output_layer], name="ys")

    def add_layer(self, x, in_size, out_size, activation=None):
        W = tf.Variable(tf.random_normal([in_size, out_size]))
        b = tf.Variable(tf.zeros([out_size]) + 0.1)
        h = tf.matmul(x, W) + b
        h = activation(h) if activation is not None else h
        return h


def get_batch_data(batch_size):
    while True:
        x_batch = []
        y_batch = []
        for i in range(batch_size):
            line = np.random.choice([0, 1], size=(16))
            x_batch.append(line)
            sum = np.sum(line)
            if sum % 3 == 0:
                y = [1, 0, 0]
            elif sum % 3 == 1:
                y = [0, 1, 0]
            else:  # 2
                y = [0, 0, 1]
            y_batch.append(y)
        yield (x_batch, y_batch)


# 几乎和training data 加载方式一样
def get_test_data():
    # load test data
    x_test = []
    y_test = []
    for i in range(1000):
        line = np.random.choice([0, 1], size=(16))
        x_test.append(line)
        sum = np.sum(line)
        if sum % 3 == 0:
            y = [1, 0, 0]
        elif sum % 3 == 1:
            y = [0, 1, 0]
        else:  # 2
            y = [0, 0, 1]
        y_test.append(y)

    return (x_test, y_test)


def comput_acc(pred, target):
    correct = tf.equal(tf.argmax(pred, 1), tf.argmax(target, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))
    return accuracy


def run():
    # model parameters
    n_input_layer = 16
    n_hidden_layer_1 = 10
    n_hidden_layer_2 = 10
    n_hidden_layer_3 = 10
    n_hidden_layer_4 = 10
    n_output_layer = 3  # 3 classes

    # training parameters
    batch_size = 256
    epoch = 20000
    display_step = 200
    learning_rate = 0.01

    model = NN(n_input_layer, n_hidden_layer_1, n_hidden_layer_2, n_hidden_layer_3, n_hidden_layer_4, n_output_layer,
               learning_rate)
    init = tf.global_variables_initializer()

    data = get_batch_data(batch_size)

    x_test, y_test = get_test_data()

    with tf.Session() as sess:
        sess.run(init)

        tf.train.SummaryWriter("logs/", sess.graph)
        saver = tf.train.Saver()

        pre_accuracy = 0
        for i in range(epoch):
            x_batch, y_batch = data.__next__()

            _, train_cost = sess.run([model.train_op, model.cost], feed_dict={model.xs: x_batch, model.ys: y_batch})

            if i % display_step == 0:
                acc = comput_acc(model.pred, model.ys)
                train_acc = sess.run(acc, feed_dict={model.xs: x_batch, model.ys: y_batch})
                test_acc = sess.run(acc, feed_dict={model.xs: x_test, model.ys: y_test})
                print("Loss: ", train_cost)
                print("Epoch: %s, Accuracy\n, train acc: %s, test acc: %s" % (i, train_acc, test_acc))

                # save model
                if test_acc > pre_accuracy:
                    saver.save(sess, "./model/nn_model.ckpt")
                    print("Model saved at step %s" % i)
                    pre_accuracy = test_acc

                print("-" * 50)


if __name__ == '__main__':
    run()
