import os
from flask import Flask, request, jsonify
import json
import components
import compiler
import pbl
import time

app = Flask(__name__)

@app.route('/inventory')
def inventory():
    results = {
        'status': 'ok',
        'inventory': components.exported_inventory
    }
    return jsonify(results)

@app.route('/run', methods=['GET', 'POST'])
def run():
    start = time.time()
    program = request.json
    status, obj = compiler.compile(program)

    print 'compiled in', time.time() - start, 'secs'

    if 'max_tracks' in program:
        max_tracks = program['max_tracks']
    else:
        max_tracks = 40

    results = { 'status': status}

    if status == 'ok':
        tracks = []
        tids = pbl.get_tracks(obj, max_tracks)
        print
        for i, tid in enumerate(tids):
            print i, pbl.tlib.get_tn(tid)
            tracks.append(pbl.tlib.get_track(tid))
        print
        results['tracks'] = tracks

    results['time'] = time.time() - start
    print 'compiled and executed in', time.time() - start, 'secs'
    return jsonify(results)
    

if __name__ == '__main__':
    if os.environ.get('PBL_NO_CACHE'):
        app.debug = True
        print 'debug  mode'
    else:
        print 'prod  mode'
    app.run()
