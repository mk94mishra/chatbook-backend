import redis
r = redis.Redis(host='localhost', port=8081, db=0)
r.set('foo', 'bar')
print(r.get('foo'))
