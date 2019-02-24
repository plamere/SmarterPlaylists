import sys
import redis
import json
import datetime


max_days_to_keep = 30

r = redis.StrictRedis(host='localhost', port=6379, db=0)

unexpired_byte_count = 0
expired_byte_count = 0
total_byte_count = 0


total_jobs = 0
removed_jobs = 0
trimmed_jobs = 0
keep_all_jobs = 0

MAX_AGE_RESULTS = 30 * 24 * 60 * 60

def trim_results(name):
    global total_jobs, removed_jobs, trimmed_jobs, keep_all_jobs
    results = r.lrange(name, 0, 100)
    last_result_to_keep = -1
    total_jobs += 1
    for i, js in enumerate(results):
        results = json.loads(js)
        # print name, i,  fmt_date(results['runtime'])
        age = get_age(results['runtime'])
        if age < max_days_to_keep:
            last_result_to_keep = i
        else:
            break
    if last_result_to_keep == -1:
        removed_jobs += 1
        r.delete(name)
    else:
        r.ltrim(name, 0, last_result_to_keep)
        trimmed_jobs += 1

    print "%d %s %4d %8d %8d %8d %8d" % (i, fmt_date(results['runtime']), get_age(results['runtime']), total_jobs, removed_jobs, trimmed_jobs, keep_all_jobs)

def count_results(name):
    global total_byte_count, expired_byte_count, unexpired_byte_count
    results = r.lrange(name, 0, 100)
    for i, js in enumerate(results):
        total_byte_count += len(js)
        results = json.loads(js)
        # print name, i,  fmt_date(results['runtime'])
        age = get_age(results['runtime'])
        if age < max_days_to_keep:
            unexpired_byte_count += len(js)
        else:
            expired_byte_count += len(js)
    print "%d %s %4d %8d %8d %8d" % (i, fmt_date(results['runtime']), get_age(results['runtime']), unexpired_byte_count, expired_byte_count, total_byte_count)

def show_results(name):
    results = r.lrange(name, 0, 100)
    ttl = r.ttl(name)
    for i, js in enumerate(results):
        results = json.loads(js)
        # print json.dumps(results, indent=4)
        print "TTL", ttl
        show_result(results)

def expire_key(name):
    r.expire(name, MAX_AGE_RESULTS)


def show_result(result):
    print "%s %s %.2f" % (result['status'], fmt_date(result['runtime']), result['time'])
    print result['oinfo']
    print result['info']
    if result['status'] == 'ok':
        print result['name']
        print result['uri']
    else:
        print result['message']
    print

def fmt_date(ts):
    date = datetime.date.fromtimestamp(ts)
    return date.strftime("%Y-%m-%d")

def get_age(ts):
    date = datetime.date.fromtimestamp(ts)
    now = datetime.date.today()
    delta = now - date
    return delta.days
    

def trim():
    cursor, knames = r.scan(0, match="sched-results-*")
    for name in knames:
        trim_results(name)

    while cursor != 0:
        cursor, knames = r.scan(cursor, match="sched-results-*")
        for name in knames:
            trim_results(name)

def count():
    cursor, knames = r.scan(0, match="sched-results-*")
    for name in knames:
        count_results(name)

    while cursor != 0:
        cursor, knames = r.scan(cursor, match="sched-results-*")
        for name in knames:
            count_results(name)

def show():
    cursor, knames = r.scan(0, match="sched-results-*")
    for name in knames:
        show_results(name)

    while cursor != 0:
        cursor, knames = r.scan(cursor, match="sched-results-*")
        for name in knames:
            show_results(name)

def expire():
    cursor, knames = r.scan(0, match="sched-results-*")
    for name in knames:
        expire_key(name)

    while cursor != 0:
        cursor, knames = r.scan(cursor, match="sched-results-*")
        for name in knames:
            expire_key(name)


if __name__ == '__main__':

    args = sys.argv[1:]

    while args:
        arg = args.pop(0)

        if arg == '--trim':
            trim()
        elif arg == '--count':
            count()
        elif arg == '--show':
            show()
        elif arg == '--expire':
            expire()
        else:
            print "unknown arg", arg
