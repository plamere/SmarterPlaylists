import os
from flask import Flask, request, jsonify
from flask.ext.cors import CORS, cross_origin
import json
import components
import compiler
import pbl
import time

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

debug_exceptions = False


@app.route('/sps/inventory')
@cross_origin()
def inventory():
    start = time.time()
    results = {
        'status': 'ok',
        'inventory': components.exported_inventory,
    }
    print 'inventory', time.time() - start
    return jsonify(results)

@app.route('/sps/run', methods=['GET', 'POST'])
@cross_origin()
def run():
    start = time.time()
    program = request.json
    print 'got program', program

    results = { }

    try:
        status, obj = compiler.compile(program)
        print 'compiled in', time.time() - start, 'secs'

        if 'max_tracks' in program:
            max_tracks = program['max_tracks']
        else:
            max_tracks = 40

        results['status'] = status

        if status == 'ok':
            results['name'] = obj.name
            tids = pbl.get_tracks(obj, max_tracks)

            tracks = []
            results['tracks'] = tracks
            print
            for i, tid in enumerate(tids):
                print i, pbl.tlib.get_tn(tid)
                tracks.append(pbl.tlib.get_track(tid))
            print
        else:
            results['status'] = 'error'
            results['message'] = status

    except pbl.PBLException as e:
        if debug_exceptions:
            raise
        results['status'] = 'error'
        results['message'] = e.reason
        if e.component:
            cname = program['hsymbols'][e.component]
        else:
            cname = e.cname
        results['component'] = cname

    except Exception as e:
        if debug_exceptions:
            raise
        results['status'] = 'error'
        results['message'] = str(e)

    results['time'] = time.time() - start
    print 'compiled and executed in', time.time() - start, 'secs'
    if app.trace:
        print json.dumps(results, indent=4)
    print 'run', time.time() - start, results['status']
    return jsonify(results)
  
#@app.errorhandler(Exception)
def handle_invalid_usage(error):
    start = time.time()
    print error
    results = { 'status': 'exception: '  + str(error)}
    print 'invalid usage', time.time() - start
    return jsonify(results)

if __name__ == '__main__':
    if os.environ.get('PBL_NO_CACHE'):
        app.debug = True
        app.trace = True
        print 'debug  mode'
        app.run(threaded=True)
    else:
        from gevent.wsgi import WSGIServer
        app.trace = False
        print 'prod  mode'
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
