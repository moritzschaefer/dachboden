#!/usr/bin/env python
import time
import glob
import os
import socket
import logging

from flask import Flask, jsonify, render_template, request

from strob import base

app = Flask(__name__)


DIR = "/home/pi/webserver/strob/pics"

animator = None


@app.route('/strobe', methods=['GET'])
def get_pic():
    last_pic = sorted(glob.glob(DIR + ('/*.rgb')))[-1]
    filename = (request.args.get('filename', None))
    if filename:
        filename = DIR + '/' + filename
    else:
        filename = last_pic
    array = []
    with open(filename) as f:
        for line in f.readlines():
            colors = line.rstrip().split('#')[1:]
            for i, color in enumerate(colors):
                try:
                    array[i].append('#{}'.format(color))
                except IndexError:
                    array.append(['#{}'.format(color)])
    artname = (filename.split('_')[1]).split('.')[0]
    return jsonify({'artname': artname, 'pic': array})


@app.route('/strobe', methods=['POST'])
def save_pic():
    global animator
    timestamp = int(time.time())
    artname = request.json['artname']
    filename = '{}/{}_{}.rgb'.format(DIR, timestamp, artname)
    array = []
    with open(filename, 'w') as f:
        for i in range(32):  # 32 pixelz
            for col in request.json['pic']:
                f.write(col[i])
            f.write('\n')

    if animator:
        animator.stopThread()

    animator = base.main(filename)
    
    return '', 201
    

@app.route('/')
def index():
    names = sorted(os.listdir(DIR), reverse=True)
    name_objects = [{'name': (name.split('_')[1]).split('.')[0], 'filename': name} for name in names]
    return render_template('index.html', names=name_objects)

@app.route('/generate_204')
def generate_204():
    return '', 204

if __name__ == '__main__':
    while True:
        try:
            if app.run(port=80, host='0.0.0.0') == None:
                raise Exception('Finish now!')
        except socket.error as e:
            logging.warn('Socket Error: {}'.format(e))
