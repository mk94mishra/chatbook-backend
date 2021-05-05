import redis
r = redis.Redis(host='localhost', port=8081, db=0)
r.set('foo', 'bar')
r.get('foo')