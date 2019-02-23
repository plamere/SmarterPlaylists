
import json
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)


print json.dumps(r.info(), indent=2)
print "dbsize", r.dbsize()
