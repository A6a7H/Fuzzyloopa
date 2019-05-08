import json
import tensorflow as tf
import numpy as np
from flask import Flask, render_template, request
from Model.Models import CFuzzyloopa
from Preprocessing.Preprocessing import Prepocessing as prep


D = 7
T = 1
ALPHA = 0.01  # learning rate
M = 22


def read_data(path, name, d, t, start, finish):
    series = prep(path, d, t, name)
    series.creat_features()
    series.normalize_features()
    series.creat_target()

    data = np.array(series.features)[:finish]
    lbls = np.array(series.targets)[:finish]

    chkData_new = data[start:finish, :]
    chkLbls_new = lbls[start:finish, :]
    return lbls, chkData_new, chkLbls_new


def read_weights(path):
    with open(path) as json_file:
        data = json.load(json_file)
        ai_algn = data['ai']
        ci_algn = data['ci']
        y_algn = data['y']
    return ai_algn, ci_algn, y_algn


app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')


@app.route('/predict_align/', methods=['POST'])
def go_align():

    start = 2400
    finish = 2600
    ai_algn, ci_algn, y_algn = read_weights('../Weights/Algn_22_1_7_2400_2600.txt')
    lbls, chkData_new, chkLbls_new = read_data('../TimeSeries/Algn.csv', 'Adj Close', D, T, start, finish)
    cfis = CFuzzyloopa(n_inputs=D, n_rules=M, n_output=T, learning_rate=ALPHA, ai=ai_algn, ci=ci_algn, y=y_algn)

    with tf.Session() as sess:
        sess.run(cfis.init_variables)

        all_data = []
        for ch in lbls:
            all_data.append(ch[0])

        val_pred, val_loss = cfis.make_prediction(sess, chkData_new, chkLbls_new)
        prediction = [-1 for i in range(len(all_data) - len(val_pred))]
        for ch in val_pred:
            prediction.append(ch[0])

        labels = [i for i in range(2800)]
        line_labels = labels
        line_values = all_data

    return render_template('plot.html', labels=line_labels, values=line_values, predic=prediction,label_name='Align')

@app.route('/predict_Zuerich/', methods=['POST'])
def go_zuerich():

    ai_Zuerich, ci_Zuerich, y_Zuerich = read_weights('../Weights/Zuerich_22_1_15_2.txt')
    cfis = CFuzzyloopa(n_inputs=D, n_rules=M, n_output=T, learning_rate=ALPHA, ai=ai_Zuerich, ci=ci_Zuerich, y=y_Zuerich)
    lbls, chkData_new, chkLbls_new = read_data('../TimeSeries/zuerich.csv', 'Zuerich', D, T, 2400, 2600)

    with tf.Session() as sess:
        sess.run(cfis.init_variables)

        all_data = []
        for ch in lbls:
            all_data.append(ch[0])

        val_pred, val_loss = cfis.make_prediction(sess, chkData_new)
        prediction = [-1 for i in range(len(all_data) - len(val_pred))]
        for ch in val_pred:
            prediction.append(ch[0])

        labels = [i for i in range(2800)]
        line_labels = labels
        line_values = all_data

    return render_template('plot.html', labels=line_labels, values=line_values, predic=prediction,label_name='Zuerich')


@app.route('/predict_Mackey/', methods=['POST'])
def go_mackey():

    start = 2500
    finish = 2505
    ai_Mackey, ci_Mackey, y_Mackey = read_weights('../Weights/Mackey_22_5_7_2500_2505.txt')
    cfis = CFuzzyloopa(n_inputs=D, n_rules=M, n_output=5, learning_rate=ALPHA, ai=ai_Mackey, ci=ci_Mackey, y=y_Mackey)
    lbls, chkData_new, chkLbls_new = read_data('../TimeSeries/Mackey.csv', 'mackey', D, 5, start, finish)

    with tf.Session() as sess:
        sess.run(cfis.init_variables)

        all_data = []
        for ch in lbls:
            all_data.append(ch[0])

        val_pred = cfis.make_prediction(sess, chkData_new)
        prediction = [-1 for i in range(2300,start)]
        prediction.extend(val_pred[0][:])


        labels = [i for i in range(2300,finish)]
        line_labels = labels
        line_values = all_data[2300:finish]

    return render_template('plot.html', labels=line_labels, values=line_values, predic=prediction,label_name='Zuerich')


if __name__ == '__main__':
    app.run()