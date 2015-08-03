'''
  program manager

'''

import redis
import simplejson as json
import hashlib
import random
import time


'''
    schema:

        programs:

            program:pid json-string

        directory
            directory:user list-of-pids
            

'''

class ProgramManager:

    def __init__(self, r = None):
        if r:
            self.r = r
        else:
            self.r = redis.StrictRedis(host='localhost', port=6379, db=0)

        ''' program looks like

            {
                name: '',
                main:'',
                pid:'',
                components : [],
                extra : {},
                owner: 'plamere',
                uri:  'spotify:plamere:12345678'
                schedule: {
                    enabled: true,
                    start
                },
            }
        '''


    def add_program(self, user, program):
        ''' add the program to the db

            get an id for the program
            save the program to redis
            add the program to the dirctory
            return the id
        '''

        pid = make_pid(program)
        program['pid'] = pid
        program['owner']  = user
        program['uri']  = None
        pkey = mkkey('program', pid)
        self.r.set(pkey, json.dumps(program))

        dirkey = mkkey('directory', user)
        self.r.rpush(dirkey, pid)
        self.add_stat(pid, 'creation_date', int(time.time()))

        return pid
        
    def directory(self, user, start, count):
        dirkey = mkkey('directory', user)
        pids = self.r.lrange(dirkey, start, count - 1)
        pipe = self.r.pipeline()
        for pid in pids:
            pkey = mkkey('program', pid)
            pipe.get(pkey)
        programs = pipe.execute()
        out = []
        total  = self.r.llen(dirkey)
        for p, pid in zip(programs, pids):
            program = json.loads(p)
            info = {
                'name': program['name'],
                #'pid': program['pid'],
                'pid': pid,
                'ncomponents': len(program['components']),
            }

            if 'uri' in program:
                info['uri'] = program['uri']

            info.update(program['extra'])
            info.update(self.get_stats(pid))
            out.append(info)
        return total, out
            

    def get_program(self, pid):
        pkey = mkkey('program', pid)
        val = self.r.get(pkey)
        if val:
            program = json.loads(val)
        else:
            program = None
        return program

    def delete_program(self, user, pid):
        dirkey = mkkey('directory', user)
        removed_count = self.r.lrem(dirkey, 1, pid)
        if removed_count >= 1:
            pkey = mkkey('program', pid)
            self.r.delete(pkey)
        return removed_count >= 1

    def update_program(self, user, program):
        pid = program['pid']
        pkey = mkkey('program', pid)
        self.r.set(pkey, json.dumps(program))

        dirkey = mkkey('directory', user)
        self.r.lrem(dirkey, 1, pid)
        self.r.rpush(dirkey, pid)

    def add_stat(self, pid, key, val):
        pkey = mkkey('program-stats', pid)
        self.r.hset(pkey, key, val)

    def inc_stat(self, pid, key):
        pkey = mkkey('program-stats', pid)
        self.r.hincrby(pkey, key, 1)

    def get_stats(self, pid):
        pkey = mkkey('program-stats', pid)
        stats = self.r.hgetall(pkey)
        out = {}
        for k, v in stats.items():
            out[k] = int(float(v))
        return out

    def share_program(self, user, pid):
        pass

    def unshare_program(self, user, share_id):
        pass

    def schedule_program(self, user, pid):
        pass


def mkkey(type, id):
    return type + ':' + id

def make_pid(program):
    salt = random.randint(0, 1000000)
    js = json.dumps(program) + str(salt)
    md5 = hashlib.md5(js).hexdigest()
    return md5


if __name__ == '__main__':
    import sys
    import pprint

    p = ProgramManager()
    user = sys.argv[1]

    def mk_program():
        return {
            "name": 'tst',
            "main":'main',
            "components" : [],
            "extra" : {},
            "schedule": {
            }
        }

    def show_dir(user):
        for pid in p.directory(user):
            print pid,
            program = p.get_program(pid)
            pprint.pprint(program)
            print



    print 'dir', p.directory(user)

    program = mk_program()
    p.add_program(user, program)
    show_dir(user)




