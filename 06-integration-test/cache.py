import redis

client = redis.Redis(host='cache', port=6379, db=0)

def ping():
    return client.ping()

def set(key, value):
    return client.set(key, value)

def delete(key):
    return client.delete(key)

def get(key):
    return client.get(key)

def setex(key, value, time):
    return client.setex(key, time, value)

def setnx(key, value):
    return client.setnx(key, value)

