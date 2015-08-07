import sys
import redis
import program_manager
import time
import simplejson as json
import threading
from datetime import datetime

class Scheduler(object):
    
    '''
        constraints - only one scheduled task per item
        squeue - a zset with proc IDs ('process:pid') sorted by excution times
        proces info a hash with
           pid, next exec time, 
            delta, count, error count, consecutive errors count

        process-stats: a list of json results, trimmed to size 10
        sleeper queue

    '''

    def __init__(self, redis, pm):
        self.r = redis
        self.pm = pm
        self.job_queue = 'sched-job-queue'
        self.proc_queue = 'sched-proc-queue'
        self.wait_queue = 'sched-wait-queue'
        self.max_time = 1000000
        self.max_cerrors = 3
        self.max_retained_results = 10

    def schedule(self, auth_code, user, pid, when, delta, total):
        # as a pipleline
        # add schedule to process info hash
        # if count > 0
        #    add proc-id when to squeue
        #    hash proc info to hash (dec count)
        # post to sleeper queue

        skey = mk_sched_key('job', user, pid)
        pipe = self.r.pipeline()
        pipe.hset(skey, 'auth_code', auth_code)
        pipe.hset(skey, 'user', user)
        pipe.hset(skey, 'pid', pid)
        pipe.hset(skey, 'when', when)
        pipe.hset(skey, 'delta', delta)
        pipe.hset(skey, 'total', total)
        pipe.hset(skey, 'runs', 0)
        pipe.hset(skey, 'errors', 0)
        pipe.hset(skey, 'cerrors', 0)
        pipe.execute()
        self.post_job(skey, when)
        return True

    def post_job(self, skey, when):
        print 'posting', skey, 'to run in', when - time.time(), 'secs'
        self.r.zadd(self.job_queue, when, skey)
        self.r.lpush(self.wait_queue, 1)

    def cancel(self, user, pid):
        skey = mk_sched_key('job', user, pid)
        self.r.zrem(self.job_queue, skey)
        self.r.delete(skey)

    def get_run_stats(self, pid):
        skey = mk_sched_key('job', user, pid)
        return self.r.hgetall(skey)

    def get_next_item(self):
        now = self.now()
        items = self.r.zrange(self.job_queue, 0, 0, withscores=True, score_cast_func=int)
        print 'items', items
        if len(items) > 0:
            item = items[0]
            skey, next_time = item
            if now >= next_time:
                self.r.zrem(self.job_queue, skey)
                return skey
        else:
            return None

    def get_next_delta(self):
        now = self.now()
        items = self.r.zrange(self.job_queue, 0, 0, withscores=True, score_cast_func=int)
        if len(items) > 0:
            item = items[0]
            print item
            skey, next_time = item
            return next_time - now
        else:
            return self.max_time
        
    def wait_for_next(self):
        timeout = self.get_next_delta()
        if timeout > 0:
            print 'waiting for', timeout, 'secs'
            self.r.blpop(self.wait_queue, timeout)
        return self.get_next_item()
            
    def execute_job(self, skey):
        results = None
        info = self.r.hgetall(skey)
        print 'execute_job', skey, info
        if info:
            print 'execute_job', info
            auth_code = info['auth_code']
            pid = info['pid']
            results = self.pm.execute_program(auth_code, pid, True)
        return results

    def run_job(self, skey):
        results = self.execute_job(skey)
        print 'run_job', skey, results
        self.process_job_result(skey, results)

    def process_job_result(self, skey, results):
        p = self.r.pipeline()
        p.hincrby(skey, 'runs', 1)
        if results['status'] == 'ok':
            p.hset(skey, 'cerrors', 0)
        else:
            p.hincrby(skey, 'cerrors', 1)
            p.hincrby(skey, 'errors', 1)
        p.hgetall(skey)
        pres = p.execute()
        info = pres[-1]

        cerrors = int(info['cerrors'])
        runs = int(info['runs'])
        delta = int(info['delta'])

        print
        print 'info', info
        print

        user = info['user']
        pid = info['pid']

        results['runtime'] = time.time()
        if cerrors > self.max_cerrors:
            results['info'] = 'max consecutive errors exceeded, job cancelled'
        elif runs >= int(info['total']):
            results['info'] = 'total runs reached, job finished'
        else:
            next_time = self.now() + delta
            next_date= datetime.fromtimestamp(next_time).strftime('%Y-%m-%d %H:%M:%S')
            results['info'] = 'next run at ' + next_date
            self.post_job(skey, next_time)

        ntracks = len(results['tids']) if 'tids' in results else 0
        results['oinfo'] = 'generated ' + str(ntracks) + ' tracks'
        rkey = mk_sched_key('results', user, pid)
        jresults = json.dumps(results, indent=2)
        print jresults
        self.r.lpush(rkey, jresults)
        self.r.ltrim(rkey, 0, self.max_retained_results - 1)


    def now(self):
        return int(time.time())

    def process_job_queue(self):
        # there should only be one thread
        # doing this

        print 'starting job pusher'
        cur_count = self.r.getset('pusher-count', '1')
        if cur_count == '1':
            print 'pusher already running'
            return
            
        try:
            while True:
                skey = self.wait_for_next()
                if skey:
                    print '    pushing', skey
                    self.r.rpush(self.proc_queue, skey)
        finally:
             self.r.set('pusher-count', '0')
             print 'pusher released'


    def process_jobs(self):
        print 'starting job processor'
        while True:
            _,skey = self.r.blpop(self.proc_queue)
            if skey:
                print '   processing', skey
                self.run_job(skey)
            else:
                break
        print 'shutting down job processor'


    def start_processing_threads(self, threads=5):
        def worker():
            self.process_jobs()

        for i in xrange(threads):
            t = threading.Thread(target=worker)
            t.start()
        sched.process_job_queue()
        
def mk_sched_key(op, user, pid):
    return 'sched-' + op + '-' + user + '-' + pid

if __name__ == '__main__':
    import random
    import spotify_auth

    my_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    my_auth = spotify_auth.SpotifyAuth(r=my_redis)
    my_pm = program_manager.ProgramManager(my_auth, r=my_redis)

    sched = Scheduler(my_redis, my_pm)

    threads = 5

    if len(sys.argv) > 1:
        threads = int(sys.argv[1])

    sched.start_processing_threads(threads)

