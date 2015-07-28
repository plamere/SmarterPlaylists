import os
from flask import Flask, request, jsonify, send_from_directory
from flask.ext.cors import cross_origin
import json
import components
import compiler
import hashlib
import pbl
import time
import collections
import spotify_auth

app = Flask(__name__)
debug_exceptions = True

auth_directory = '/lab/SmarterPlaylists/auth'
save_directory = '/lab/SmarterPlaylists/shared'

auth = spotify_auth.SpotifyAuth(auth_directory)

@app.route('/SmarterPlaylists/inventory')
@cross_origin()
def inventory():
    start = time.time()
    results = {
        'status': 'ok',
        'inventory': components.exported_inventory,
    }
    print 'inventory', time.time() - start
    return jsonify(results)

@app.route('/SmarterPlaylists/publish', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def publish():
    start = time.time()
    program = request.json
    print 'got program', program
    results = { }
    if (is_valid_program(program)):
        pid = make_pid(program)
        program['extra']['pid'] = pid
        
        path = os.path.join(save_directory, pid + ".json")
        save_program(path, program)
        results['status'] = 'ok'
        results['pid'] = pid
    else:
        results['status'] = 'error'
        results['msg'] = 'bad program'
    return jsonify(results)

def save_program(path, program):
    out = json.dumps(program, indent=2)
    f = open(path, 'w')
    print >>f, out
    f.close()

def make_pid(program):
    js = json.dumps(program)
    md5 = hashlib.md5(js).hexdigest()
    return md5


def is_valid_program(program):
    sections = ['name', 'main', 'components', 'extra']
    for section in sections:
        if not section in program:
            return False
    return True;

@app.route('/SmarterPlaylists/shared')
@cross_origin(allow_headers=['Content-Type'])
def shared():
    pid = request.args.get('pid', '')
    if '..' in pid:
        abort(404)
    return send_from_directory(save_directory, pid + ".json")

@app.route('/SmarterPlaylists/run', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def run():
    start = time.time()
    program = request.json
    print 'got program', program

    results = { }

    try:
        pbl.engine.clearEnvData()
        env = program['env']
        if 'spotify_auth_code' in env:
            auth_code = env['spotify_auth_code']
            if auth_code:
                token = auth.get_fresh_token(auth_code)
                if not token:
                    print 'WARNING: bad auth token', auth_code
                    # maybe we should generate an error here
                    pass
                else:
                    pbl.engine.setEnv('spotify_auth_token', token['access_token'])

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

    pbl.engine.clearEnvData()
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
        app.trace = False
        print 'debug  mode'
        app.run(threaded=True)
    else:
        from gevent.wsgi import WSGIServer
        app.trace = False
        print 'prod  mode'
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()

