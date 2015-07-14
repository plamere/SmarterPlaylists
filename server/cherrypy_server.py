import os 
import sys
import cherrypy
from cherrypy import tools
import ConfigParser
import json
import time
import components
import compiler
import pbl
import time

class SmarterPlaylistServer(object):
    def __init__(self):
        pass

    @cherrypy.expose
    @tools.json_out()
    def inventory(self):
        start = time.time()
        print 'inventory'
        results = {
            'status': 'ok',
            'inventory': components.exported_inventory,
            'types': components.inventory['types']
        }
        print 'inventory', time.time() - start
        return results

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    def run(self):
        print 'inventory'
        start = time.time()
        # program = request.json
        print cherrypy.request.headers
        cl = cherrypy.request.headers['Content-Length']
        #rawbody = cherrypy.request.body.read(int(cl))
        program = cherrypy.request.json

        print 'got program', program
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
            results['name'] = obj.name

        results['time'] = time.time() - start
        print 'compiled and executed in', time.time() - start, 'secs'
        if app.trace:
            print json.dumps(results, indent=4)
        print 'run', time.time() - start
        return results
  

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
    cherrypy.response.headers['Content-Type']= 'application/json'

def error_page_404(status, message, traceback, version):
    cherrypy.response.headers['Content-Type']= 'application/json'
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
    results = { 'status' : 'error', 'reason': message}
    return json.dumps(results)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        DEBUG = True

    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)

    config = {
        'global' : {
            'server.socket_host' : '0.0.0.0',
            'server.socket_port' : 5000,
            'server.thread_pool' : 10,
        },
        '/' : {
            'tools.CORS.on' : True,
            'tools.caching.on' : True,
            'error_page.404': error_page_404,
        }
    }
    cherrypy.quickstart(SmarterPlaylistServer(), '/sps', config=config)

