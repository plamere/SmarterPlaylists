import cmd
import redis
import program_manager
import spotify_auth
import simplejson as json
import time
import datetime
import collections

class SmarterPlaylistsAdmin(cmd.Cmd):
    job_queue = 'sched-job-queue'
    proc_queue = 'sched-proc-queue'
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
        print "total users:", len(users)

    def do_dir(self, line):
        users = line.strip().split()
        for user in users:
            total, directory = self.pm.directory(user, 0, 10000)
            print 
            print "total programs", total
            for entry in directory:
                print json.dumps(entry, indent=4)

    def do_gstats(self, line):
        stats = self.my_redis.hgetall("global_stats")
        skeys = [key for key in stats.keys()]
        skeys.sort()

        for key in skeys:
            print '  ', key, stats[key]

    def do_redis_stats(self, line):
        print json.dumps(self.my_redis.info(), indent=2)
        print
        for key, val  in self.my_redis.info().items():
            if "memory" in key:
                print "%32.32s %s" % (key, str(val))
        print
        print "dbsize", self.my_redis.dbsize()

    def do_system_status(self, line):
        admin = self.my_redis.hgetall("system-status")
        for k, v in admin.items():
            print k,v

    def do_motd(self, line):
        if len(line) == 0:
            self.do_system_status(line)
        else:
            pipe = self.my_redis.pipeline()
            pipe.hset('system-status', 'motd', line)
            pipe.hincrby('system-status', 'motd_count', 1)
            pipe.execute()

    def do_version(self, line):
        if len(line) == 0:
            self.do_system_status(line)
        else:
            self.my_redis.hset('system-status', 'version', line)

    def do_maint_mode(self, line):
        if len(line) == 0:
            mode = self.my_redis.hget("system-status", "maint_mode")
            print "maint_mode", mode
        else:
            mode = 'true' if line == 'true' else 'false'
            self.my_redis.hset('system-status', 'maint_mode', mode)

    def do_maint_key(self, line):
        if len(line) == 0:
            key = self.my_redis.hget("system-status", "maint_key")
            print "maint_key", key
        else:
            self.my_redis.hset('system-status', 'maint_key', line)

    def do_progs(self, line):
        prog_total = 0
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
                print '   ', prog['pid'], prog['name'], '-', prog['description']
                prog_total += 1

        print prog_total, 'programs, for', len(users), 'users'

    def do_sprogs(self, line):
        """ simple list of progs and descriptions """
        prog_total = 0
        if len(line) == 0:
            users = []
            for key in self.my_redis.keys("directory:*"):
                users.append(key.split(':')[1])
            users.sort()
        else:
            users = line.strip().split()

        for user in users:
            total, progs = self.pm.directory(user, 0, 1000)
            for prog in progs:
                name = prog['name']
                description = prog['description'] if prog['description'] != "my description" else ""
                if "import of" in name:
                    continue
                if "untitled" in name:
                    continue
                print "%s\t%s" %(name, description)

    def do_save_progs(self, line):
        """ this command was used exactly once to move all
            progs from redis to the file based kvstore
        """
        prog_total = 0
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
                print '   ', prog['pid'], prog['name'], '-', prog['description']
                program = self.pm.get_program(user, prog['pid'])
                if program:
                    self.pm.save_program_to_disk(user, program)
                prog_total += 1

        print prog_total, 'programs, for', len(users), 'users'

    def do_purge_progs(self, line):
        """ this command was used exactly once to remove all
            progs from redis (they are now stored on disk)
        """
        purge_total = 0
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
                pid = prog['pid']
                pkey = program_manager.mkprogkey(user, pid)
                print '   ', prog['pid'], prog['name'], '-', prog['description'], pkey
                self.my_redis.delete(pkey)
                purge_total += 1

        print "purged", purge_total, 'programs, for', len(users), 'users'

    def do_show_all_keys(self, line):
        cursor = 0
        which = 0
        while True:
            cursor, keys = self.my_redis.scan(cursor)
            for key in keys:
                # print which, key
                print key
                which += 1
            if cursor == 0:
                break

    def do_purge_info(self, line):
        """ this command was used exactly once to remove all
            progs from redis (they are now stored on disk)
        """
        purge_total = 0
        if len(line) == 0:
            users = []
            for key in self.my_redis.keys("directory:*"):
                users.append(key.split(':')[1])
            users.sort()
        else:
            users = line.strip().split()

        found = 0
        bytes = 0
        for user in users:
            total, progs = self.pm.directory(user, 0, 1000)
            print user, total, 'programs'
            for prog in progs:
                pid = prog['pid']
                pkey = program_manager.mkprogkey(user, pid)
                data = self.my_redis.get(pkey)
                if data:
                    found +=1
                    bytes += len(data)
                print '   ', found, bytes, prog['pid'], prog['name'], '-', prog['description'], pkey
        print "found", found, "progs, with", bytes, "bytes"

    def do_pinfo(self, line):
        for pid in line.strip().split():
            info = self.pm.get_info(pid)
            for key, val in info.items():
                print '   ', key, val
            print

    def do_top_components(self, line):
        if len(line) == 0:
            users = []
            for key in self.my_redis.keys("directory:*"):
                users.append(key.split(':')[1])
            users.sort()
        else:
            users = line.strip().split()

        counter = collections.Counter()
        for i, user in enumerate(users):
            total, progs = self.pm.directory(user, 0, 1000)
            print i, user, total, 'programs'
            for prog in progs:
                #print '   ', prog['pid'], prog['name'], '-', prog['description']
                # print json.dumps(prog)
                program = self.pm.get_program(prog['owner'], prog['pid'])
                #print json.dumps(program, indent=4)
                for name, comp in program['components'].items():
                    type = comp['type']
                    counter[type] += 1

        print
        print "most common components"
        print
        for type, cnt in counter.most_common():
            print cnt, type

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
            if info and 'owner' in info and 'name' in info:
                print pid, info['owner'],  info['name']
        print

    def do_jobs(self, line):
        now = time.time()
        print "Jobs in queue", self.my_redis.zcard(self.job_queue)
        long_form = line == '-l'
        count = 1000
        if line:
            count = int(line)

        items = self.my_redis.zrange(self.job_queue, 0, count,withscores=True,score_cast_func=int)
        for item in items:
            skey, next_time = item
            print fmt_delta(next_time - now), skey
            if long_form:
                for key, val in self.my_redis.hgetall(skey).items():
                    if key not in self.skips:
                        print "   ", key, val
                print
        print 'total jobs', len(items)

    def do_proc_queue(self, line):
        now = time.time()
        print "Jobs in proc queue", self.my_redis.llen(self.proc_queue)
        long_form = line == '-l'
        count = 1000
        if line:
            count = int(line)

        items = self.my_redis.lrange(self.proc_queue, 0, count)
        for item in items:
            print(json.dumps(item, indent=4))

    def do_purge_proc_queue(self, line):
        now = time.time()
        print "Jobs in proc queue", self.my_redis.llen(self.proc_queue)

        while True:
            val = self.my_redis.lpop(self.proc_queue)
            print("popped", val)
            if val is None:
                break
    
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
