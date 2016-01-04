import cmd
import redis
import program_manager
import spotify_auth
import simplejson as json
import time
import datetime

class SmarterPlaylistsAdmin(cmd.Cmd):
    job_queue = 'sched-job-queue'
    prompt = "sp% "
    my_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    auth = spotify_auth.SpotifyAuth(r=my_redis)
    pm = program_manager.ProgramManager(auth, r=my_redis)
    skips = set(['auth_code'])

    def do_test(self, line):
        print self.my_redis
        print 'hello world'

    def do_EOF(self, line):
        return True

    def do_users(self, line):
        users = []
        for key in self.my_redis.keys("directory:*"):
            users.append(key.split(':')[1])
        users.sort()
        print ' '.join(users)

    def do_progs(self, line):
        total = 0
        if len(line) == 0:
            users = []
            for key in self.my_redis.keys("directory:*"):
                users.append(key.split(':')[1])
            users.sort()
        else:
            users = line.strip().split()

        for user in users:
            total, progs = self.pm.directory(user, 0, 1000)
            print user, total, 'programs'
            for prog in progs:
                print '   ', prog['pid'], prog['name']
                total += 1

        print total, 'programs, for', len(users), 'users'

    def do_pinfo(self, line):
        for pid in line.strip().split():
            info = self.pm.get_info(pid)
            for key, val in info.items():
                print '   ', key, val
            print

    def do_pstats(self, line):
        for pid in line.strip().split():
            stats = self.pm.get_stats(pid)
            if stats:
                print 'runs:', stats['runs'], '  last run:',  \
                    fmt_time(stats['last_run']), '  created:', fmt_time(stats['creation_date'])
            print

    def do_program(self, line):
        for pid in line.strip().split():
            owner = self.pm.get_info(pid, 'owner')
            program = self.pm.get_program(owner, pid)
            print json.dumps(program, indent=4)

    def do_published(self, line):
        for pid in self.pm.get_published_programs():
            info = self.pm.get_info(pid)
            if info:
                print pid, info['owner'],  info['name']
        print

    def do_jobs(self, line):
        now = time.time()
        print "Jobs in queue", self.my_redis.zcard(self.job_queue)
        long_form = line == '-l'

        items = self.my_redis.zrange(self.job_queue, 0,1000,withscores=True,score_cast_func=int)
        for item in items:
            skey, next_time = item
            print fmt_delta(next_time - now), skey
            if long_form:
                for key, val in self.my_redis.hgetall(skey).items():
                    if key not in self.skips:
                        print "   ", key, val
                print
                
    
def fmt_delta(delta):
    return str(datetime.timedelta(seconds=delta))
            
def mkkey(type, id):
    return type + ':' + id

fmt = "%Y-%m-%d %H:%M:%S"

def fmt_time(tm):
    ftime = time.gmtime(tm)
    return time.strftime(fmt, ftime)

if __name__ == '__main__':
    SmarterPlaylistsAdmin().cmdloop()
