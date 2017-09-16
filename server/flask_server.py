import os
from flask import Flask, request, jsonify, send_from_directory
from flask.ext.cors import cross_origin
from werkzeug.contrib.fixers import ProxyFix

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
import sys
import random

app = Flask(__name__)
app.debug = False
app.trace = False
app.testing = False

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
        print 'got program', json.dumps(program, indent=4)
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
    if pid and auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            if pm.delete_program(user, pid):
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

@app.route('/SmarterPlaylists/copy', methods=['POST'])
@cross_origin()
def copy():
    start = time.time()
    results = { }
    js = request.json
    auth_code = js['auth_code']
    pid = js['pid']
    if pid and auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            pid = pm.copy_program(user, pid)
            if pid:
                results['status'] = 'ok'
                results['pid'] = pid
            else:
                results['status'] = 'error'
                results['msg'] = "Can't copy that program"
        else:
            results['status'] = 'error'
            results['msg'] = 'no authorized user'
    else:
        results['status'] = 'error'
        results['msg'] = 'no  pid or auth'

    results['time'] = time.time() - start
    return jsonify(results)

@app.route('/SmarterPlaylists/import', methods=['POST'])
@cross_origin()
def import_program():
    start = time.time()
    results = { }
    js = request.json
    auth_code = js['auth_code']
    pid = js['pid']
    if pid and auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            new_pid = pm.import_program(user, pid)
            if new_pid:
                results['status'] = 'ok'
                results['imported_pid'] = new_pid
            else:
                results['status'] = 'error'
                results['msg'] = "Can't import that program"
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
            print "directory", user
            total, dir = pm.directory(user, start, count)

            if len(dir) > 0:
                pids = [ d['pid'] for d in dir]
                all_ss = scheduler.get_batch_schedule_status(user, pids)
                for d in dir:
                    d['schedule_status'] = all_ss[d['pid']]

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

@app.route('/SmarterPlaylists/system-status')
@cross_origin()
def system_status():
    start_time = time.time()
    results = { }
    sys_status = my_redis.hgetall("system-status")
    if 'maint_mode' in sys_status:
        sys_status['maint_mode'] = sys_status['maint_mode'] == 'true'
    if 'motd_count' in sys_status:
        sys_status['motd_count'] = int(sys_status['motd_count'])
    results['status'] = 'OK'
    results['system_status'] = sys_status
    results['time'] = time.time() - start_time
    return jsonify(results)

@app.route('/SmarterPlaylists/imports')
@cross_origin()
def imports():
    start_time = time.time()
    results = { }

    auth_code = request.args.get('auth_code', '')
    start = request.args.get('start', 0, type=int)
    count = request.args.get('count', 20, type=int)
    if auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            import_pids =  list(pm.get_published_programs())
            total = len(import_pids)
            import_pids = import_pids[start: start + count]

            out = []
            for pid in import_pids:
                info = pm.get_info(pid)
                if info:
                    if not 'imports' in info:
                        info['imports'] = 0
                    info['imports'] = int(info['imports'])
                    info['pid'] = pid
                    out.append(info)

            out.sort(key=lambda info:info['imports'], reverse=True)
            out = out[start:start+count]
            results['status'] = 'ok'
            results['imports'] = out
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

@app.route('/SmarterPlaylists/schedule_status')
@cross_origin()
def schedule_status():
    start_time = time.time()
    results = { }

    auth_code = request.args.get('auth_code', '')
    pid = request.args.get('pid', '')
    if auth_code:
        token = auth.get_fresh_token(auth_code)
        if token:
            user = token['user_id']
            stats = scheduler.get_run_stats(user, pid)
            rlist = scheduler.get_recent_results(user, pid)
            results['status'] = 'ok'
            results['schedule_status'] = stats
            results['recent_results'] = rlist
            results['pid'] = pid
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
            program = pm.get_program(user, pid)
            if program:
                results['status'] = 'ok'
                results['program'] = program
            else:
                results['status'] = 'error'
                results['msg'] = 'no program found'
        else:
            results['status'] = 'error'
            results['msg'] = 'no authorized user'
    else:
        results['status'] = 'error'
        results['msg'] = 'no authorized user'
    results['time'] = time.time() - start_time
    return jsonify(results)

@app.route('/SmarterPlaylists/shared')
@cross_origin()
def shared():
    start_time = time.time()
    results = { }

    pid = request.args.get('pid', None)
    if pid:
        info = pm.get_info(pid)
        if 'shared' in info:
            is_shared =  info['shared'] == 'True'
            if is_shared:
                owner =  info['owner']
                program = pm.get_program(owner, pid)
                if program:
                    results['status'] = 'ok'
                    results['program'] = program
                else:
                    results['status'] = 'error'
                    results['msg'] = 'no program found'
            else:
                results['status'] = 'error'
                results['program'] = 'program is not shared'
        else:
            results['status'] = 'error'
            results['program'] = 'unknown shared program id'
    else:
        results['status'] = 'error'
        results['msg'] = 'no pid'
    results['time'] = time.time() - start_time
    return jsonify(results)

@app.route('/SmarterPlaylists/shared_info')
@cross_origin()
def shared_info():
    start_time = time.time()
    results = { }
    keep_set = set(['name', 'owner', 'description'])

    pid = request.args.get('pid', None)
    if pid:
        info = pm.get_info(pid)
        if 'shared' in info:
            is_shared =  info['shared'] == 'True'
            if is_shared:
                results['status'] = 'ok'
                out = {}
                for k, v in info.items():
                    if k in keep_set:
                        out[k] = v
                results['info'] = out
            else:
                results['status'] = 'error'
                results['program'] = 'program is not shared'
        else:
            results['status'] = 'error'
            results['program'] = 'unknown shared program id'
    else:
        results['status'] = 'error'
        results['msg'] = 'no pid'

    results['time'] = time.time() - start_time
    return jsonify(results)


@app.route('/SmarterPlaylists/publish', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def publish():
    start_time = time.time()

    params = request.json
    auth_code = params['auth_code']
    token = auth.get_fresh_token(auth_code)

    results = { }
    if not token:
        print 'WARNING: bad auth token', auth_code
        results['status'] = 'error'
        results['message'] = 'not authorized'
    else:
        user = token['user_id']
        pid = params['pid']
        share = params['share']
        pm.publish_program(user, pid, share)
        results['status'] = 'ok'

    results['time'] = time.time() - start_time
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


@app.route('/SmarterPlaylists/run', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def run():
    params = request.json
    auth_code = params['auth_code']
    save_playlist = params['save']
    pid = params['pid']
    results = pm.execute_program(auth_code, pid, save_playlist)
    if results['status'] == 'ok':
        tracks = []
        results['tracks'] = tracks
        for i, tid in enumerate(results['tids']):
            if app.trace:
                print i, pbl.tlib.get_tn(tid)
            tracks.append(pbl.tlib.get_track(tid))
    return jsonify(results)

@app.route('/SmarterPlaylists/schedule', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def schedule():
    start = time.time()
    results = {}
    params = request.json
    auth_code = params['auth_code']
    min_delta = 60
    max_total = 100

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
        ok = True

        print 'delta', delta, 'when', when, 'total', total

        if delta != 0 and delta < min_delta:
            results['status'] = 'error'
            results['message'] = "Too frequent a schedule"
            ok = False

        if total > max_total:
            results['status'] = 'error'
            results['message'] = "Too many runs scheduled"
            ok = False

        if ok:
            if delta > 0 and total > 0:
                if scheduler.schedule(auth_code, user, pid, when, delta, total):
                    results['status'] = 'ok'
                else:
                    results['status'] = 'error'
                    results['message'] = "Can't schedule that job"
            else:
                if scheduler.cancel(user, pid):
                    results['status'] = 'ok'
                else:
                    results['status'] = 'error'
                    results['message'] = "Can't cancel that job"

    results['time'] = time.time() - start
    return jsonify(results)

@app.route('/SmarterPlaylists/force_error')
@cross_origin()
def force_error():
    start = time.time()
    results = {
        'status': 'ok',
    }
    bad = {}
    if bad['missing']:
        print "forced error"
    return jsonify(results)

@app.errorhandler(Exception)
def handle_invalid_usage(error):
    print "error", error
    results = { 
        'status': 'internal_error',
        "message": str(error)
    }
    return jsonify(results)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.debug = False
    app.trace = False
    app.wsgi = False
    for arg in sys.argv[1:]:
        if arg == '--debug':
            app.debug = True
        if arg == '--trace':
            app.trace = True
    if app.debug:
        print 'debug  mode'
        app.run(threaded=False, debug=True)
    elif app.wsgi:
        from gevent.wsgi import WSGIServer
        print 'prod  mode'
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
    else:
        app.run(threaded=True, debug=False)
