import redis
redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
redis_conn.set('foo', 'bar')
mv=redis_conn.get('foo')
print(mv)