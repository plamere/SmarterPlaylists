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
import plugs
import pprint
import program_manager
import redis
import scheduler

app = Flask(__name__)

my_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
auth = spotify_auth.SpotifyAuth(r=my_redis)
pm = program_manager.ProgramManager(auth, r=my_redis)
scheduler = scheduler.Scheduler(my_redis, pm)

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

@app.route('/SmarterPlaylists/save', methods=['POST'])
@cross_origin()
def save():
    start = time.time()
    results = { }
    js = request.json
    if 'auth_code' in js:
        program = js['program']
        auth_code = js['auth_code']
        token = auth.get_fresh_token(auth_code)
        user = token['user_id']
        print 'got program', program
        if 'pid' in program:
            print 'got pid', program['pid']
        if is_valid_program(program):
            if 'pid' in program:
                pid = program['pid']
                pm.update_program(user, program)
            else:
                pid = pm.add_program(user, program)
            results['status'] = 'ok'
            results['pid'] = pid
        else:
            results['status'] = 'error'
            results['msg'] = 'bad program'
    else:
        results['status'] = 'error'
        results['msg'] = 'no authorized user'

    results['time'] = time.time() - start
    return jsonify(results)

@app.route('/SmarterPlaylists/delete', methods=['POST'])
@cross_origin()
def delete():
    start = time.time()
    results = { }
    js = request.json
    auth_code = js['auth_code']
    pid = js['pid']
    #auth_code ='asdf'
    #pid ='123'
    print 'delete', pid
    print auth_code
    if pid and auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            if pm.delete_program(user, pid):
                print 'deleted', user, pid
                results['status'] = 'ok'
            else:
                results['status'] = 'error'
                results['msg'] = 'program not found or not owned by user'
        else:
            results['status'] = 'error'
            results['msg'] = 'no authorized user'
    else:
        results['status'] = 'error'
        results['msg'] = 'no  pid or auth'
        
    results['time'] = time.time() - start
    return jsonify(results)

@app.route('/SmarterPlaylists/directory')
@cross_origin()
def directory():
    start_time = time.time()
    results = { }

    auth_code = request.args.get('auth_code', '')
    start = request.args.get('start', 0, type=int)
    count = request.args.get('count', 20, type=int)
    if auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            total, dir = pm.directory(user, start, count)
            results['status'] = 'ok'
            results['programs'] = dir
            results['total'] = total
            results['start'] = start
            results['count'] = count
        else:
            results['status'] = 'error'
            results['msg'] = 'no authorized user'
    else:
        results['status'] = 'error'
        results['msg'] = 'no authorized user'
    results['time'] = time.time() - start_time
    return jsonify(results)

@app.route('/SmarterPlaylists/program')
@cross_origin()
def program():
    start_time = time.time()
    results = { }

    auth_code = request.args.get('auth_code', None)
    pid = request.args.get('pid', None)
    if pid and auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            program = pm.get_program(pid)
            results['status'] = 'ok'
            results['program'] = program
        else:
            results['status'] = 'error'
            results['msg'] = 'no authorized user'
    else:
        results['status'] = 'error'
        results['msg'] = 'no authorized user'
    results['time'] = time.time() - start_time
    return jsonify(results)


@app.route('/SmarterPlaylists/publish', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def publish():
    # TODO fix this
    start = time.time()
    program = request.json
    print 'got program', program
    results = { }
    if is_valid_program(program):
        pid = make_pid(program)
        program['extra']['pid'] = pid
        
        # path = os.path.join(save_directory, pid + ".json")
        results['status'] = 'ok'
        results['pid'] = pid
    else:
        results['status'] = 'error'
        results['msg'] = 'bad program'
    return jsonify(results)

@app.route('/SmarterPlaylists/user_info')
@cross_origin()
def user_info():
    auth_code = request.args.get('auth_code', '')

    results = { }
    token = auth.get_fresh_token(auth_code)
    if token:
        info = {
            'user_id' : token['user_id'],
            'user_name' : token['user_name'],
        }
        results['status'] = 'ok'
        results['user_info'] = info
    else:
        results['status'] = 'error'
        results['msg'] = 'unknown auth code'
    return jsonify(results)

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
    params = request.json
    auth_code = params['auth_code']
    save_playlist = params['save']
    pid = params['pid']
    print 'running', pid
    results = pm.execute_program(auth_code, pid, save_playlist)
    if results['status'] == 'ok':
        tracks = []
        results['tracks'] = tracks
        print
        for i, tid in enumerate(results['tids']):
            print i, pbl.tlib.get_tn(tid)
            tracks.append(pbl.tlib.get_track(tid))
    if app.trace:
        print json.dumps(results, indent=4)
    return jsonify(results)

@app.route('/SmarterPlaylists/schedule', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def schedule():
    start = time.time()
    results = {}
    params = request.json
    auth_code = params['auth_code']

    token = auth.get_fresh_token(auth_code)
    if not token:
        print 'WARNING: bad auth token', auth_code
        results['status'] = 'error'
        results['message'] = 'not authorized'
    else:
        user = token['user_id']
        pid = params['pid']
        when = params['when']
        delta = params['delta']
        total = params['total']
        if scheduler.schedule(auth_code, user, pid, when, delta, total):
            results['status'] = 'ok'
        else:
            results['status'] = 'error'
            results['message'] = "Can't schedule that job"

    results['time'] = time.time() - start
    return jsonify(results)

def old_run():
    start = time.time()
    params = request.json
    pprint.pprint(params)
    pid = params['pid']
    auth_code = params['auth_code']
    save_playlist = params['save']
    print 'running', pid

    program = pm.get_program(pid)
    pprint.pprint(program)

    results = { }

    try:
        pbl.engine.clearEnvData()
        token = auth.get_fresh_token(auth_code)
        if not token:
            print 'WARNING: bad auth token', auth_code
            results['status'] = 'error'
            results['message'] = 'not authorized'
        else:
            delta = token['expires_at'] - time.time()
            print 'cur token expires in', delta, 'secs'
            print 'token', token
            user = token['user_id']
            pbl.engine.setEnv('spotify_auth_token', token['access_token'])
            pbl.engine.setEnv('spotify_user_id', token['user_id'])

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

                print 'SAVE to Spotify', save_playlist
                if save_playlist:
                    uri = pm.get_info(pid, 'uri')
                    new_uri = plugs.save_to_playlist(program['name'], uri, tids)
                    if uri != new_uri:
                        pm.add_info(pid, 'uri', new_uri)
                    if new_uri:
                        results['uri'] = new_uri
                    else:
                        results['status'] = 'error'
                        results['message'] = "Can't save playlist to Spotify"
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

    pm.add_stat(pid, 'last_run', time.time());
    if results['status'] == 'ok':
        pm.inc_stat(pid, 'runs');
    else:
        pm.inc_stat(pid, 'errors');

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


